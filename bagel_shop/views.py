from models import Base, User, Bagel
from flask import Flask, jsonify, request, url_for, abort, g
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine
from flask_httpauth import HTTPBasicAuth

auth = HTTPBasicAuth()

engine = create_engine('sqlite:///bagelShop.db')

Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()
app = Flask(__name__)


# ADD @auth.verify_password here
@auth.verify_password
def verify_password(username_or_token, password):
    # Check if it's a token
    user_id = User.verify_auth_token((username_or_token))
    if user_id:
        user = session.query(User).filter_by(username=username_or_token).first()
    else:
        user = None

    if not user:
        print("User not found")
        return False

    if not user.verify_password(password):
        print ("Unable to verify password")
        return False
    g.user = user
    return True

@app.route('/token')
@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token()
    return jsonify({'token': token.decode('ascii')})

# ADD a /users route here
@app.route('/users', methods=['POST'])
def new_user():
    username = request.json.get('username')
    password = request.json.get('password')
    if username is None or password is None:
        abort(400)  # missing arguments

    user = session.query(User).filter_by(username=username).first()
    if user is not None:
        print("User already exists")
        return jsonify("message: User already exists"),200  # User already exists

    user = User()
    user.username = username
    user.hash_password(password)
    session.add(user)
    session.commit()
    return jsonify({'username': user.username}), 201


@app.route('/bagels', methods=['GET', 'POST'])
@auth.login_required
def showAllBagels():
    if request.method == 'GET':
        bagels = session.query(Bagel).all()
        return jsonify(bagels=[bagel.serialize for bagel in bagels])
    elif request.method=="POST":
        name = request.json.get('name')
        description = request.json.get('description')
        picture = request.json.get('picture')
        price = request.json.get('price')
        newBagel = Bagel(name=name, description=description, picture=picture, price=price)
        session.add(newBagel)
        session.commit()
        return jsonify(newBagel.serialize)

    # data = dict(username="TinnyTim", password="Udacity", name="plain",
    #             picture="http://bonacbagel.weebly.com/uploads/4/0/5/4/40548977/s318635836612132814_p1_i1_w240.jpeg",
    #             description="Old-Fashioned Plain Bagel", price="$1.99")


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
