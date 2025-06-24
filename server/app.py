from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from flask_migrate import Migrate
from datetime import datetime, timezone

from models import db, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)

db.init_app(app)

@app.route('/messages', methods=['GET'])
def get_messages():
    messages = Message.query.order_by(Message.created_at.asc()).all()
    messages_data = [message.to_dict() for message in messages]  
    
    response = make_response(jsonify(messages_data), 200)
    return response


@app.route('/messages', methods=['POST'])
def create_message():
    data = request.get_json() if request.is_json else request.form

    body = data.get('body')
    username = data.get('username')

    if not body or not username:
        return jsonify({"error": "Both 'body' and 'username' are required."}), 400

    new_message = Message(
        body=body,
        username=username,
    )
    
    db.session.add(new_message)
    db.session.commit()

    response = make_response(
        jsonify(new_message.to_dict()),
        201
    )
    return response

@app.route('/messages/<int:id>', methods=['PATCH'])
def update_message(id):
    message = Message.query.get_or_404(id) 

    data = request.get_json()  
    if not data or 'body' not in data:
        return jsonify({"error": "Missing 'body' in request data."}), 400

    message.body = data['body']
    message.updated_at = datetime.now(timezone.utc)  

    try:
        db.session.commit()
        return jsonify(message.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
if __name__ == '__main__':
    app.run(port=5555)

@app.route('/messages/<int:id>', methods=['DELETE'])
def delete_message(id):
    message = Message.query.get_or_404(id)  

    try:
        db.session.delete(message)
        db.session.commit()
        return jsonify({"message": "Message deleted successfully."}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
