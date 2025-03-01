from flask import Flask, request
from flask_socketio import SocketIO
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
socketio = SocketIO(app, cors_allowed_origins="*")

clients = {}  # Dictionary to store connected clients

@app.route('/')
def index():
    return "Chess Game Server Running"

@socketio.on('connect')
def handle_connect():
    global clients
    session_id = request.sid  # Get unique session ID
    client_count = len(clients) + 1  # Use dynamic client count

    if client_count % 2 == 1:  # First client in a pair
        color = 'white' if random.randrange(0, 2) == 1 else 'black'
    else:  # Second client in a pair
        previous_client = f'client{client_count - 1}'
        previous_color = clients[previous_client]['color']
        color = 'white' if previous_color == 'black' else 'black'

    clients[f'client{client_count}'] = {'sid': session_id, 'color': color}
    
    print(f"Client {client_count} connected! Assigned sid: {session_id}")
    socketio.emit('initial_color', {'message': color}, to=session_id)
    print(clients)

@socketio.on('disconnect')
def handle_disconnect():
    session_id = request.sid
    client_key = next((key for key, value in clients.items() if value['sid'] == session_id), None)
    
    if client_key:
        del clients[client_key]  # Remove client from the dictionary
        print(f"Client {client_key} disconnected. Session ID: {session_id}")

@socketio.on('client_message')
def handle_client_message(data):
    print(f"handle_client_message triggered with data: {data}")  # Debug print
    session_id = request.sid
    message = data['message']

    # Find the client key
    client_key = next((key for key, value in clients.items() if value['sid'] == session_id), None)

    if not client_key:
        print(f"Error: Could not find client with session ID {session_id}")
        return

    client_number = int(client_key[6:])  # Extract number from 'clientX'
    opponent_key = f'client{client_number - 1}' if client_number % 2 == 0 else f'client{client_number + 1}'
    if opponent_key in clients:
        opponent_sid = clients[opponent_key]['sid']
        socketio.emit('message_response', {'message': message}, to=opponent_sid)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
