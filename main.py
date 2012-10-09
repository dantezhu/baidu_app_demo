#!/usr/bin/env python
# -*- coding: utf-8 -*-

import hashlib

from flask import Flask
from flask import render_template, redirect, url_for
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

@app.route('/index')
def index():
    is_login = auth_login()

    authorize_url = None

    if not is_login:
        authorize_url = baidu_api.get_authorize_url(
            'http://%s%s' % (request.host, url_for('.login_callback'))
        )

    return render_template('index.html', is_login=is_login, authorize_url=authorize_url)

@app.route('/login_callback')
def login_callback():
    code = request.values.get('code', None)

    if not code:
        return u'参数错误'

    token_data = baidu_api.get_token(code)
    if not token_data:
        return u'获取token失败'

    access_token = token_data['access_token']

    json_data = baidu_api.call('/rest/2.0/passport/users/getLoggedInUser', dict(
        access_token=access_token
    ), method='GET')

    if not json_data:
        return u'获取用户资料报错'

    return str(json_data)


if __name__ == '__main__':
    app.run(debug=True, port=6299)
