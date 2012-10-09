# -*- coding: utf-8 -*-

import urllib
import httplib
import urlparse
import json
import logging

API_DOMAIN = 'openapi.baidu.com'
AUTHORIZE_URL = 'https://%s/oauth/2.0/authorize' % API_DOMAIN
TOKEN_URL = 'https://%s/oauth/2.0/token' % API_DOMAIN

logger = logging.getLogger('baidu_api')

class BaiduAPI(object):
    """
    封装API
    """

    _appid = None
    _api_key = None
    _secret_key = None

    def __init__(self, appid, api_key, secret_key):
        """
        初始化
        """
        self._appid = appid
        self._api_key = api_key
        self._secret_key = secret_key

    def get_authorize_url(self, redirect_uri, **kwargs):
        """
        获取authorize的url
        """
        params = dict(
            response_type='code',
            client_id=self._api_key,
            redirect_uri=redirect_uri,
            display='page',
        )

        if kwargs:
            params.update(kwargs)

        enc_params = urllib.urlencode(params)

        url = '%s?%s' % (AUTHORIZE_URL, enc_params)

        return url

    def get_token(self, code, redirect_uri, **kwargs):
        """
        使用Authorization Code换取Access Token
        """

        params = dict(
            grant_type='authorization_code',
            code=code,
            redirect_uri=redirect_uri,
            client_id=self._api_key,
            client_secret=self._secret_key,
        )

        if kwargs:
            params.update(kwargs)

        url_parts = urlparse.urlparse(TOKEN_URL)

        data = self._https_send(url_parts.netloc, url_parts.path, params, 'POST')

        try:
            json_data = json.loads(data)
        except Exception, e:
            logger.error('exception occur.msg[%s], traceback[%s]' % (str(e), __import__('traceback').format_exc()))
            return None

        return json_data

    def call(self, path, params, method='POST'):
        """
        通用API调用接口
        """

        params.update(dict(
            format='json',
        ))

        data = self._https_send(API_DOMAIN, path, params, method)

        try:
            json_data = json.loads(data)
        except Exception, e:
            logger.error('exception occur.msg[%s], traceback[%s]' % (str(e), __import__('traceback').format_exc()))
            return None

        return json_data

    def _https_send(self, ip, url_path, params, method='GET'):
        """
        通用https发送接口
        """
        ec_params = urllib.urlencode(params)

        conn = httplib.HTTPSConnection(ip)

        method = method.upper()

        if method == 'GET':
            url = '%s?%s' % (url_path, ec_params)
            conn.request(method, url)
        else:
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            conn.request(method, url_path, ec_params, headers = headers)

        rsp = conn.getresponse()

        if rsp.status != 200:
            raise ValueError, 'status:%d' % rsp.status
        data = rsp.read()

        return data


class BaiduUtils(object):
    """
    百度的一些工具函数，不必生成实例
    """

    @classmethod
    def get_portrait_url(cls, portrait, image_size='large'):
        """
        转化头像
        """

        if image_size == 'small':
            url = 'http://himg.bdimg.com/sys/portraitn/item/%s.jpg' % portrait
        else:
            url = 'http://himg.bdimg.com/sys/portrait/item/%s.jpg' % portrait

        return url
