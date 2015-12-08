#Django libs
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

#Import Models and Forms
from seshdash.models import Sesh_Site,Site_Weather_Data, BoM_Data_Point
from seshdash.utils import time_utils
from pprint import pprint
from seshdash.forms import SiteForm
from django.db.models import Avg
from django.db.models import Sum

#Import utils
from datetime import timedelta
from datetime import datetime, date, time, tzinfo
import json,time,random,datetime

# Import for API
from rest_framework import generics, permissions
from seshdash.serializers import BoM_Data_PointSerializer, UserSerializer
from django.contrib.auth.models import User

@login_required
def index(request,site_id=0):

    sites = Sesh_Site.objects.all()
    sites = get_objects_for_user(request.user,'seshdash.view_Sesh_Site')
    context_dict = {}
    #Handle fisrt login if user has no site setup:
    if not sites:
        context_dict['form'] = SiteForm()
        return render(request,'seshdash/initial-login.html',context_dict)
    if not site_id:
        #return first site user has action
        print "no side id recieved"
        site_id = sites[0].pk
    #Check if user has any sites under their permission
    context_dict, content_json = get_user_data(request.user,site_id,sites)

    context_dict = jsonify_dict(context_dict,content_json)
    #Generate date for dashboard  TODO use victron solar yield data using mock weather data for now
    y_data,x_data = prep_time_series(context_dict['site_weather'],'cloud_cover','date')
    y2_data,x2_data = prep_time_series(context_dict['site_weather'],'cloud_cover','date')
    #create graphs for PV dailt prod vs cloud cover

    context_dict=linebar(x2_data,y_data,y2_data,'WH produced','% cloud cover','chartcontainer',context_dict)

    # Create an object of the get_high_chart_date

    context_dict['high_chart']= get_high_chart_data()

    return render(request,'seshdash/main-dash.html',context_dict)
0
@login_required
def create_site(request):
    context_dict = {}
    if request.method == "POST":
        form = SiteForm(request.POST)

        if (form.is_valid):
            context_dict['message'] = "success"
            form.save()
        else:
            #TODO provide meaning full erro message from validate
            context_dict['message'] = "failure"
            return render(request,'seshdash/initial-login.html',context_dict)

        return render(request,'seshdash/main-dash.html',context_dict)

def prep_time_series(data,field_1_y,field_2_date,field_2_y=None):
    """
    Create time series data from model data to use for graphing
    """
    y_data = []
    y2_data = []
    x_data = []

    for point in data:
        y_data.append(getattr(point,field_1_y))
        if field_2_y:
            y_data.append(getattr(point,field_2_y))
        date = getattr(point,field_2_date)
        #havascript expets this in milliseconds multiply by 1000
        time_epoch = int(time_utils.get_epoch_from_datetime(date)) * 1000
        x_data.append(time_epoch)
    if field_2_y:
        return y_data,y2_data,x_data
    return y_data,x_data


#testing out some nvd3 graphs
#TODO move graphing functions to different library
def linebar(xdata,ydata,ydata2,label_1,label_2,chart_container,data):
    """
    lineplusbarchart page
    """
    #start_time = int(time.mktime(datetime.datetime(2012, 6, 1).timetuple()) * 1000)
    #nb_element = 100
    #xdata = range(nb_element)
    #xdata = map(lambda x: start_time + x * 1000000000, xdata)
    #ydata = [i + random.randint(1, 10) for i in range(nb_element)]
    #ydata2 = [i + random.randint(1, 10) for i in reversed(range(nb_element))]
    kwargs1 = {}
    kwargs1['bar'] = True

    tooltip_date = "%d %b %Y"
    extra_serie1 = {"tooltip": {"y_start": "wh ", "y_end": ""},
                    "date_format": tooltip_date}
    extra_serie2 = {"tooltip": {"y_start": "", "y_end": ""},
                    "date_format": tooltip_date}

    chartdata = {
        'x': xdata,
        'name1': label_1, 'y1': ydata, 'extra1': extra_serie1, 'kwargs1': kwargs1,
        'name2': label_2, 'y2': ydata2, 'extra2': extra_serie2,
    }

    charttype = "linePlusBarChart"
    chartcontainer = chart_container # container name
    data['charttype'] =  charttype
    data['chartdata'] =  chartdata
    data['chartcontainer'] = chartcontainer
    data['extra'] = {
            'x_is_date': True,
            'x_axis_format': '%d %b %Y %H',
            'tag_script_js': True,
            'jquery_on_ready': True,
            'focus_enable': True,
        }

    return  data


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
    context_data = {}
    context_data_json = {}
    if not user.has_perm('seshdash.view_Sesh_Site',site):
        print "user doesn't have permission to view site %s"%site_id
        #TODO return 403 permission denied
        return context_data,context_data_json
    context_data['sites'] = sites
    context_data['active_site'] = site
    context_data_json['sites'] = serialize_objects(sites)
    #get 5 days ago and 5 days in future for weather
    now = datetime.datetime.now()
    five_day_past = now - timedelta(days=5)
    five_day_future = now + timedelta(days=5)

    last_5_days = time_utils.get_last_five_days()

    weather_data = Site_Weather_Data.objects.filter(site=site,date__range=[five_day_past,five_day_future]).order_by('date')

    #granular pv data
    #power_data  = PV_Production_Point.objects.filter(site=site,time__range=[last_5_days[0],last_5_days[2]]).order_by('time')

    #daily pv data
    #power_data  = PV_Production_Point.objects.filter(site=site,time__range=[last_5_days[0],last_5_days[4]],data_duration=datetime.timedelta(days=1)).order_by('time')

    #BOM data

   # bom_data = BoM_Data_Point.objects.filter(site=site,time__range=[last_5_days[0],last_5_days[4]]).order_by('time')

    bom_data = BoM_Data_Point.objects.filter(site=site).order_by('-time')

    bom_data = BoM_Data_Point.objects.filter(site=site,time__range=[last_5_days[0],now]).order_by('-id')
    pprint( bom_data.first())

    #NOTE remvong JSON versions of data for now as it's not necassary
    #weather_data_json = serialize_objects(weather_data)
    #power_data_json = serialize_objects(power_data)
    #bom_data_json = serialize_objects(power_data)

    context_data['site_weather'] = weather_data
    #context_data['site_power'] = power_data
    context_data['bom_data'] = bom_data

    #NOTE remvong JSON versions of data for now as it's not necassary
    #context_data_json['site_weather'] = weather_data_json
    #context_data_json['site_power'] = power_data_json
    #context_data_json['bom_data'] = bom_data_json

    return context_data,context_data_json


def jsonify_dict(context_dict,content_json):
            #context_dict['weather_json'] = content_json['site_weather']
            #context_dict['power_json'] = content_json['site_power']
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

class UserList(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserDetail(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


def get_high_chart_data():
    # this the content object
     content_data = {}
    # Initializing Date
     now = datetime.datetime.now()
     five_day_past2 = now - timedelta(days=5)
     five_day_future2 = now + timedelta(days=6)
    # Queries and Data retreiving of the climate
     high_cloud_cover = Site_Weather_Data.objects.filter(date__range=[five_day_past2,five_day_future2]).values_list('cloud_cover', flat=True).order_by('date')
     content_data['high_cloud_cover']=high_cloud_cover
    # Queries and Data retreiving of the PV Production and Dates

     high_date = Site_Weather_Data.objects.filter(date__range=[five_day_past2,five_day_future2]).values_list('date', flat=True).order_by('date')
     high_date2 = []
     last_date=None
     high_pv_production =[]
     for elt in high_date:
        date1=elt.strftime("%d %B %Y")
        high_date2.append(date1)
        if last_date==None:
            last_date= elt

        pv_sum_day= BoM_Data_Point.objects.filter(time__range=[last_date,elt]).aggregate(pv_sum=Sum('pv_production'))
        last_date=elt

        pv_sum_day2 = pv_sum_day.get('pv_sum', 0)
        if pv_sum_day2 is None:
            pv_sum_day2 = 0

        high_pv_production.append(pv_sum_day2)
     content_data['high_date2']= high_date2
     content_data['high_pv_production']= high_pv_production
     print (content_data['high_pv_production'])
     return content_data
