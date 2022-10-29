import uuid

from flask import Flask, request
from flask_restx import Resource, Api, marshal_with, fields
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from functools import wraps


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'jab30/3yX R~XHH!jmN]LWX/,?RT'

db = SQLAlchemy(app)

migrate = Migrate(app, db)




authorizations = {
    'apikey' : {
        'type' : 'apiKey',
        'in' : 'header',
        'name' : 'X-API-KEY'
    }
}

api = Api(app, title='Items API', authorizations=authorizations,  description='API about Items')



taskFields = {
    'id' : fields.Integer,
    'name' : fields.String
}



def token_required(f):
    wraps(f)
    def decorated(*args, **kwargs):

        token = None

        if 'X-API-KEY' in request.headers:
            token = request.headers['X-API-KEY']

        if not token:
            return {'result' : 'Token is missing.'}, 401

        if token != 'mytoken':
            return {'result' : 'Token is not valid'}, 401

        print('TOKEN : ' + token)
        return f(*args, **kwargs)
    
    return decorated
    

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    
    def __repr__(self):
        return self.name


class Items(Resource):

    @marshal_with(taskFields)
    def get(self):
        tasks = Task.query.all()
        return tasks

    @marshal_with(taskFields)
    def post(self):
        data = request.json
        
        task = Task(name=data['name'])

        db.session.add(task)
        db.session.commit()

        return {'result' : 'Name Added'}, 201
  
    


class Item(Resource):

    @marshal_with(taskFields)
    def get(self, id):
        task = Task.query.filter_by(id=id).first()
        return task

    @marshal_with(taskFields)
    def put(self, id):
        data = request.json
        
        task = Task.query.filter_by(id=id).first()
        task.name = data['name']

        db.session.commit()

        return {'result' : 'Updated ' + data['name'] }

    def delete(self, id):
        task = Task.query.filter_by(id=id).first()

        db.session.delete(task)
        db.session.commit()

        return {'result' : 'Deleted id : #' + str(id)}



api.add_resource(Items, '/items/')
api.add_resource(Item, '/item/<int:id>')


if __name__ == '__main__':
    app.run(debug=True)