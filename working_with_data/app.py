import sqlite3
import json

from flask import Flask, request, jsonify, g

# start the flask app
wakadinali = Flask(__name__)

# DATABASE SETUP
DATABASE_NAME = "victim_of_madness"

def get_database():
    """
    Get the connection to a database
    """
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE_NAME)
        # helps in making the tuple more readable
        g.db.row_factory = sqlite3.Row 
    return g.db

@wakadinali.teardown_appcontext
def close_database(e):
    """
    Terminate the connection once the request is done
    """
    db = g.pop("db", None)
    if db is not None:
        db.close()

def start_db():
    """
    Create the tables (DDL)
    Seed the table with initial data(DML)
    commit the execution (TCL)
    """
    db = get_database()

    # DDL
    db.execute("""
    CREATE TABLE IF NOT EXISTS books (
               id        INTEGER PRIMARY KEY AUTOINCREMENT,
               title     TEXT    NOT NULL,
               author    TEXT    NOT NULL,
               genre     TEXT    NOT NULL,
               year_pub  INTEGER NOT NULL,
               available INTEGER NOT NULL DEFAULT 1
               )
    """)
    # DQL
    if db.execute("SELECT COUNT(*) FROM books").fetchone()[0] == 0:
        reading_material = [
            ("The alchemist", "paulo coehlo", "fictional", 1991, 1), 
            ("thinking, fast and slow", "Daniel Kahneman", "Non-fiction", 2011, 1)
        ]
        # DML
        for item in reading_material:
            db.execute("""
                       INSERT INTO books 
                            (title, author, genre, year_pub, available) 
                       VALUES 
                            (?,?,?,?,?)
            """, (*item,)
            )

    # TCL
    db.commit()

def row_to_dict(row):
    """
    Convertion of row to dictionary so that we can jsonify
    """
    return dict(row)

# HELPER FUNCTION(utility)
def api_response(data=None, message="", status_code=200):
    """
    return consistent response to the api
    """
    payload = {
        "ok": status_code < 400,
        "status": status_code,
        "message": message
    }

    if data is not None:
        payload["data"] = data
    return jsonify(payload), 200

def error_response(message, status_code=400):
    """Shortcut for error messages"""
    return api_response(message=message, status_code=status_code)


# ENDPOINTS

# run the app and start the db process
if __name__ == "__main__":
    with wakadinali.app_context():
        start_db()
    wakadinali.run()
