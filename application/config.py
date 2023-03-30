from os import environ
from dotenv import load_dotenv, find_dotenv


class DevConfig:
    # Look for the .env and load it
    load_dotenv(find_dotenv())
    TESTING = True
    DEBUG = True
    ENV = 'development'
    TEMPLATE_DIR = '/templates'
    ARTICLES_DIR = '/articles'
    LABS_DIR = '/labs'
