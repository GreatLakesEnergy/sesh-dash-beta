from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views import generic
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.core import serializers

from .models import Sesh_Site, PV_Production_Point, Site_Weather_Data
from seshdash.utils import time_utils
import json
from pprint import pprint

@login_required
def index(request,site_id=0):

    if not site_id:
        #return first site user has action
        print "no side id recieved"
        site_id = 1

    context_dict, content_json = get_user_data(request.user,site_id)
    context_dict = jsonify_dict(context_dict,content_json)
    print context_dict
    return render(request,'seshdash/main-dash.html',context_dict)


def logout_user(request):
    logout(request)
    return render(request,'seshdash/logout.html')

def login_user(request):

    context_dict = {}
    #is the user already logged in?
    if request.user.is_authenticated():
            context_dict, content_json = get_user_data(request.user,1)
            context_dict['data_json'] = content_json
            #TODO call the function index directly instead. Will reduce code
            return render(request,'seshdash/main-dash.html',context_dict)
    #if not did we get post request ?
    if not request.POST:
        return render(request,'seshdash/login.html')
    username = request.POST['inputEmail']
    password = request.POST['inputPassword']
    user = authenticate(username=username, password=password)

    if user is not None:
        if user.is_active:
            login(request,user)
            #send user name and favorite site data to index page for initial login load
            context_dict, content_json = get_user_data(user,1)
            context_dict = jsonify_dict(context_dict,content_json)
            return render(request,'seshdash/main-dash.html',context_dict)
        else:
            #return an error message
            return render(request,'seshdash/login.html')
    else:
            #return invalid login page
            return render(request,'seshdash/login.html')
"""
Get user site information

"""
def get_user_sites(user):
    pass
#need row based permissioning

def get_user_data(user,site_id):
    #TODO implement row based permissions
    #TODO HACK getting all sites for now till we have row based permissions
    site = Sesh_Site.objects.get(pk=site_id)
    sites = Sesh_Site.objects.all()
    context_data = {}
    context_data_json = {}
    context_data['sites'] = sites
    context_data['active_site'] = site
    context_data_json['sites'] = serialize_objects(sites)
    last_5_days = time_utils.get_last_five_days()

    weather_data = Site_Weather_Data.objects.filter(site=site,date__range=[last_5_days[0],last_5_days[4]])
    power_data  = PV_Production_Point.objects.filter(site=site,time__range=[last_5_days[0],last_5_days[4]])

    weather_data_json = serialize_objects(weather_data)
    power_data_json = serialize_objects(power_data)

    context_data['site_weather'] = weather_data
    context_data['site_power'] = power_data

    context_data_json['site_weather'] = weather_data_json
    context_data_json['site_power'] = power_data_json

    return context_data,context_data_json


def jsonify_dict(context_dict,content_json):
            context_dict['weather_json'] = content_json['site_weather']
            context_dict['power_json'] = content_json['site_power']
            context_dict['sites_json'] = content_json['sites']
            return context_dict
"""
Turn django objects in JSON
"""

def serialize_objects(objects, format_ = 'json'):
    return serializers.serialize('json',objects)
