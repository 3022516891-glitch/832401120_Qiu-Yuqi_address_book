import sqlite3
from pathlib import Path

from flask import current_app, g


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def insert_contact(db, name, favorite, methods):
    cursor = db.execute(
        "INSERT INTO contact (name, favorite) VALUES (?, ?)", (name, favorite)
    )
    db.executemany(
        "INSERT INTO contact_method (contact_id, kind, value) VALUES (?, ?, ?)",
        [(cursor.lastrowid, kind, value) for kind, value in methods if value],
    )


def close_db(error=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_app(app):
    app.teardown_appcontext(close_db)
    Path(app.config["DATABASE"]).parent.mkdir(parents=True, exist_ok=True)
    with app.app_context():
        get_db().executescript(Path(__file__).with_name("schema.sql").read_text(encoding="utf-8"))
