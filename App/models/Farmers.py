from flask import Flask
from App.extensions import db


class Farmers(db.Model):
    __tablename__ = 'farmers'

    id = db.Column(db.String, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    phone = db.Column(db.Integer, nullable=True)
    username = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    profile_picture = db.Column(db.String(255))

