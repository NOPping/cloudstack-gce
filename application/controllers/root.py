from application import app
from flask import jsonify, Response

@app.route('/')
def api_root():
    message = {
            'status': 200,
            'message': app.config["CLOUDSTACK_URL"]
    }
    resp = jsonify(message)
    resp.status_code = 200

    return resp
