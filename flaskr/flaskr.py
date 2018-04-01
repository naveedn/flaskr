# all the imports
import os
import sqlite3

from flask import (Flask, abort, flash, g, redirect, render_template, request,
                   session, url_for)

app = Flask(__name__)
app.config.from_object(__name__) ## Load config from this file, flaskr.py

app.config.update(dict(
  DATABASE=os.path.join(app.root_path, 'flaskr.db'),
  SECRET_KEY='development key',
  USERNAME='admin',
  PASSWORD='default'
))

app.config.from_envvar('FLASKR_SETTINGS', silent=True)


def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

def init_db():
  db = get_db()
  with app.open_resource('schema.sql', mode='r') as f:
    db.cursor().executescript(f.read())
  db.commit()

@app.cli.command('initdb')
def initdb_command():
  """Initializes the database"""
  init_db()
  print('Initiailized the database')

def get_db():
  """singleton pattern for handling db connections"""
  if not hasattr(g, 'sqlite_db'):
    g.sqlite_db = connect_db()
  return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
  """Closes the db at the end of a request"""
  if hasattr(g, 'sqlite_db'):
    g.sqlite_db.close()

