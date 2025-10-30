# run.py
from app import create_app, db
from app.models import User, GeneralTag, SpeciesTag
from werkzeug.security import generate_password_hash
import click

app = create_app()

@app.cli.command("init-db")
def init_db_command():
    """Clear the existing data and create new tables and default data."""
    db.drop_all()
    db.create_all()

    # Create Admin User
    admin_user = User(username="Ryan", password=generate_password_hash("06242005", method='pbkdf2:sha256'))
    db.session.add(admin_user)

    # Pre-populate General Tags
    general_tags = ["Game", "Anime", "Celebrity", "Animal", "Other", "Film", "Disney", "Pokemon"]
    for tag in general_tags:
        db.session.add(GeneralTag(name=tag))
    
    # Pre-populate Species Tags
    species_tags = ["Furry", "Human", "Humanoid", "Mammal", "Other"]
    for tag in species_tags:
        db.session.add(SpeciesTag(name=tag))

    db.session.commit()
    click.echo("Initialized the database with default tags and admin user.")

if __name__ == '__main__':
    app.run(debug=True)
