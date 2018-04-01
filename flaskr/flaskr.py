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


@app.route('/')
def show_entries():
  db = get_db()
  cur = db.execute('select title, text from entries order by id desc')
  entries = cur.fetchall()
  return render_template('show_entries.html', entries=entries)

@app.route('/add', methods=['POST'])
def add_entry():
  if not session.get('logged_in'):
    abort(401)
  db = get_db()
  db.execute('insert into entries (title, text) values (?, ?)', [request.form['title'], request.form['text']])
  db.commit()
  flash('New Entry was successfully posted')
  return redirect(url_for('show_entries'))

@app.route('/login', methods=['GET', 'POST'])
def login():
  error = None
  if request.method == 'POST':
    if request.form['username'] != app.config['USERNAME']:
      error = 'username does not match'
    elif request.form['password'] != app.config['PASSWORD']:
      error = 'password is incorrect'
    else:
      session['logged_in'] = True
      flash('You were logged in!')
      return redirect(url_for('show_entries'))
  return render_template('login.html', error=error)

@app.route('/logout')
def logout():
  session.pop('logged_in', None)
  flash('you were logged out')
  return redirect(url_for('show_entries'))
