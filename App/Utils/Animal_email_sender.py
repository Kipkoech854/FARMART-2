from flask_mail import Message
from App.extensions import mail  
from App.Utils.mail_utils import get_farmer_contact

def send_animal_creation_confirmation(payload):
    try:
        id = payload['id']
        name = payload['name']
        breed = payload['breed']
        age = payload['age']
        price = payload['price']
        description = payload['description']
        images = payload.get('images', [])
        number = len(images)
        plural = 's' if number != 1 else ''
        farmer_id = payload['farmer_id']

        # Get farmer contact info
        farmer_data = get_farmer_contact(farmer_id)
        username = farmer_data['username']
        recipient = farmer_data['email']

        msg = Message(
            'FARMART',
            sender='farmart597@gmail.com',
            recipients=[recipient]
        )
        msg.body = f"""
Hello {username},

Your new product has been successfully created with the following details:

Product ID: {id}
Name: {name}
Breed: {breed}
Age: {age} years
Price: KES {price}
Description: {description}

You have uploaded {number} image{plural} for this product.

Thank you for using our platform!

Best regards,  
The FarmArt Team
        """

        mail.send(msg)
        print(">> Animal confirmation email sent to farmer.")
        return True

    except Exception as e:
        print(">> Email sending failed:", str(e))
        return False
