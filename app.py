import os
import random
import string
from flask import Flask

from views.v1 import v1

app = Flask(__name__)
if os.getenv('JWT_SECRET') is None:
    os.environ['JWT_SECRET'] = ''.join([random.choice(string.printable) for _ in range(24)])

app.config['JWT_SECRET'] = os.getenv('JWT_SECRET')
app.config['REDIS_KWARGS'] = {'host': '127.0.0.1', 'port': 6379, 'db': 0}
app.register_blueprint(v1)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5001, debug=True)
