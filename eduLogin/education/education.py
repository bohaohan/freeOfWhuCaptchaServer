# -*- coding: utf-8 -*-

import re
import socket

import requests
from requests.exceptions import RequestException
from StringIO import StringIO
from PIL import Image
from django.conf import settings

from eduLogin.captcha import Captcha
from eduLogin.education.exceptions import EducationCrash, EducationPasswordError, EducationCaptchaError
#from utils import transform_weekday


def get_login_cookie(retry_times=settings.EDUCATION_RETRY_TIMES):
    """
    获取教务系统第一次 cookie
    :param retry_times: 尝试重试次数
    :return: cookie
    """
    if retry_times <= 0:
        raise EducationCrash(u'error occurred when accessing the first cookie')

    url = 'http://210.42.121.241/'
    try:
        r = requests.get(url, timeout=settings.EDUCATION_TIMEOUT)
    except (RequestException, socket.timeout) as exc:
        return get_login_cookie(retry_times=retry_times-1)

    return r.cookies


def get_captcha_alpha(cookies, manual=False, retry_times=settings.EDUCATION_RETRY_TIMES):
    """
    获取识别好的验证码字母
    :param cookies: 教务系统第一次 cookie 值 (由 get_login_cookie 函数得到)
    :param manual: 为 True 则使用人工验证码, 为 False 则使用机器验证码 (如无意外推荐使用机器验证码)
    :param retry_times: 尝试重试次数
    :return: (str, cookies) str为识别的验证码字母, cookies为新的cookies
    """
    if retry_times <= 0:
        raise EducationCrash(u'error occurred when getting captcha alpha')

    url = 'http://210.42.121.241/servlet/GenImg'
    try:
        r = requests.get(url, cookies=cookies, timeout=settings.EDUCATION_TIMEOUT)
    except (RequestException, socket.timeout) as exc:
        return get_captcha_alpha(cookies=cookies, manual=manual, retry_times=retry_times-1)

    image = Image.open(StringIO(r.content))
    if manual:  # 人工验证码
        string = StringIO()
        image.save(string, format='jpeg')
        string.seek(0)
        result = Captcha(image=string, manual=True).result()
        string.close()
    else:  # 机器验证码
        result = Captcha(image=image).result()
    return result, r.cookies


def login_with_cookie(sid, pwd, cookies, captcha_alpha, retry_times=settings.EDUCATION_RETRY_TIMES):
    """
    以学生身份登录教务系统(需提供cookie及验证码)
    :param sid: 学号
    :param pwd: 密码
    :param cookies: cookie 值
    :param captcha_alpha: 验证码字母
    :param retry_times: 尝试重试次数
    """
    if retry_times <= 0:
        raise EducationCrash(u'error occurred when login educational system')

    url = 'http://210.42.121.241/servlet/Login'
    payload = {
        'id': sid,
        'pwd': pwd,
        'xdvfb': captcha_alpha,
    }

    try:
        r = requests.post(url, data=payload, cookies=cookies, timeout=settings.EDUCATION_TIMEOUT)
    except (RequestException, socket.timeout) as exc:
        return login_with_cookie(sid=sid, pwd=pwd, cookies=cookies, captcha_alpha=captcha_alpha, retry_times=retry_times-1)

    if re.search(u'武汉大学教务部', r.text):
        return
    elif re.search(u'密码错误|对不起，您无权访问当前页面', r.text):
        raise EducationPasswordError(u'the password of %s is wrong' % sid)
    elif re.search(u'验证码', r.text):
        raise EducationCaptchaError(u'captcha error')
    else:
        raise EducationCrash(u'unknown error when login education system')


def guest_login_with_cookie(cookies, captcha_alpha, retry_times=settings.EDUCATION_RETRY_TIMES):
    """
    以游客身份登录教务系统(需提供cookie及验证码)
    :param cookies: cookie 值
    :param captcha_alpha: 验证码字母
    :param retry_times: 尝试重试次数
    """
    if retry_times <= 0:
        raise EducationCrash(u'error occurred when guest login educational system')

    url = 'http://210.42.121.241/servlet/Login'
    payload = {
        'id': '',
        'pwd': '',
        'xdvfb': captcha_alpha,
    }
    try:
        r = requests.post(url, data=payload, cookies=cookies, timeout=settings.EDUCATION_TIMEOUT)
    except (RequestException, socket.timeout) as exc:
        return guest_login_with_cookie(cookies=cookies, captcha_alpha=captcha_alpha, retry_times=retry_times-1)

    if re.search(u'武汉大学教务部', r.text):
        return
    else:
        raise EducationCrash(u'unknown error when guest login education system')


def login(sid, pwd, manual=False, retry_times=settings.EDUCATION_LOGIN_RETRY_TIMES):
    """
    通过学号和密码登录教务系统
    :param sid: 学号
    :param pwd: 密码
    :param manual: 为 True 则使用人工验证码, 为 False 则使用机器验证码 (如无意外推荐使用机器验证码)
    :param retry_times: 尝试重试次数
    :return: cookie 值
    """
    if retry_times <= 0:  # 因为只有验证码错误会持续重试，所以如果 retry_times <= 0 则抛出验证码异常
        raise EducationCaptchaError(u'captcha error')

    cookies = get_login_cookie()
    captcha, cookies = get_captcha_alpha(cookies=cookies, manual=manual)
    try:
        login_with_cookie(sid=sid, pwd=pwd, cookies=cookies, captcha_alpha=captcha)
    except EducationCaptchaError as exc:
        return login(sid=sid, pwd=pwd, manual=manual, retry_times=retry_times-1)

    return cookies


def guest_login(manual=False, retry_times=settings.EDUCATION_LOGIN_RETRY_TIMES):
    """
    以游客身份登录教务系统
    :param manual: 为 True 则使用人工验证码, 为 False 则使用机器验证码 (如无意外推荐使用机器验证码)
    :param retry_times: 尝试重试次数
    :return: cookie 值
    """
    if retry_times <= 0:  # 因为只有验证码错误会持续重试，所以如果 retry_times <= 0 则抛出验证码异常
        raise EducationCaptchaError(u'captcha error')

    cookies = get_login_cookie()
    captcha, cookies = get_captcha_alpha(cookies=cookies, manual=manual)
    try:
        guest_login_with_cookie(cookies=cookies, captcha_alpha=captcha)
    except EducationCaptchaError as exc:
        return guest_login(manual=manual, retry_times=retry_times-1)

    return cookies


# def decode_lessons_time(text):
#     """
#     解析教务系统的课程时间字符串为字典
#     :param text: 课程时间字符串 (unicode)
#     :return: dict
#     """
#     if not isinstance(text, unicode):
#         raise ValueError('The argument must be unicode type')

#     result = []
#     text = text.strip().replace(u'\t', u'').replace(u'\n', u'')
#     while u'  ' in text:
#         text = text.replace(u'  ', u' ')

#     # 将split出来的列表中的多个连续空格合并为一个空格
#     cook = ''.join(filter(lambda x: x, text.split(u' ')))
#     cook = filter(lambda x: x, cook.split(u'\r'))

#     try:
#         for food in cook:
#             if food:
#                 food = food.replace(u'每', u'').replace(u'周', u'').replace(u'节', u'').replace(u':', u',').replace(u';', u',').split(u',')
#                 result.append({
#                     'weekday': transform_weekday(food[0]),
#                     'week_from': int(food[1].split('-')[0]),
#                     'week_to': int(food[1].split('-')[1]),
#                     'repeats': int(food[2]),
#                     'class_begin': int(food[3].split('-')[0]),
#                     'class_over': int(food[3].split('-')[1]),
#                     'location': food[4] + ',' + food[5] if len(food) > 4 else u'',
#                 })
#     except IndexError as exc:
#         logger.warning(u'Cannot decode lessons time with: ' + text)
#         pass

#     return result