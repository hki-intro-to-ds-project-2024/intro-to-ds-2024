from flask import Flask, send_file, send_from_directory, jsonify
from src.config import FRONTEND_DIR, DEVELOPMENT_ENV
from src.analysis import Analytics

app = Flask("bicycle-map-app")
analytics = Analytics()

@app.route("/")
def index():
    return send_file(FRONTEND_DIR / "index.html")

@app.route("/<path:path>")
def file_paths(path):
    return send_from_directory(FRONTEND_DIR,path)

@app.route("/nodes")
def all_nodes():
    nodes = Analytics.node
    return jsonify(nodes)

if __name__ == "__main__":
    app.run(debug=DEVELOPMENT_ENV)