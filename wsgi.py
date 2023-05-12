from web import app
import os

if __name__ == "__main__":
	app.run(host="127.0.0.1", port=5000, debug=bool(os.getenv("DEBUG")))