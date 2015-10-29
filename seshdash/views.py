from django.shortcuts import render, get_object_or_404, render_to_response
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views import generic
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.core import serializers
from guardian.shortcuts import get_objects_for_user
from guardian.shortcuts import get_perms

from seshdash.models import Sesh_Site, PV_Production_Point, Site_Weather_Data, BoM_Data_Point
from seshdash.utils import time_utils
from pprint import pprint

import json,time,random,datetime

# Import for API
from rest_framework import generics, permissions
from seshdash.serializers import BoM_Data_PointSerializer

@login_required
def index(request,site_id=0):

    sites = Sesh_Site.objects.all()
    sites = get_objects_for_user(request.user,'seshdash.view_Sesh_Site')
    if not site_id:
        #return first site user has action
        print "no side id recieved"
        site_id = sites[0].pk
    #TODO this will break when there is no site created
    context_dict, content_json = get_user_data(request.user,site_id,sites)
    context_dict = jsonify_dict(context_dict,content_json)
    print context_dict
    return render(request,'seshdash/main-dash.html',context_dict)

#testing out some nvd3 graphs
def pie(request):
    xdata = ["Apple", "Apricot", "Avocado", "Banana", "Boysenberries", "Blueberries", "Dates", "Grapefruit", "Kiwi", "Lemon"]
    ydata = [52, 48, 160, 94, 75, 71, 490, 82, 46, 17]
    chartdata = {'x': xdata, 'y': ydata}
    charttype = "pieChart"
    chartcontainer = 'piechart_container'
    data = {
        'charttype': charttype,
        'chartdata': chartdata,
        'chartcontainer': chartcontainer,
        'extra': {
            'x_is_date': False,
            'x_axis_format': '',
            'tag_script_js': True,
            'jquery_on_ready': False,
        }
    }
    return render_to_response('seshdash/piechart.html', data)

def linebar(request):
    """
    lineplusbarchart page
    """
    start_time = int(time.mktime(datetime.datetime(2012, 6, 1).timetuple()) * 1000)
    nb_element = 100
    xdata = range(nb_element)
    xdata = map(lambda x: start_time + x * 1000000000, xdata)
    ydata = [i + random.randint(1, 10) for i in range(nb_element)]
    ydata2 = [i + random.randint(1, 10) for i in reversed(range(nb_element))]
    kwargs1 = {}
    kwargs1['bar'] = True

    tooltip_date = "%d %b %Y %H:%M:%S %p"
    extra_serie1 = {"tooltip": {"y_start": "$ ", "y_end": ""},
                    "date_format": tooltip_date}
    extra_serie2 = {"tooltip": {"y_start": "", "y_end": " min"},
                    "date_format": tooltip_date}

    chartdata = {
        'x': xdata,
        'name1': 'series 1', 'y1': ydata, 'extra1': extra_serie1, 'kwargs1': kwargs1,
        'name2': 'series 2', 'y2': ydata2, 'extra2': extra_serie2,
    }

    charttype = "linePlusBarChart"
    chartcontainer = 'chart_container'  # container name
    data = {
        'charttype': charttype,
        'chartdata': chartdata,
        'chartcontainer': chartcontainer,
        'extra': {
            'x_is_date': True,
            'x_axis_format': '%d %b %Y %H',
            'tag_script_js': True,
            'jquery_on_ready': True,
            'focus_enable': True,
        },
    }
    return render_to_response('seshdash/line_bar.html', data)


def logout_user(request):
    logout(request)
    return render(request,'seshdash/logout.html')

def login_user(request):

    context_dict = {}
    #is the user already logged in?
    if request.user.is_authenticated():
            return index(request)
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
            return index(request)
        else:
            #return an error message
            return render(request,'seshdash/login.html')
    else:
            #return invalid login page
            return render(request,'seshdash/login.html')


def get_user_data(user,site_id,sites):
    site = Sesh_Site.objects.get(pk=site_id)
    if not user.has_perm('seshdash.view_Sesh_Site',site):
        print "user doesn't have permission to view site %s"%site_id
        #TODO return 403 permission denied
        return {},{}
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

class BoM_Data_Stream(generics.ListCreateAPIView):
    queryset = BoM_Data_Point.objects.all()
    serializer_class = BoM_Data_PointSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,) 
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class BoM_Data_Detail(generics.RetrieveUpdateDestroyAPIView):
    queryset = BoM_Data_Point.objects.all()
    serializer_class = BoM_Data_PointSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
