
#!/usr/bin/env python3

from flask import Flask, make_response, jsonify, request, session
from flask_migrate import Migrate
from flask_restful import Api, Resource

from models import db, Article, User, ArticlesSchema, UserSchema

app = Flask(__name__)

app.secret_key = b'Y\xf1Xz\x00\xad|eQ\x80t \xca\x1a\x10K'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


# CLEAR SESSION
class ClearSession(Resource):

    def get(self):
        session.pop('page_views', None)
        session.pop('user_id', None)
        return {}, 204

    def delete(self):
        session.pop('page_views', None)
        session.pop('user_id', None)
        return {}, 204


# GET ALL ARTICLES
class IndexArticle(Resource):

    def get(self):
        articles = [
            ArticlesSchema().dump(article)
            for article in Article.query.all()
        ]

        return articles, 200


# GET ONE ARTICLE
class ShowArticle(Resource):

    def get(self, id):

        session['page_views'] = (
            0 if not session.get('page_views')
            else session.get('page_views')
        )

        session['page_views'] += 1

        if session['page_views'] <= 3:

            article = Article.query.filter(
                Article.id == id
            ).first()

            article_json = ArticlesSchema().dump(article)

            return make_response(article_json, 200)

        return {'message': 'Maximum pageview limit reached'}, 401


# LOGIN
class Login(Resource):

    def post(self):

        # Get username from request JSON
        username = request.get_json()['username']

        # Find user in database
        user = User.query.filter_by(
            username=username
        ).first()

        # Handle user not found
        if user is None:
            return {'message': 'User not found'}, 404

        # Store user ID in session
        session['user_id'] = user.id

        # Return user as JSON
        return UserSchema().dump(user), 200


# LOGOUT
class Logout(Resource):

    def delete(self):

        # Remove user ID from session
        session.pop('user_id', None)

        # Return no content
        return {}, 204


# CHECK SESSION
class CheckSession(Resource):

    def get(self):

        # Get user ID from session
        user_id = session.get('user_id')

        # If no user is logged in
        if not user_id:
            return {}, 401

        # Find user using their ID
        user = User.query.filter_by(
            id=user_id
        ).first()

        # If user no longer exists
        if user is None:
            session.pop('user_id', None)
            return {}, 401

        # Return logged-in user
        return UserSchema().dump(user), 200


# REGISTER ROUTES
api.add_resource(ClearSession, '/clear')

api.add_resource(IndexArticle, '/articles')

api.add_resource(ShowArticle, '/articles/<int:id>')

api.add_resource(Login, '/login')

api.add_resource(Logout, '/logout')

api.add_resource(CheckSession, '/check_session')


if __name__ == '__main__':
    app.run(port=5555, debug=True)
