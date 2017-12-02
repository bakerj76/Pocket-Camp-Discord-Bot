"""Initializes the Animal Camp sqlite database."""
import sqlite3

conn = sqlite3.connect('ac.db')
c = conn.cursor()

with open('schema.sql', 'r') as f:
    c.execute(f.read())

conn.commit()
conn.close()
