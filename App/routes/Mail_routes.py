from flask import Blueprint,jsonify,request
from flask_mail import Message
from App.extensions import mail


Mail_bp = Blueprint('Mail_bp', __name__)

@Mail_bp.route('/Order-User/<string:userid>', methods=['POST'])
def Send_order_confirmation_user(userid):
    data = request.get_json()
    id = data['id']
    created_at = data['created_at']
    amount = data['amount']

    try:
        msg = Message(
            'FARMART',
            sender='arvinkipo@gmail.com',
            recipients=['gideonkipkoech854@gmail.com']
        )

        msg.body = (
            f"This is to confirm your order {id} which totalled {amount}. "
            f"The order was made at {created_at} and has been sent to the farmer for confirmation. "
            f"You will receive an email for confirmation in order to continue with Payment and delivery. "
            f"HAPPY SHOPPING!"
        )

        mail.send(msg)
        return jsonify({'message': 'Email sent successfully'}), 200

    except Exception as e:
        return jsonify([{'error': str(e)}]), 500


@Mail_bp.route("/test-email")
def test_email():
    from flask_mail import Message
    msg = Message("Test Email",
                  sender="arvinkipko@gmail.com",
                  recipients=["gideonkipkoech854@gmail.com"])
    msg.body = "If you get this, it works!"
    try:
        mail.send(msg)
        return "✅ Email sent"
    except Exception as e:
        print("❌ Send failed:", e)
        return f"❌ Failed: {e}"