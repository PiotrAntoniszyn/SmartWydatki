from flask import Flask, g, render_template
from src.db.supabase_client import supabase
from config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    @app.before_request
    def attach_supabase():
        # dodaj obiekt supabase do globalnego obiektu g
        g.supabase = supabase

    @app.route("/")
    def index():
        # przykładowe zapytanie
        data = g.supabase.table("profiles").select("*").execute()
        return render_template("index.html", profiles=data.data)

    return app

if __name__ == "__main__":
    create_app().run(debug=True)