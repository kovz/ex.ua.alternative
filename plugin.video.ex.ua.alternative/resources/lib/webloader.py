# -*- coding: utf-8 -*-
# Name:        webloader
# Author:      Roman V.M.
# Created:     18.02.2014
# Licence:     GPL v.3: http://www.gnu.org/copyleft/gpl.html

import os
import urllib
import urllib2
import socket
import cookielib
import re
import hashlib
import base64

if __name__ == '__main__':
    # This is for testing purposes when the module is run from console.
    _cookie_dir = os.path.dirname(__file__)

    def __log__(var_name='', variable=None):
        pass

else:  # If the module is imported during normal plugin run.
    import xbmc
    from logger import log as __log__
    _cookie_dir = xbmc.translatePath('special://profile/addon_data/plugin.video.ex.ua.alternative').decode('utf-8')

LOGIN_URL = 'http://www.ex.ua/login'


class Opener(object):
    """HTTP opener class"""
    headers = [('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:26.0) Gecko/20100101 Firefox/26.0'),
               ('Accept-Charset', 'UTF-8'),
               ('Accept', 'text/html'),
               ('Connection', 'keep-alive')]
    google_bot_user_agent = ('User-Agent', 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)')
    
    def __init__(self, handler=urllib2.BaseHandler(), host='www.ex.ua', language=''):
        """Class constructor"""
        self.opener = urllib2.build_opener(handler)
        if use_google_bot:
            headers[0] = google_bot_user_agent
        self.headers.append(('Host', host))
        if language:
            self.headers.append(('Accept-Language', language))
        self.opener.addheaders = self.headers

    def open(self, url, data=None):
        """Open specified url and return a HTTP session object"""
        return self.opener.open(url, data)

    def get_page(self, url, data=None):
        try:
            session = self.opener.open(url, data)
        except (urllib2.URLError, socket.timeout) as ex:
            __log__('webloader.Opener.get_page. Connection error', ex)
            web_page = ''
        else:
            web_page = session.read().decode('utf-8', 'replace')
            session.close()
        return web_page


class WebLoader(object):

    def __init__(self):
        """
        Class constructor.
        Prepare a cookie jar and a web-page opener.
        """
        self.cookie_file = os.path.join(_cookie_dir, '.cookies')
        self.cookie_jar = cookielib.LWPCookieJar(self.cookie_file)
        if not os.path.exists(self.cookie_file):
            self.cookie_jar.save()
        self.cookie_jar.revert()
        self.opener = Opener(handler=urllib2.HTTPCookieProcessor(self.cookie_jar))

    def get_page(self, url, data=None):
        """
        Load a web-page with a given url.
        """
        self.cookie_jar.load()
        __log__('WebLoader.get_page; cookies', self.get_cookies())
        web_page = self.opener.get_page(url, data)
        self.cookie_jar.save()
        return web_page

    def is_logged_in(self):
        """
        Check if the cookie jar has login data. Returns True, if login cookie is present.
        """
        for cookie in self.cookie_jar:
            if cookie.name == 'ukey' and len(cookie.value) > 1:
                logged_in = True
                break
        else:
            logged_in = False
        return logged_in

    def get_cookies(self):
        """
        Return existing cookies as a dictionary of {name: value} items.
        """
        cookies = {}
        for cookie in self.cookie_jar:
            cookies[cookie.name] = cookie.value
        return cookies

    def check_captcha(self):
        """
        Check if there is a captcha on a loging page. Returns a dictionary
        with 'captcha_id' and 'captcha_file' keys.
        """
        web_page = self.get_page(LOGIN_URL)
        captcha = {'captcha_id': '', 'captcha_file': ''}
        captcha_group = re.search('<img src=\'/captcha\?captcha_id=(.+?)\'', web_page, re.UNICODE)
        if captcha_group is not None:
            captcha_id = captcha_group.group(1)
            captcha_file = os.path.join(_cookie_dir, 'captcha.png')
            os.remove(captcha_file)
            urllib.urlretrieve('http://www.ex.ua/captcha?captcha_id=' + captcha_id, captcha_file)
            captcha = {'captcha_id': captcha_id, 'captcha_file': captcha_file}
        __log__('WebLoader.check_captcha; captcha', captcha)
        return captcha

    def check_error(self, web_page):
        """
        Check if there is an error image on a web-page,
        Returns True if there is no error, and False if the error image is present.
        """
        return re.search('i_error.png', web_page) is None

    def login(self, username, password, remember_user=True, captcha_text='', captcha_id=''):
        """
        Send loging data to ex.ua. Returns True on successful login.
        """
        login_data = [('login', username), ('password', password), ('flag_permanent', int(remember_user)),
                                                                    ('flag_not_ip_assign', 1)]
        if captcha_text:
            login_data.append(('captcha_value', captcha_text))
            login_data.append(('captcha_id', captcha_id))
        post_data = urllib.urlencode(login_data)
        result_page = self.get_page(LOGIN_URL, post_data)
        return self.check_error(result_page)

    def get_direct_link(self, url):
        """Get direct link to a video file"""
        try:
            sesion = self.opener.open(url)
        except (urllib2.URLError, socket.timeout) as ex:
            __log__('webloader.WebLoader.get_girect_link. Connection error', ex)
            resolved_url = ''
        else:
            resolved_url = sesion.geturl()
            sesion.close()
        return resolved_url


def encode(clear):
    key = hashlib.md5(str(True)).hexdigest()
    enc = []
    for i in range(len(clear)):
        key_c = key[i % len(key)]
        enc_c = chr((ord(clear[i]) + ord(key_c)) % 256)
        enc.append(enc_c)
    return base64.urlsafe_b64encode(''.join(enc))


def decode(enc):
    key = hashlib.md5(str(True)).hexdigest()
    dec = []
    enc = base64.urlsafe_b64decode(enc)
    for i in range(len(enc)):
        key_c = key[i % len(key)]
        dec_c = chr((256 + ord(enc[i]) - ord(key_c)) % 256)
        dec.append(dec_c)
    return ''.join(dec)


if __name__ == '__main__':
    pass
