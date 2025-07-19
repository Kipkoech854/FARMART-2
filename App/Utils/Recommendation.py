from App.models.Likes import Like
from App.models.A import Animal
from sqlalchemy import func


def recommend_animals_for_user(user_id, limit=5):

    liked_animal_ids = db.session.query(Like.animal_id).filter_by(user_id=user_id).subquery()

   
    similar_users = db.session.query(Like.user_id)\
        .filter(Like.animal_id.in_(liked_animal_ids))\
        .filter(Like.user_id != user_id)\
        .distinct().subquery()

    
    recommended_animals = db.session.query(
        Animal, func.count(Like.id).label('score')
    ).join(Like, Animal.id == Like.animal_id)\
     .filter(Like.user_id.in_(similar_users))\
     .filter(~Like.animal_id.in_(liked_animal_ids))\
     .group_by(Animal.id)\
     .order_by(func.count(Like.id).desc())\
     .limit(limit).all()

    return [animal for animal, _ in recommended_animals]
