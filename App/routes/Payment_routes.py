
from flask import Blueprint, request, jsonify
from App.extensions import db
from App.models.Payments import Payment, Item 
import uuid
import stripe
import os
from dotenv import load_dotenv

load_dotenv()

payment_bp = Blueprint('payment_bp', __name__)
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
endpoint_secret = os.getenv("STRIPE_WEBHOOK_SECRET")  

@payment_bp.route('/create-checkout-session', methods=['POST', 'OPTIONS'])
def create_checkout_session():
    if request.method == 'OPTIONS':
        return '', 200

    try:
        data = request.get_json()

        # Debugging logs (remove in production)
        print("Received payload:", data)

        items = data.get('items')
        if not isinstance(items, list):
            return jsonify({'error': 'Invalid items format — expected a list of item objects'}), 400

        shipping_cost = data.get('shipping_cost', 0)
        pickup_location = data.get('pickup_location', '')
        shipping_method = data.get('shipping_method', '')

        line_items = []
        for item in items:
            # Defensive check
            if not all(k in item for k in ('name', 'price')):
                return jsonify({'error': 'Each item must include name and price'}), 400

            line_items.append({
                'price_data': {
                    'currency': 'kes',
                    'product_data': {
                        'name': item['name'],
                    },
                    'unit_amount': int(float(item['price']) * 100),  # Convert to cents
                },
                'quantity': item.get('quantity', 1),
            })

        metadata = {
            'shipping_cost': str(shipping_cost),
            'pickup_location': pickup_location,
            'shipping_method': shipping_method,
            'item_ids': ','.join([str(item.get('id', '')) for item in items])
        }

        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items,
            mode='payment',
            metadata=metadata,
            success_url='http://localhost:3000/success',
            cancel_url='http://localhost:3000/cancel',
        )

        return jsonify({'url': session.url})

    except Exception as e:
        print("Stripe error:", e)
        return jsonify({'error': str(e)}), 400


@payment_bp.route('/webhook', methods=['POST'])
def stripe_webhook():
    payload = request.data
    sig_header = request.headers.get('stripe-signature')

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except stripe.error.SignatureVerificationError:
        return jsonify({'error': 'Invalid signature'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 400

    # Handle completed checkout
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        metadata = session.get('metadata', {})

        try:
            # Extract payment metadata
            amount_total = session['amount_total'] / 100  # convert back from cents
            shipping_cost = float(metadata.get('shipping_cost', 0))
            pickup_location = metadata.get('pickup_location')
            shipping_method = metadata.get('shipping_method')
            item_ids = metadata.get('item_ids', '').split(',')

            payment = Payment(
                amount=amount_total - shipping_cost,
                shipping_cost=shipping_cost,
                total=amount_total,
                pickup_location=pickup_location,
                shipping_method=shipping_method
            )
            db.session.add(payment)
            db.session.flush()

            for item_id in item_ids:
                if item_id:  # skip empty
                    item = Item(
                        id=str(uuid.uuid4()),
                        payment_id=payment.id,
                        item_id=item_id
                    )
                    db.session.add(item)

            db.session.commit()
            print(f"✅ Payment stored for session {session['id']}")
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error saving payment: {e}")

    return '', 200
