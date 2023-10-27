'''from flask_mongoengine import MongoEngine

'from flask_mongoengine import MongoEngine'

db = MongoEngine()

class User(db.Document):
    username = db.StringField(unique=True, required=True)
    password = db.StringField(required=True)
    email = db.StringField(required=True)
    firstname = db.StringField(required=True)
    lastname = db.StringField(required=True)
    contact_no = db.IntField(required=True)

    def to_json(self):
        return {
            "username": self.username,
            "password": self.password,
            "email": self.email,
            "firstname": self.firstname,
            "lastname": self.lastname,
            "contact_no": self.contact_no
        }'''
