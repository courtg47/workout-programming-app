#!/usr/bin/env python

"""
This is the database setup for the Exercise Catalog project.

It connects to the exercisecatalog PostgreSQL database.
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
    primary_category = Column(
        Integer, ForeignKey('primary_categories.id'))

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
    secondary_category = Column(
        Integer, ForeignKey('secondary_categories.id'))
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship(Users)

    @property
    def serialize(self):
        """Return object data in serializable format for JSON endpoints."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'video_url': self.video_url,
        }


if __name__ == '__main__':
    engine = create_engine('postgresql:///exercisecatalog')
    Base.metadata.create_all(engine)
