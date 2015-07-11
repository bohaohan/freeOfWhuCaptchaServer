# -*- coding: utf-8 -*-

from eduLogin.exceptions import APIException


class EducationException(APIException):
    """
    教务系统异常基类
    """
    pass


class EducationCrash(EducationException):
    """
    教务系统崩溃异常，抛出此异常则说明教务系统当前无法访问
    """
    pass


class EducationPasswordError(EducationException):
    """
    教务系统密码错误异常
    """
    pass


class EducationCaptchaError(EducationException):
    """
    教务系统验证码无法识别，通常抛出此异常后需要重试
    """
    pass