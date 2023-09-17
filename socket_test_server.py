from flask import Flask
import flask_socketio
import functools

app = Flask(__name__)

socket = flask_socketio.SocketIO(app)


def need_code(func):
    @functools.wraps(func)
    def deced(data):
        if data['auth'] != 123:
            flask_socketio.disconnect()
        else: func(data)
    return deced


@socket.on('connect')
def connect_sock():
    socket.emit("response", {'data': True})

@socket.on('auth')
def auth(data):
    print(data)

@need_code
@socket.on('data')
def give_data(data):
    socket.emit('got data', {'data': [123, 456, 789]})


socket.run(app, host="127.0.0.1", port=5000, debug=False)