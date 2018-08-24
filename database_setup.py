#!/usr/bin/env python3

"""
This is the database setup for the Workout Programming App.

It connects to the exercisecatalog PostgreSQL database. This is a shared
database with the Exercise Catalog app.
"""

import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String, Text, Sequence
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine


Base = declarative_base()


class Users(Base):
    """Users table in the exercisecatalog database.

    Keep track of the users that logged in for local permissions purposes.
    """

    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))


class PrimaryCategories(Base):
    """PrimaryCategories table in the exercisecatalog database.

    Store the first set of categories that are displayed on the homepage.
    """

    __tablename__ = 'primary_categories'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    description = Column(Text)
    picture = Column(String(250))

    @property
    def serialize(self):
        """Return object data in serializable format for JSON endpoints."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'picture': self.picture,
        }


class SecondaryCategories(Base):
    """SecondaryCategories table in the exercisecatalog database.

    Store the second set of categories that are dependent upon the
    primary categories.
    """

    __tablename__ = 'secondary_categories'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    description = Column(Text)
    primary_category = Column(Integer, ForeignKey('primary_categories.id'))

    @property
    def serialize(self):
        """Return object data in serializable format for JSON endpoints."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'primary_category': self.primary_category,
        }


class Exercises(Base):
    """Exercises table in the exercisecatalog database.

    Store all exercises with descriptions and all information.
    """

    __tablename__ = 'exercises'

    id = Column(Integer, Sequence('exercises_id'), primary_key=True)
    name = Column(String(250), nullable=False)
    description = Column(Text)
    video_url = Column(Text)
    secondary_category = Column(Integer, ForeignKey('secondary_categories.id'))
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship(Users)
    equipment_id = Column(Integer, ForeignKey('equipment.id'))

    @property
    def serialize(self):
        """Return object data in serializable format for JSON endpoints."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'video_url': self.video_url,
        }


class Equipment(Base):
    """Equipment table in the exercisecatalog database.

    Stores all exercise equipment with an image.
    """

     __tablename__ = 'equipment'

     id = Column(Integer, Sequence('equipment_id'), primary_key=True)
     name = Column(String(250), nullable=False)
     image = Column(String(250))

     @property
     def serialize(self):
         """Return object data in serializable format for JSON endpoints."""
         return {
            'id': self.id
            'name': self.name
            'image': self.image
         }


class Templates(Base):
    """Templates table in the exercisecatalog database.

    Stores all exercise templates with name, template type, and user id
    associated to the template.
    """

    __tablename__ = 'templates'

    id = Column(Integer, Sequence('template_id'), primary_key=True)
    name = Column(String(250), nullable=False)
    template_type = Column(String(250), ForeignKey('template_type.id'))
    user_id = Column(Integer, ForeignKey('users.id'))

     @property
     def serialize(self):
         """Return object data in serializable format for JSON endpoints."""
         return {
            'id': self.id
            'name': self.name
            'template_type': self.template_type
         }


class TemplateType(Base):
    """Template Types table in the exercisecatalog database.

    Stores all templates types within a template.
    Contains name and description of template type.
    """

    __tablename__ = 'template_type'

    id = Column(Integer, Sequence('template_type_id'), primary_key=True)
    name = Column(String(250), nullable=False)
    description = Column(Text)

    @property
    def serialize(self):
        """Return object data in serializable format for JSON endpoints."""
        return {
            'id': self.id
            'name': self.name
            'description': self.description
        }



class TemplateItems(Base):
    """Template Items table in the exercisecatalog database.

    Stores all templates items (secondary categories) within a template.
    Contains name of item, url link to the category in the database UI.
    """

    __tablename__ = 'template_items'

    id = Column(Integer, Sequence('template_items_id'), primary_key=True)
    name = Column(String(250), nullable=False)
    link = Column(String(250), nullable=False)
    template_id = Column(Integer, ForeignKey('templates.id'))

    @property
    def serialize(self):
        """Return object data in serializable format for JSON endpoints."""
        return {
           'id': self.id
           'name': self.name
           'link': self.link
        }


if __name__ == '__main__':
    engine = create_engine('postgresql:///exercisecatalog')
    Base.metadata.create_all(engine)
