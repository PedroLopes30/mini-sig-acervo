#imports
from dotenv import load_dotenv
from os import getenv

#funcs
load_dotenv('./.env')

#DATABASE
DATABASE = getenv('DATABASE', './db.sqlite3')