from web import socket, app
import os

if __name__ == "__main__":
	socket.run(app, host="127.0.0.1", port=5000, debug=bool(os.getenv("DEBUG")))