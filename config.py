import os

class Config:
    SECRET_KEY = 'supersecretkey'
    # Database configuration
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:9257postgres@localhost/users'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = True