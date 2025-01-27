import os
import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template
import secrets
from flask_socketio import SocketIO, join_room, leave_room, emit
from GameController import GameController


app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(16)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

rooms = {}  # Dictionary to track active rooms and players

#game_controller = GameController()

@app.route('/')
def index():
    return "Chess Game Server Running"

@socketio.on('join')
def handle_join(data):
    username = data['username']
    room = data['room']
    join_room(room)
    
    if room not in rooms:
        rooms[room] = []
    rooms[room].append(username)

    emit('status', {'message': f"{username} joined the room."}, room=room)
    print(f"{username} joined room: {room}")

@socketio.on('leave')
def handle_leave(data):
    username = data['username']
    room = data['room']
    leave_room(room)
    
    if room in rooms and username in rooms[room]:
        rooms[room].remove(username)
    emit('status', {'message': f"{username} left the room."}, room=room)
    print(f"{username} left room: {room}")

@socketio.on('move')
def handle_move(data):
    room = data['room']
    move = data['move']  
    emit('opponent_move', {'move': move}, room=room, include_self=False)
    print(f"Move in room {room}: {move}")

if __name__ == '__main__':

     
    port = int(os.environ.get("PORT", 10000))
    socketio.run(app, host='192.168.1.73', port=5000, debug=True, use_reloader=False)



