#!/usr/bin/env python
# -*- coding: utf-8 -*-

import hashlib

from flask import Flask
from flask import render_template, redirect, url_for
from flask import request, session

from baidu_api import BaiduAPI, BaiduAPIUtils

SECRET_KEY = '2334'

BD_APPID = 385894
BD_API_KEY = '45EIK7cZSSuQovKreyQHQnwz'
BD_SECRET_KEY = 'Uy2uF4PItYIZcVtIllqAvcn1y2wZiVRO'

app = Flask(__name__)
app.config.from_object(__name__)

baidu_api = BaiduAPI(BD_APPID, BD_API_KEY, BD_SECRET_KEY)

def get_login_userid():
    """
    登录时的检查登录态
    """
    if 'bd_user' not in request.values or 'bd_sig' not in request.values:
        return None

    bd_user = request.values['bd_user']
    bd_sig = request.values['bd_sig']

    expected_sig = hashlib.md5('bd_user=%s%s' % (bd_user, BD_SECRET_KEY)).hexdigest()

    if expected_sig != bd_sig:
        return None

    userid = session.get('userid', None)

    if userid != bd_user:
        #说明换了用户了，需要重新授权
        return None

    return userid

@app.route('/login')
def login():
    login_userid = get_login_userid()

    if not login_userid:
        authorize_url = baidu_api.get_authorize_url(
            'http://%s%s' % (request.host, url_for('.login_callback'))
        )
        return render_template('login.html', authorize_url=authorize_url)

    return redirect(url_for('index'))

@app.route('/index')
def index():
    login_userid = session.get('userid', None)

    if not login_userid:
        return u'请先登录'

    return render_template('index.html', login_userid=login_userid)

@app.route('/login_callback')
def login_callback():
    code = request.values.get('code', None)

    if not code:
        return u'参数错误'

    token_data = baidu_api.get_token(code, redirect_uri='http://%s%s' % (request.host, url_for('.login_callback')))
    if not token_data:
        return u'获取token失败'

    access_token = token_data['access_token']

    userinfo = baidu_api.call('/rest/2.0/passport/users/getLoggedInUser', dict(
        access_token=access_token
    ), method='GET')

    if not userinfo:
        return u'获取用户资料报错'

    session['userid'] = userinfo['uid']

    #在正式应用中，这里就应该把用户数据存储下来了。
    #这里只做演示就不搞数据库了

    portrait_url = BaiduAPIUtils.get_portrait_url(userinfo['portrait'], 'large')
    print portrait_url

    return render_template('login_callback.html', userinfo=userinfo, portrait_url=portrait_url)


if __name__ == '__main__':
    app.run(debug=True, port=6299)
