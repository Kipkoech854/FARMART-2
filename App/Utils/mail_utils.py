from App.models.Animals import Animal,AnimalImage
from App.models.Farmers import Farmer
from App.models.Users import User
from App.extensions import mail
from flask_mail import Message

def get_farmer_contact(farmer_id):
    farmer = Farmer.query.get(farmer_id)
    if not farmer:
        return None
    return {"email": farmer.email, "username": farmer.username ,"profile_picture":farmer.profile_picture}

def get_user_contact(user_id):
    user = User.query.get(user_id)
    if not user:
        return None
    return {"email": user.email, "username": user.username, "profile_picture": farmer.profile_picture}

def group_items_by_farmer_util(items):
    if not isinstance(items, list):
        raise ValueError("'items' must be a list")

    farmer_items = {}

    for item in items:
        animal_id = item.get("animal_id")
        if not animal_id:
            continue

        animal = Animal.query.get(animal_id)
        if not animal:
            continue

        farmer_id = animal.farmer_id
        if farmer_id not in farmer_items:
            farmer_items[farmer_id] = []

        enriched_item = {
            "animal_id": animal.id,
            "name": animal.name,
            "type": animal.type,
            "breed": animal.breed,
            "age": animal.age,
            "price": animal.price,
            "description": animal.description,
            "is_available": animal.is_available,
            "image_count": len(animal.images),
            "quantity": item.get("quantity"),
            "price_at_order_time": item.get("price_at_order_time")
        }

        farmer_items[farmer_id].append(enriched_item)

    response_payload = []

    for farmer_id, items_list in farmer_items.items():
        contact = get_farmer_contact(farmer_id)
        if not contact:
            print(f"Farmer not found: {farmer_id}")
            continue

        response_payload.append({
            "id": farmer_id,
            "email": contact.get("email"),
            "username": contact.get("username"),
            "items": items_list
        })

    return response_payload


def validate_request_data(data):
    if not data:
        return None, jsonify({'error': 'Invalid or no data to send to farmers'}), 400

    items = data.get('items')
    if not items:
        return None, jsonify({'error': 'No items found in the request data'}), 400

    return items, None, None


def compose_order_lines(items):
    order_lines = ""
    for item in items:
        order_lines += f"""
----------------------------
Animal Name: {item.get('name')}
Type: {item.get('type')}
Breed: {item.get('breed')}
Age: {item.get('age')}
Available: {"Yes" if item.get('is_available') else "No"}
Price at Order Time: KES {item.get('price_at_order_time')}
Quantity Ordered: {item.get('quantity')}
Description: {item.get('description')}
Number of Images Listed: {item.get('image_count')}
"""
    return order_lines

def send_email(msg, recipient_email):
    try:
        mail.send(msg)
        print(f"Email sent successfully to {recipient_email}")
        return True, None
    except Exception as e:
        error_msg = str(e)
        print(f"Error sending email to {recipient_email}: {error_msg}")
        return False, error_msg



def group_items_by_farmer_util_for_user(items):
    if not isinstance(items, list):
        raise ValueError("'items' must be a list")

    farmer_items = {}

    # Step 1: Collect animal_ids from items
    animal_ids = [item.get("animal_id") for item in items if item.get("animal_id")]

    # Step 2: Query all animals at once (to reduce DB hits)
    animals = Animal.query.filter(Animal.id.in_(animal_ids)).all()
    animal_map = {animal.id: animal for animal in animals}

    for item in items:
        animal_id = item.get("animal_id")
        if not animal_id or animal_id not in animal_map:
            continue

        animal = animal_map[animal_id]
        farmer_id = animal.farmer_id
        if farmer_id not in farmer_items:
            farmer_items[farmer_id] = []

        enriched_item = {
            "animal_id": animal.id,
            "name": animal.name,
            "type": animal.type,
            "breed": animal.breed,
            "age": animal.age,
            "price": animal.price,
            "description": animal.description,
            "is_available": animal.is_available,
            "images": [img.url for img in animal.images],
            "image_count": len(animal.images),
            "quantity": item.get("quantity"),
            "price_at_order_time": item.get("price_at_order_time")
        }

        farmer_items[farmer_id].append(enriched_item)

    # Step 3: Build final payload with farmer contact
    response_payload = []

    for farmer_id, items_list in farmer_items.items():
        contact = get_farmer_contact(farmer_id)
        if not contact:
            print(f"Farmer not found: {farmer_id}")
            continue

        response_payload.append({
            "id": farmer_id,
            "email": contact.get("email"),
            "username": contact.get("username"),
            "items": items_list
        })

    return response_payload



def group_items_by_farmer_util_for_farmer(user_id, items):
    if not isinstance(items, list):
        raise ValueError("'items' must be a list")

    current_user_id = user_id  
    farmer_items = {}

    for item in items:
        animal_id = item.get("animal_id")
        if not animal_id:
            continue

        animal = Animal.query.get(animal_id)
        if not animal:
            continue

        # Only include items from animals owned by the current farmer
        if animal.farmer_id != current_user_id:
            continue

        if animal.farmer_id not in farmer_items:
            farmer_items[animal.farmer_id] = []

        enriched_item = {
            "animal_id": animal.id,
            "name": animal.name,
            "type": animal.type,
            "breed": animal.breed,
            "age": animal.age,
            "price": animal.price,
            "description": animal.description,
            "is_available": animal.is_available,
            "image_count": len(animal.images),
            "quantity": item.get("quantity"),
            "price_at_order_time": item.get("price_at_order_time")
        }

        farmer_items[animal.farmer_id].append(enriched_item)

    response_payload = []

    for farmer_id, items_list in farmer_items.items():
        contact = get_farmer_contact(farmer_id)
        if not contact:
            continue

        response_payload.append({
            "id": farmer_id,
            "email": contact.get("email"),
            "username": contact.get("username"),
            "items": items_list
        })

    return response_payload



def get_orders_relevant_to_farmer(farmer_id):
    # Step 1: Join OrderItem → Animal, filter by farmer_id
    relevant_order_items = (
        db.session.query(OrderItem)
        .join(Animal, OrderItem.animal_id == Animal.id)
        .filter(Animal.farmer_id == farmer_id)
        .all()
    )

    # Step 2: Extract unique Order IDs
    order_ids = {item.order_id for item in relevant_order_items}

    # Step 3: Query all orders with those IDs
    orders = Order.query.filter(Order.id.in_(order_ids)).order_by(Order.created_at.desc()).all()

    return orders
