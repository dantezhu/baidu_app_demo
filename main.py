#!/usr/bin/env python
# -*- coding: utf-8 -*-

import hashlib

from flask import Flask
from flask import render_template, redirect
from flask import request, session

from baidu_api import BaiduAPI

BD_APPID = 385894
BD_API_KEY = '45EIK7cZSSuQovKreyQHQnwz'
BD_SECRET_KEY = 'Uy2uF4PItYIZcVtIllqAvcn1y2wZiVRO'

app = Flask(__name__)
app.config.from_object(__name__)

baidu_api = BaiduAPI(BD_APPID, BD_API_KEY, BD_SECRET_KEY)

def auth_login():
    if 'bd_user' not in request.values or 'bd_sig' not in request.values:
        return False

    bd_user = request.values['bd_user']
    bd_sig = request.values['bd_sig']

    expected_sig = hashlib.md5('bd_user=%s%s' % (bd_user, BD_SECRET_KEY)).hexdigest()

    if expected_sig != bd_sig:
        return False

    s_bd_user = session.get('bd_user', None)

    return s_bd_user == bd_user


@app.route('/index/')
def index():
    is_login = auth_login()
    return render_template('index.html', is_login=is_login)


if __name__ == '__main__':
    app.run(debug=True, port=6299)
