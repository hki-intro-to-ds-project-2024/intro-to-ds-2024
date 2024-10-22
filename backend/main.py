from flask import Flask, send_file, send_from_directory, jsonify, request
from flask_cors import CORS
from src.config import FRONTEND_DIR, DEVELOPMENT_ENV
from src.analytics.analytics import Analytics
import logging

app = Flask("bicycle-map-app")
CORS(app)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)
analytics = Analytics(logger=logger.getChild("analytics"))

@app.route("/")
def index():
    return send_file(FRONTEND_DIR / "index.html")

@app.route("/<path:path>")
def file_paths(path):
    return send_from_directory(FRONTEND_DIR,path)

@app.route("/nodes")
def all_nodes():
    """
    Example request: /nodes?time_start=2022-01-01T00:00:00&time_end=2022-01-02T00:00:00&zero_rides=1&proportion=0.5
    """
    time_start = request.args.get('time_start')
    time_end = request.args.get('time_end')
    zero_rides = request.args.get('zero_rides')
    proportion = request.args.get('proportion')
    nodes_json = analytics.get_nodes_json(time_start, time_end, zero_rides, proportion)
    logger.info(nodes_json)
    return jsonify(nodes_json)

@app.route("/predictions")
def predictions():
    """
    Example request: /predictions?time_start=2022-01-01T00:00:00&time_end=2022-01-02T00:00:00&zero_rides=1
    """
    time_start = request.args.get('time_start')
    time_end = request.args.get('time_end')
    zero_rides = request.args.get('zero_rides')
    proportion = request.args.get('proportion')
    predictions_json = analytics.get_predictions_json(time_start, time_end, zero_rides)
    logger.info(predictions_json)
    return jsonify(predictions_json)

if __name__ == "__main__":
    app.run(debug=DEVELOPMENT_ENV)

