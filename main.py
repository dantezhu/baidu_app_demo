#!/usr/bin/env python
# -*- coding: utf-8 -*-

import hashlib

from flask import Flask
from flask import render_template, redirect, url_for
from flask import request, session

from baidu_api import BaiduAPI

SECRET_KEY = '2334'

BD_APPID = 385894
BD_API_KEY = '45EIK7cZSSuQovKreyQHQnwz'
BD_SECRET_KEY = 'Uy2uF4PItYIZcVtIllqAvcn1y2wZiVRO'

app = Flask(__name__)
app.config.from_object(__name__)

baidu_api = BaiduAPI(BD_APPID, BD_API_KEY, BD_SECRET_KEY)

def get_login_uid():
    if 'bd_user' not in request.values or 'bd_sig' not in request.values:
        #如果没有参数，那有session也行
        if 'uid' in session:
            return session['uid']
        return None

    bd_user = request.values['bd_user']
    bd_sig = request.values['bd_sig']

    expected_sig = hashlib.md5('bd_user=%s%s' % (bd_user, BD_SECRET_KEY)).hexdigest()

    if expected_sig != bd_sig:
        return None

    uid = session.get('uid', None)

    if uid != bd_user:
        #说明换了用户了，需要重新授权
        return None

    return uid

@app.route('/index')
def index():
    login_uid = get_login_uid()

    session.pop('uid', None)

    authorize_url = None

    if not login_uid:
        authorize_url = baidu_api.get_authorize_url(
            'http://%s%s' % (request.host, url_for('.login_callback'))
        )

    return render_template('index.html', login_uid=login_uid, authorize_url=authorize_url)

@app.route('/login_callback')
def login_callback():
    code = request.values.get('code', None)

    if not code:
        return u'参数错误'

    token_data = baidu_api.get_token(code, redirect_uri='http://%s%s' % (request.host, url_for('.login_callback')))
    if not token_data:
        return u'获取token失败'

    access_token = token_data['access_token']

    json_data = baidu_api.call('/rest/2.0/passport/users/getLoggedInUser', dict(
        access_token=access_token
    ), method='GET')

    if not json_data:
        return u'获取用户资料报错'

    session['uid'] = json_data['uid']

    return render_template('login_callback.html')


if __name__ == '__main__':
    app.run(debug=True, port=6299)
