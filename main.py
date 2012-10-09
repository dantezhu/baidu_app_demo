#!/usr/bin/env python
# -*- coding: utf-8 -*-

import hashlib

from flask import Flask
from flask import render_template
from flask import request

BD_APPID = 385894
BD_API_KEY = '45EIK7cZSSuQovKreyQHQnwz'
BD_SECRET_KEY = 'Uy2uF4PItYIZcVtIllqAvcn1y2wZiVRO'

app = Flask(__name__)
app.config.from_object(__name__)


def auth_login():
    if 'bd_user' not in request.values or 'bd_sig' not in request.values:
        return False

    bd_user = request.values['bd_user']
    bd_sig = request.values['bd_sig']

    expected_sig = hashlib.md5('bd_user=%s%s' % (bd_user, BD_SECRET_KEY)).hexdigest()

    return expected_sig == bd_sig


@app.route('/index/')
def index():
    is_login = auth_login()
    return render_template('index.html', is_login=is_login)


if __name__ == '__main__':
    app.run(debug=True, port=6299)
