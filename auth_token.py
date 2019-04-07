from flask import current_app
from itsdangerous import JSONWebSignatureSerializer, BadData


class BadToken(Exception):
    pass


class AuthToken(object):
    def __init__(self):
        with current_app.app_context():
            self.serializer = JSONWebSignatureSerializer(
                secret_key=current_app.config['JWT_SECRET'],
                serializer_kwargs={'sort_keys': True},
                algorithm_name='HS256',
                salt=None
            )

    def generate_jwt(self, student_id: str) -> str:
        return self.serializer.dumps({'studentId': student_id}, header_fields={'typ': 'JWT'}).decode()

    def validate_jwt(self, token_string: str):
        try:
            obj = self.serializer.loads(token_string.encode())
            return obj['studentId']
        except BadData:
            raise BadToken('Invalid Token')
