from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///recipes.db'
db = SQLAlchemy(app)

association_table = db.Table('association',
                             db.Column('recipe_id', db.Integer, db.ForeignKey('recipe.id')),
                             db.Column('ingredient_id', db.Integer, db.ForeignKey('ingredient.id'))
                             )


class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    ingredients = db.relationship('Ingredient', secondary=association_table,
                                  backref=db.backref('recipes', lazy='dynamic'))


class Ingredient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)


@app.route('/recipes', methods=['GET'])
def get_recipes():
    recipes = Recipe.query.all()
    return jsonify(
        [{'id': recipe.id, 'name': recipe.name, 'ingredients': [ingredient.name for ingredient in recipe.ingredients]}
         for recipe in recipes])


@app.route('/ingredients', methods=['GET'])
def get_ingredients():
    ingredients = Ingredient.query.all()
    return jsonify(
        [{'id': ingredient.id, 'name': ingredient.name, 'recipes': [recipe.name for recipe in ingredient.recipes]} for
         ingredient in ingredients])


@app.route('/recipes', methods=['POST'])
def add_recipe():
    data = request.json
    name = data.get('name')
    ingredients = data.get('ingredients', [])

    if name:
        recipe = Recipe(name=name)
        for ingredient_name in ingredients:
            ingredient = Ingredient.query.filter_by(name=ingredient_name).first()
            if ingredient is None:
                ingredient = Ingredient(name=ingredient_name)
            recipe.ingredients.append(ingredient)

        db.session.add(recipe)
        db.session.commit()

        return jsonify({'message': 'Recipe added successfully'})
    else:
        return jsonify({'error': 'Missing recipe name'}), 400


if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)
