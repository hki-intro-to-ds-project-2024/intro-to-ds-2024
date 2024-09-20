from flask import Flask, send_file, send_from_directory
from src.config import FRONTEND_DIR, DEVELOPMENT_ENV

app = Flask("bicycle-map-app")

@app.route("/")
def index():
    return send_file(FRONTEND_DIR / "index.html")

@app.route("/<path:path>")
def file_paths(path):
    return send_from_directory(FRONTEND_DIR,path)

if __name__ == "__main__":
    app.run(debug=DEVELOPMENT_ENV)