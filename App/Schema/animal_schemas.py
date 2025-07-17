from App.extensions import ma
from App.models.Animals import Animal, AnimalImage

class AnimalSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Animal
        include_fk = True
    id = ma.auto_field()
    name = ma.auto_field()
    type = ma.auto_field()
    breed = ma.auto_field()
    age = ma.auto_field()
    price = ma.auto_field()
    description = ma.auto_field()
    is_available = ma.auto_field()
    farmer_id = ma.auto_field()
    images = ma.Nested('AnimalimagesSchema', many=True)

class AnimalimagesSchema(ma.SQLAlchemySchema):
    class Meta:
        model = AnimalImage
        include_fk = True
    id = ma.auto_field()
    url = ma.auto_field()
    animal_id = ma.auto_field()