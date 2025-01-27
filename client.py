import socketio
from GameController import GameController

sio = socketio.Client()

SERVER_URL = 'https://Chess-Game.onrender.com'


class ChessClient:
    def __init__(self):
        self.sio = socketio.Client()
        self.connect_to_server()

    def connect_to_server(self):
        try:
            self.sio.connect(SERVER_URL)
            print("Connected to server")
        except Exception as e:
            print(f"Connection failed: {e}")
#initialize GameController
#game= GameController()

username = input("Enter your username: ")
room = input("Enter room name to join: ")

@sio.event
def connect():
    print("Connected to server!")
    sio.emit('join', {'username': username, 'room': room})

@sio.event
def status(data):
    print(data['message'])

@sio.event
def opponent_move(data):
    move = data['move']
    print(f"Opponent's move: {move}")

@sio.event
def disconnect():
    print("Disconnected from server.")

def send_move(move):
    sio.emit('move', {'room': room, 'move': move})

sio.connect('http://192.168.1.73:5000')

while True:
    move = input("Enter your move (or 'quit' to leave): ")
    if move.lower() == 'quit':
        sio.emit('leave', {'username': username, 'room': room})
        sio.disconnect()
        break
    send_move(move)

