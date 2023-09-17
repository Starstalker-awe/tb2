import socketio

sio = socketio.Client()

@sio.event
def connect():
    sio.emit('data', {'auth': 123})

sio.on('got data', lambda data:print(data))


sio.connect("ws://127.0.0.1:5000")