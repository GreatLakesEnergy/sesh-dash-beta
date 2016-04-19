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
from django.forms import modelformset_factory, inlineformset_factory, formset_factory
from django.forms.models import model_to_dict
from django.contrib.auth.models import User
from django import forms

#Import Models and Forms
from seshdash.models import Sesh_Site,Site_Weather_Data, BoM_Data_Point,VRM_Account, Sesh_Alert,Sesh_RMC_Account, Daily_Data_Point
from django.db.models import Avg
from django.db.models import Sum
from seshdash.forms import SiteForm, VRMForm, RMCForm, SiteRMCForm

# Special things we need
from seshdash.utils import time_utils, rmc_tools
from pprint import pprint

#Import utils
from seshdash.utils.time_utils import get_timesince
from seshdash.utils.model_tools import get_model_first_reference
from datetime import timedelta
from datetime import datetime, date, time, tzinfo
from dateutil.relativedelta import relativedelta
import json,time,random,datetime

# Import for API
from rest_framework import generics, permissions
from seshdash.serializers import BoM_Data_PointSerializer, UserSerializer
from seshdash.api.victron import VictronAPI

# celery tasks
from seshdash.tasks import get_historical_BoM, generate_auto_rules

#generics
import logging


@login_required(login_url='/login/')
def index(request,site_id=0):
    """
    Initial user view user needs to be logged
    Get user related site data initially to display on main-dashboard view
    """
    sites =  _get_user_sites(request)

    context_dict = {}
    # Handle fisrt login if user has no site setup:
    if not sites:
           context_dict['VRM_form'] = _create_vrm_login_form()
           return render(request,'seshdash/initial-login.html',context_dict)

    if not site_id:
        #return first site user has action
        print "no site id recieved"
        site_id = sites[0].pk
    #Check if user has any sites under their permission
    context_dict, content_json = get_user_data(request.user,site_id,sites)

    context_dict = jsonify_dict(context_dict,content_json)
    #Generate date for dashboard  TODO use victron solar yield data using mock weather data for now
    y_data,x_data = prep_time_series(context_dict['site_weather'],'cloud_cover','date')
    y2_data,x2_data = prep_time_series(context_dict['site_weather'],'cloud_cover','date')
    #create graphs for PV dailt prod vs cloud cover

    # Create an object of the get_high_chart_date
    context_dict['high_chart']= get_high_chart_data(request.user,site_id,sites)
    context_dict['site_id'] = site_id

    return render(request,'seshdash/main-dash.html',context_dict)

def _create_vrm_login_form():
        #print "getting vrm form"
        # Simplt give the option first
        VRM_form = VRMForm()
        return VRMForm


def get_user_sites(vrm_user_id,vrm_password):
    """
    Import user sites from VRM
    """
    context_dict = {}
    site_list = []
    flatten_list = []
    v = VictronAPI(vrm_user_id,vrm_password)
    print 'getting suer sites'
    if v.IS_INITIALIZED:
            logging.debug("victron API is initialized ")
            sites = v.get_site_list()
            logging.info("Found sites %s "%sites)
            site_list.append(sites)
    if site_list:
        #make list of lists flat
        flatten_list = reduce(lambda x,y: x+y,site_list)
    context_dict['sites'] = flatten_list
    return context_dict


def _return_error_import( request, context_dict, form, message):
    """
    TODO Generalize this
    """
    #TODO
    context_dict['message'] = message
    context_dict['error'] = True
    context_dict['VRM_form'] = form
    return render(request,'seshdash/initial-login.html',context_dict)


@login_required
def import_site(request):
    """
    Initial login to gather VRM and Account information
    """
    context_dict = {}
    template = 'seshdash/initial-login.html'
    if request.method == "POST":
            #check if post is VRM Account form
            #print "got post"
            #print request.POST.keys()
            if request.POST.get('form_type',None) == 'vrm':
                print "got vrm form"
                form = VRMForm(request.POST)
                if not form.is_valid():
                    context_dict['VRM_form'] = form
                    context_dict['error'] = True
                    context_dict['message'] = 'Unable to add accout'
                if form.is_valid():
                    #print "form is vald"
                    site_list = get_user_sites(form['vrm_user_id'].value(),form['vrm_password'].value())
                    if not site_list['sites']:
                       # Error with credentials
                       return _return_error_import(request,context_dict,form,"check credentials")

                    context_dict['message'] = "success"
                    #do a psuedo save first we need to modify a field later
                    form = form.save(commit=False)
                    #now get user sites
                    context_dict['form_type'] = "vrm"
                    context_dict['site_list'] = site_list
                    context_dict['no_sites'] = len(site_list)
                    #modify field
                    form.number_of_sites = len(site_list)
                    #save for real
                    form.save()
                    #create initial data for formset
                    pre_pop_data = []
                    for site in site_list['sites']:
                        #get one and only vrm account
                        VRM = VRM_Account.objects.first()

                        site_model_form = {'site_name':site['name'],
                                            'vrm_site_id':site['idSite'],
                                            'has_genset': site['hasGenerator'],
                                            'vrm_account': VRM
                                            }
                        pre_pop_data.append(site_model_form)

                    site_forms_factory = inlineformset_factory(VRM_Account,Sesh_Site,
                            extra=len(site_list['sites']),form=SiteForm,
                            exclude=('vrm_account','rmc_account'),
                            can_delete= False)

                    context_dict['site_forms'] = site_forms_factory(initial = pre_pop_data,
                                                                    instance=VRM)
            else:
                # if RMC site
                # Handle RMC account info
                #print "rmc request recieved is rmc request getting form ready"
                site_forms_factory = inlineformset_factory(Sesh_RMC_Account,
                                                           Sesh_Site,
                                                           form=SiteRMCForm,
                                                           extra=1,
                                                           can_delete=False
                                                           )
                form = site_forms_factory()
                context_dict['site_forms'] = form
                context_dict['form_type'] = 'rmc'
    else:
        context_dict['VRM_form'] = _create_vrm_login_form()

    return render(request,template,context_dict)

def _download_data(request):
    """
    Trigger download of vrm upon loading site data
    """

    sites = _get_user_sites(request)
    for site in sites:
        if site.import_data:
            get_historical_BoM.delay(site.pk, time_utils.get_epoch_from_datetime(site.comission_date))

def _aggregate_imported_data(sites):
    for site in sites:
        aggregate_daily_data()

def _validate_form(form,context_dict):
    """
    Validate forms basedo no form input
    """
    if form.is_valid():
        form = form.save(commit=False)
        context_dict['error'] =  False

    else:
         context_dict['message'] = "failure creating site"
         context_dict['error'] = True
         context_dict['site_forms'] = form

    return context_dict,form

def _get_user_sites(request):
    """
    Helper function to get sites for user
    """
    # Get sites for use
    return  get_objects_for_user(request.user,'seshdash.view_Sesh_Site')


@login_required
def handle_create_site(request):
    """
    Handle parsing of RMC and VRM form and create models accordingly
    """
    context_dict = {}
    form = None
    if request.method == 'POST':
        if request.POST.get('form_type',None) == 'rmc':
            # Handle RMC form creation
            #print "checking rmc form"
            context_dict['form_type'] = 'rmc'
            form = _create_site_rmc(request)
        else:
            # Handle VRM form creation
            context_dict['form_type'] = 'vrm'
            #print "checking vrm form"
            form = _create_site_vrm(request)
            context_dict['form'] = form

    context_dict, valid_form = _validate_form(form,context_dict)
    print valid_form
    # Handle Form Errors
    if context_dict['error']:
        # Got Error return problem!
        # Delete VRM or RmC Account if this fails
        return render(request,'seshdash/initial-login.html',context_dict)

    for site in valid_form:
        # Initiate standard alarms
        generate_auto_rules(site.pk)

        # Finally
        site.save()

    # Initiate download if requred
    _download_data(request)


    return index(request)


def _create_site_rmc(request):
    """
    Create site for RMC account
    """
    rmc = Sesh_RMC_Account(api_key=rmc_tools.generate_rmc_api_key())
    rmc.save()
    site_forms_factory = inlineformset_factory(Sesh_RMC_Account, Sesh_Site, form=SiteRMCForm,exclude=('delete',))
    # Create RMC account associated with it
    form = site_forms_factory(request.POST, instance=rmc)
    return form


def _create_site_vrm(request):
    """
    Create the sites imported from VRM account
    """
    #TODO Bug allert!!  more than one VRM account will cause problem
    VRM = VRM_Account.objects.first()
    site_forms_factory = inlineformset_factory(VRM_Account,
            Sesh_Site,
            form=SiteForm,
            exclude=('delete',))
    form = site_forms_factory(request.POST, instance=VRM)
    return form

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
    """
    Logout user
    """
    logout(request)
    return render(request,'seshdash/logout.html')

def login_user(request):
    """
    Login motions for user logging into system
    """
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
            message = "Incorrect password"
            context_dict['error'] = message
            return render(request,'seshdash/login.html',context_dict)
    else:
            message = "Error user doesn't exist"
            context_dict['error'] = message
            return render(request,'seshdash/login.html',context_dict)


def get_user_data(user,site_id,sites):
    """
    Get site data for logged in user
    """
    site = Sesh_Site.objects.get(pk=site_id)
    context_data = {}
    context_data_json = {}
    if not user.has_perm('seshdash.view_Sesh_Site',site):
        #print "user doesn't have permission to view site %s"%site_id
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

    context_data['alerts'] = display_alerts(site_id)

    return context_data,context_data_json


def jsonify_dict(context_dict,content_json):
            #context_dict['weather_json'] = content_json['site_weather']
            #context_dict['power_json'] = content_json['site_power']
            context_dict['sites_json'] = content_json['sites']
            return context_dict

"""
BEGIN Turn django objects in JSON
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


"""
END
"""

def get_high_chart_data(user,site_id,sites):
     """
     This functimn  get_high_chart_data is help to get
     object to use in the High Chart Daily PV production and cloud cover
     """

     site = Sesh_Site.objects.get(pk=site_id)
     context_high_data = {}
     if not user.has_perm('seshdash.view_Sesh_Site',site):
        print "user doesn't have permission to view site %s"%site_id
        #TODO return 403 permission denied
        return context_high_data

     now = datetime.datetime.now()
     five_day_past2 = now - timedelta(days=5)
     five_day_future2 = now + timedelta(days=6)

    # Getting climat conditions

     high_cloud_cover = list(Site_Weather_Data.objects.filter(site=site,date__range=[five_day_past2,five_day_future2]).values_list('cloud_cover', flat=True).order_by('date'))
     context_high_data['high_cloud_cover']=high_cloud_cover

     # Getting climat Dates and the Pv Daily production
     # Getting  Dates  Site_Weather_Data is where i can find the date interval for dynamic initialization
     high_date = Site_Weather_Data.objects.filter(site=site,date__range=[five_day_past2,five_day_future2]).values_list('date', flat=True).order_by('date').distinct()
     high_date_data = []
     last_date=None
     high_pv_production =[]

     # extract date form high_pv_production  and give them a ready life time format , put it in list high_date_data
     for date in high_date:
        date_data=date.strftime("%d %B %Y")
        high_date_data.append(date_data)
        if last_date==None:
            last_date= date

        # Getting sum   Pv Production in the interval of 24 hours
        pv_sum_day= BoM_Data_Point.objects.filter(site=site,time__range=[last_date,date]).aggregate(pv_sum=Sum('pv_production'))
        last_date=date

        # extract pv sum value form pv_sum_day object   and put it in a list high_pv_production
        pv_sum_day_data = pv_sum_day.get('pv_sum', 0)
        if pv_sum_day_data is None:
            pv_sum_day_data = 0

        high_pv_production.append(pv_sum_day_data)


    # initiating the context_high_data Object
     context_high_data['high_date']= high_date_data
     context_high_data['high_pv_production']= high_pv_production
     print (context_high_data['high_pv_production'])
     return context_high_data

def display_alerts(site_id):
     alerts = Sesh_Alert.objects.filter(site=site_id, isSilence=False).order_by('-date')[:5]

     alert_list = []

     for alert in alerts:
          alert_list.append(alert)

     return alert_list

@login_required
def get_alerts(request):
    site_id = request.POST.get('site_id','')


    alerts = Sesh_Alert.objects.filter(site=site_id, isSilence=False).order_by('-date')[:5]

    alert_data = []


    # Loop to generate alert data
    for alert in alerts:
        alert_data.append({
            "alertId": alert.id,
            "site":alert.site.site_name,
            "alert":str(alert),
            "date":get_timesince(alert.date),
            })

    return HttpResponse(json.dumps(alert_data))

def display_alert_data(request):
    # Getting the clicked alert via ajax
    alert_id = request.POST.get("alertId",'')
    alert_id = int(alert_id)
    alert = Sesh_Alert.objects.filter(id=alert_id).first()

    alert_values = {}

    point = get_model_first_reference(alert.point_model, alert)

    alert_values = model_to_dict(point)

    # Converting time to json serializable value and changing it to timesince
    alert_values['time'] = get_timesince(alert_values['time'])

    return HttpResponse(json.dumps(alert_values))

def silence_alert(request):
    alert_id = request.POST.get("alertId", '')
    alerts = Sesh_Alert.objects.filter(id=alert_id)

    if len(alerts) >= 1:
       alert = alerts[0]
       alert.isSilence = True
       alert.save()
       return HttpResponse(True);
    else:
       return HttpResponse(False);


def get_latest_bom_data(request):
    latest_bom = BoM_Data_Point.objects.order_by('-time')[0]

    latest_bom_data = []
    latest_bom_data.append({"item": "State of Charge", "value":str(latest_bom.soc) + '%' })
    latest_bom_data.append({"item": "Battery Voltage", "value":latest_bom.battery_voltage})
    latest_bom_data.append({"item": "Consumption Data", "value":round(latest_bom.AC_output_absolute, 2)})
    latest_bom_data.append({"item": "Recent Contact", "value": get_timesince(latest_bom.time)})

    return HttpResponse(json.dumps(latest_bom_data))


@login_required
def historical_data(request):
    
    # If ajax request
    if request.method == 'POST': 
        sort_value = request.POST.get('sort_value', '')
        historical_data = get_historical_dict(column=sort_value)
        return HttpResponse(json.dumps(historical_data))
   
    # On page load
    else:
        sites = get_objects_for_user(request.user, 'seshdash.view_Sesh_Site')
        active_site = sites[0]
        context_dict = {}
        context_dict['sites'] = sites
        context_dict['site_id'] = 0
        context_dict['active_site'] = active_site
        return render(request, 'seshdash/historical-data.html', context_dict);


def get_alerts_for_year(site):
    """ Returns a json object containing the number of alerts for a year range """
 
    # NOTE: When using datetime object date_range does not include the last date
    now = datetime.datetime.now()
    year_before = now - relativedelta(years=1)
    number_of_alerts = Sesh_Alert.objects.filter(date__range=[
                                                             time_utils.get_date_dashed(year_before),\
							     time_utils.get_date_dashed(now)], site=site ).count()


    
    return number_of_alerts;
 
def get_avg_field_year(site, field):
    """ Returns the average of a field for a year range in Daily Data Point"""
    avg_field_yield = Daily_Data_Point.objects.filter(site=site)[:365].aggregate(Avg(field)).values()[0]
    return avg_field_yield

def get_historical_dict(column='daily_pv_yield'):
    unit = Daily_Data_Point.UNITS_DICTIONARY[column]
    print "The unit is: ",
    print unit
    sites = Sesh_Site.objects.all();
    historical_points = Daily_Data_Point.objects.all()
       
    historical_data = [];
    
      
    # For each site get Points
    for site in sites:
       historical_points = Daily_Data_Point.objects.filter(site=site.id)
       site_historical_data = []   
          
        # For point get neccessary Data
       for point in historical_points:
           site_historical_data.append({
               "date": time_utils.get_date_dashed(point.date),
               "count": getattr(point, column)
           })
          
       historical_data.append({
                               "site_id":site.id,
                               "site_name":site.site_name,
                               "site_historical_data": site_historical_data,
                               "data_unit": unit,
                               "number_of_alerts": get_alerts_for_year(site),
                               "average_pv_yield": get_avg_field_year(site, 'daily_pv_yield'),
                               "average_power_consumption_total": get_avg_field_year(site, 'daily_power_consumption_total')
                    })
    return historical_data

