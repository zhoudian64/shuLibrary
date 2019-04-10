import pickle
from redis import Redis
from werkzeug.exceptions import HTTPException
from flask import Blueprint, abort, current_app, g, jsonify, request

from service import Student, InvalidCredential, CredentialRequired
from auth_token import AuthToken, BadToken

v1 = Blueprint(__name__, __name__, url_prefix='/')


@v1.before_request
def connect_db():
    with current_app.app_context():
        redis_kwargs = current_app.config['REDIS_KWARGS']
    g.db = Redis(**redis_kwargs)


@v1.route('/login', methods=['POST'])
def login():
    input_data = request.get_json()
    username = input_data.get('username')
    password = input_data.get('password')
    if username is None or password is None:
        abort(400)
    student = Student()
    try:
        student.login(username, password)
    except InvalidCredential as error:
        abort(401, str(error))
    g.db.set('shu-library-{}'.format(username), pickle.dumps(student), ex=3600)
    return jsonify({
        'token': AuthToken().generate_jwt(username)
    })


@v1.route('/loans', methods=['GET'])
def loans():
    authorization = request.headers.get('Authorization')
    if authorization is None or not authorization.startswith('Bearer '):
        abort(403)
    token = authorization[7:]
    try:
        username = AuthToken().validate_jwt(token)
        raw_student_data = g.db.get('shu-library-{}'.format(username))
        if raw_student_data is None:
            abort(403)
        student = pickle.loads(raw_student_data)
        return jsonify({
            'histories': student.get_loans()
        })
    except CredentialRequired:
        abort(403)
    except BadToken as error:
        abort(403, str(error))


@v1.route('/histories', methods=['GET'])
def histories():
    authorization = request.headers.get('Authorization')
    if authorization is None or not authorization.startswith('Bearer '):
        abort(403)
    token = authorization[7:]
    try:
        username = AuthToken().validate_jwt(token)
        raw_student_data = g.db.get('shu-library-{}'.format(username))
        if raw_student_data is None:
            abort(403)
        student = pickle.loads(raw_student_data)
        return jsonify({
            'histories': student.get_histories()
        })
    except CredentialRequired:
        abort(403)
    except BadToken as error:
        abort(403, str(error))


@v1.errorhandler(HTTPException)
def errorhandler(error):
    return jsonify({
        'error': error.description
    })
