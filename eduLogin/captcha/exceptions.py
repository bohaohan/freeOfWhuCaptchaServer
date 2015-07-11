# -*- coding: utf-8 -*-

from eduLogin.exceptions import APIException


class CaptchaException(APIException):
    """
    验证码异常类
    """
    pass


class CaptchaParamError(CaptchaException):
    """
    验证码参数提供错误
    """
    pass


class CaptchaDownloadError(CaptchaException):
    """
    验证码下载异常
    """
    pass
