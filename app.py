from flask import Flask, request, jsonify, render_template, url_for, redirect, session
from flask_bcrypt import Bcrypt
from pymongo import MongoClient
from bson import ObjectId
import jwt
import os

app = Flask(__name__)
app.secret_key = 'jopher123456'

client = MongoClient("mongodb+srv://josiriboup:YeFfiKAjkGHJyKar@cluster0.71gaxnl.mongodb.net/?retryWrites=true&w=majority")
db = client['PYTHON']
bcrypt = Bcrypt(app)



@app.route('/')
def home():
    return render_template('home.html')

@app.route('/main')
def main():
    user_firstname = session.get('user_firstname', '')  # Get the user's first name from the session
    records = list(db.records.find({}))
    return render_template('main.html', user_firstname=user_firstname, records=records)

@app.route('/logout')
def logout():
    # Clear the user's session, effectively logging them out
    session.clear()
    return redirect(url_for('home'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        # Handle GET request (display the registration form)
        return render_template('signup.html')
    elif request.method == 'POST':
        try:
            # Retrieve form data using request.form
            username = request.form.get('username')
            email = request.form.get('email')
            password = request.form.get('password')
            firstname = request.form.get('firstname')
            lastname = request.form.get('lastname')
            contact_no = request.form.get('contact_no')

            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

            user = {
                'username': username,
                'password': hashed_password,
                'email': email,
                'firstname': firstname,
                'lastname': lastname,
                'contact_no': contact_no
            }

            user_id = db.users.insert_one(user).inserted_id
            user['_id'] = str(user_id)

            # After successful registration, redirect to the login page
            return redirect(url_for('login'))

        except Exception as e:
            return jsonify({'error': str(e)}), 400

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        try:
            email = request.form.get('email')
            password = request.form.get('password')

            user = db.users.find_one({'email': email})
            if user:
                if bcrypt.check_password_hash(user['password'], password):
                    SECRET = os.environ.get('JWT_SECRET') or 'jopher123456'

                    payload = {
                        'firstname': user['firstname'],
                        'lastname': user['lastname'],
                        'email': user['email'],
                        'id': str(user['_id']),
                        'contact_no': user['contact_no'],
                    }

                    token = jwt.encode(payload, SECRET, algorithm='HS256')
                    user_profile = {
                        'firstname': user['firstname'],
                        'lastname': user['lastname'],
                        'email': user['email'],
                        'id': str(user['_id']),
                        'contact_no': user['contact_no'],
                    }

                    # Store the user's first name in the session
                    session['user_firstname'] = user_profile['firstname']

                    # Redirect to the main page
                    return redirect(url_for('main'))

                else:
                    return jsonify({'error': "Password doesn't match"}, 400)
            else:
                return jsonify({'error': "Email doesn't match"}, 400)

        except Exception as e:
            return jsonify({'error': str(e)}, 400)

@app.route('/records', methods=['POST', 'GET'])
def records():
    if request.method == 'GET':
        return render_template('main.html')
    if request.method == 'POST':
        try:

            name = request.form.get('name')
            email = request.form.get('email')
            lastname = request.form.get('lastname')

            if not name or not lastname or not email:
                return jsonify({'error': 'Incomplete data. Name, lastname, and email are required fields.'}), 400

            record = {
                'name': name,
                'lastname': lastname,
                'email': email
            }

            record_id = db.records.insert_one(record).inserted_id
            record['_id'] = str(record_id)



            # Return a response to indicate success
            return redirect(url_for('main'))

        except Exception as e:
            return jsonify({'error': str(e)}), 400

@app.route('/update_record', methods=['POST'])
def update_record():
    record_id = request.form.get('update_id')
    name = request.form.get('update_name')
    lastname = request.form.get('update_lastname')
    email = request.form.get('update_email')

    if not name or not lastname or not email:
        return jsonify({'error': 'Incomplete data. Name, lastname, and email are required fields.'}), 400

    # Update the record in the database based on the record_id
    db.records.update_one({'_id': ObjectId(record_id)}, {'$set': {'name': name, 'lastname': lastname, 'email': email}})

    return redirect(url_for('main'))

@app.route('/delete_record', methods=['POST'])
def delete_record():
    record_id = request.form.get('delete_id')

    if not record_id:
        return jsonify({'error': 'Invalid request'}), 400

    # Delete the record from the database based on the record_id
    db.records.delete_one({'_id': ObjectId(record_id)})

    return redirect(url_for('main'))

if __name__ == '__main__':
    app.run(debug=True)
