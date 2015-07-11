# -*- coding: utf-8 -*-
import urllib, urllib2, json, time, sys ,base64
import requests
#import simplejson as json
from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from eduLogin.education.education import *
from eduLogin.captcha.captcha import Captcha
def index(request):
	return render_to_response("index.html")


def login(request):
	if request.method == 'GET':
		img = request.GET.get("img")
		img = img.replace("*1*","/")
		img = img.replace("*2*",":")
		img = img.replace("*3*",";")
		img = img.replace("*4*","+")
		img = img.replace("*5*","=")
		img = img[23:]
		imag = base64.b64decode(img)
		image = Image.open(StringIO(imag))
		result = Captcha(image=image).result()
		return HttpResponse(json.dumps({'result': result}))
		#return HttpResponse(json.dumps(img))
		
	