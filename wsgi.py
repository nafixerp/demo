# wsgi.py
# This file serves as an entry point for Gunicorn

from app import app

if __name__ == "__main__":
    app.run()
