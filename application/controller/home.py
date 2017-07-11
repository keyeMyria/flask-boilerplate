from flask import Blueprint, jsonify

home = Blueprint('home', __name__)


@home.route('/', methods=['GET'])
def index():
    return jsonify(hello='world')
