# app/models.py
from . import db
from flask_login import UserMixin

# Association tables for many-to-many relationships
characters_general_tags = db.Table('characters_general_tags',
    db.Column('character_id', db.Integer, db.ForeignKey('character.id'), primary_key=True),
    db.Column('general_tag_id', db.Integer, db.ForeignKey('general_tag.id'), primary_key=True)
)

characters_species_tags = db.Table('characters_species_tags',
    db.Column('character_id', db.Integer, db.ForeignKey('character.id'), primary_key=True),
    db.Column('species_tag_id', db.Integer, db.ForeignKey('species_tag.id'), primary_key=True)
)

class Character(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.String(50))
    from_where = db.Column(db.String(150))
    gender = db.Column(db.String(20), nullable=False)
    image_file = db.Column(db.String(100), nullable=False, default='default.jpg')
    smash_count = db.Column(db.Integer, default=0)
    pass_count = db.Column(db.Integer, default=0)
    
    general_tags = db.relationship('GeneralTag', secondary=characters_general_tags, lazy='subquery',
        backref=db.backref('characters', lazy=True))
    
    species_tags = db.relationship('SpeciesTag', secondary=characters_species_tags, lazy='subquery',
        backref=db.backref('characters', lazy=True))

class GeneralTag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

class SpeciesTag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
