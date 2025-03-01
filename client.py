import socketio
from ChessData import ChessData
class ChessClient:
    def __init__(self):
        self.sio = socketio.Client()
        self.register_events()

    def register_events(self):
        # Register event handlers
        self.sio.on('connect', self.on_connect)
        self.sio.on('disconnect', self.on_disconnect)
        self.sio.on('message_response', self.on_message_response)
        self.sio.on('initial_color',self.on_initial_color)

    def on_initial_color(self,data):
        ChessData.game_color_update(data['message'])

    def on_connect(self):
        print("Connected to the server!")
        

    def on_disconnect(self):
        print("Disconnected from the server.")

    def on_message_response(self, data):
        # Handle the server's response
        self.handle_opponent_move(data)
        

    def handle_opponent_move(self, data):
        # Process the opponent's move
        data = data['message']
        ChessData.update_opponent(data)

    def connect_to_server(self, url):
        try:
            if self.sio.connected:
                self.sio.disconnect()
            self.sio.connect(url, transports=['websocket', 'polling'])
            print("Connected successfully!")
        except Exception as e:
            print(f"Failed to connect to server: {e}")

    def disconnect_from_server(self):
        self.sio.disconnect()

    def send_message(self, message):
        # Send a message to the server
        self.sio.emit('client_message', {'message': message})

