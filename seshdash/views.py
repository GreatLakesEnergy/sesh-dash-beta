#Django libs
from django.shortcuts import render, get_object_or_404, render_to_response
from django.http import HttpResponseRedirect
from django.http import HttpResponseBadRequest
from django.core.urlresolvers import reverse
from django.views import generic
from django.views.decorators.http import require_GET
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.shortcuts import redirect
from guardian.core import ObjectPermissionChecker
from guardian.shortcuts import get_objects_for_user
from guardian.shortcuts import get_perms
from django.forms import modelformset_factory, inlineformset_factory, formset_factory
from django.forms.models import model_to_dict
from django.contrib.auth.models import User
from django.contrib.admin.views.decorators import staff_member_required
from django import forms
from django.db import OperationalError
from django.template.loader import get_template

#Guardian decorator
from guardian.decorators import permission_required_or_403

#Import Models and Forms
from seshdash.models import Sesh_Site,Site_Weather_Data, BoM_Data_Point,VRM_Account, Sesh_Alert,Sesh_RMC_Account, Daily_Data_Point, RMC_status
from django.db.models import Avg
from django.db.models import Sum

from seshdash.forms import SiteForm, VRMForm, RMCForm, SiteRMCForm, SensorEmonThForm,  \
                           SensorEmonTxForm, SensorBMVForm, SensorEmonPiForm, EditSiteForm, SiteVRMForm, \
                           AlertRuleForm, SeshUserForm, StatusCardForm

# Special things we need
from seshdash.utils import time_utils, rmc_tools, alert as alert_utils
import demjson

#Import utils
from seshdash.data.trend_utils import get_avg_field_year, get_alerts_for_year, get_historical_dict
from seshdash.utils.time_utils import get_timesince, get_timesince_influx, get_epoch_from_datetime
from seshdash.utils.model_tools import get_quick_status, get_model_first_reference, get_model_verbose,\
                                       get_measurement_verbose_name, get_measurement_unit,get_status_card_items,get_site_measurements, \
                                       associate_sensors_sets_to_site, get_all_associated_sensors, get_config_sensors, save_sensor_set, model_list_to_field_list

from seshdash.utils.reporting import get_report_table_attributes, get_edit_report_list
from seshdash.models import SENSORS_LIST

from datetime import timedelta
from datetime import datetime, date, time, tzinfo
from dateutil import parser
from dateutil.relativedelta import relativedelta
from seshdash.utils.permission_utils import get_permissions, get_org_edit_permissions

import json,time,random

# Import for API
from rest_framework import generics, permissions
from seshdash.serializers import BoM_Data_PointSerializer, UserSerializer
from seshdash.api.victron import VictronAPI

# celery tasks
from seshdash.tasks import get_historical_BoM, generate_auto_rules

#Import for Influx
from seshdash.data.db.influx import Influx, get_measurements_latest_point

#generics
import logging

#Autocomplete
from seshdash.models import *
import json
# Influxdb
from seshdash.data.db.influx import Influx


# Initializing the logger
logger = logging.getLogger(__name__)

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
        site_id = sites[0].pk
    #Check if user has any sites under their permission
    context_dict, content_json = get_user_data(request.user,site_id,sites)

    context_dict = jsonify_dict(context_dict,content_json)
    #Generate date for dashboard  TODO use victron solar yield data using mock weather data for now
    context_dict['site_id'] = site_id

    #Generating site measurements for a graph
    current_site = Sesh_Site.objects.filter(id = site_id).first()

    #getting site measurements
    site_measurements = get_site_measurements(current_site)
    measurements ={}

    for measurement in site_measurements:
        #getting verbose names
        measurement_verbose_name = get_measurement_verbose_name(measurement)
        measurements[measurement] = measurement_verbose_name
    context_dict['measurements']= measurements

    # status card form
    site = Sesh_Site.objects.filter(id=site_id).first()
    form = StatusCardForm(instance=site.status_card) 
    context_dict['status_form'] = form


    #sites witth weather and battery status
    sites_stats = get_quick_status(sites)
    context_dict['sites_stats'] = sites_stats

    # user permissions
    context_dict['permitted'] = get_org_edit_permissions(request.user)
    context_dict['user'] = request.user

    return render(request,'seshdash/main-dash.html',context_dict)

def _create_vrm_login_form():
        #print "getting vrm form"
        # Simplt give the option first
        VRM_form = VRMForm()
        return VRMForm


def get_user_sites(vrm_user_id, vrm_password):
    """
    Import user sites from VRM
    """

    context_dict = {}
    site_list = []
    flatten_list = []
    v = VictronAPI(vrm_user_id,vrm_password)

    if v.IS_INITIALIZED:
            logger.debug("victron API is initialized ")
            sites = v.get_site_list()
            logger.info("Found sites %s "%sites)
            site_list.append(sites)
    if site_list:
        #make list of lists flat
        flatten_list = reduce(lambda x,y: x+y,site_list)
    context_dict['sites'] = flatten_list
    return context_dict

def get_user_vrm_accounts(request):
    """
    get a list of vrm accouts attached to the user account
    """
    context_dict = {}
    vrm_accounts = get_objects_for_user(request.user,'seshdash.view_VRM_Accounts', klass=VRM_Account)
    context_dict['items'] = vrm_accounts
    context_dict['var_name'] = 'vrm_accounts'

    context_dict['verbose_name'] = VRM_Account._meta.verbose_name
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


def _create_vrm_site_forms(site_list, VRM_acc, context_dict, exclude=[]):
    """
    Create forms for site importation from VRM
    """

    if not site_list['sites']:
       # Error with credentials
       return _return_error_import(request,context_dict,form,"check credentials")

    #create initial data for formset
    pre_pop_data = []

    for site in site_list['sites']:
        #get one and only vrm account
        #  remove sites that are already in the sesh_site
        if not site['name'] in exclude:
            site_model_form = {'site_name':site['name'],
                                'vrm_site_id':site['idSite'],
                                'has_genset': site['hasGenerator'],
                                'vrm_account': VRM_acc
                                }
            pre_pop_data.append(site_model_form)

    # Create form factory
    site_forms_factory = inlineformset_factory(VRM_Account,Sesh_Site,
            extra=len(pre_pop_data),form=SiteForm,
            exclude=('vrm_account','rmc_account'),
            can_delete= False
            )
    site_forms_factory = site_forms_factory(initial = pre_pop_data)
    context_dict['site_forms'] = site_forms_factory
    return  context_dict

@login_required
def import_site_account(request):
    context_dict = {}
    exclude_list = model_list_to_field_list(_get_user_sites(request),'site_name')
    if request.method == 'GET':

        vrm_account = get_object_or_404(VRM_Account,pk=request.GET.get('vrm_account',''))
        site_list = get_user_sites(vrm_account.vrm_user_id, vrm_account.vrm_password)
        context_dict = _create_vrm_site_forms(
                    site_list,
                    vrm_account,
                    context_dict,
                    exclude = exclude_list
                    )

        # exclude already existing sites from list
        context_dict['form_type'] = 'vrm'
        return render(request, 'seshdash/initial-login.html', context_dict)

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
            if request.POST.get('form_type',None) == 'vrm':
                form = VRMForm(request.POST)
                if not form.is_valid():
                    context_dict['VRM_form'] = form
                    context_dict['error'] = True
                    context_dict['message'] = 'Unable to add account'
                if form.is_valid():
                    # Fake save our vrm account so we can add number of sites to it
                    form.save(commit=False)
                    site_list = get_user_sites(form['vrm_user_id'].value(),form['vrm_password'].value())
                    form.number_of_sites = len(site_list)
                    form.save()
                    vrm_acc = VRM_Account.objects.get(vrm_user_id=form['vrm_user_id'].value())
                    VRM = VRM_Account.objects.get(vrm_user_id=form['vrm_user_id'].value())
                    # generate site forms based on data from vrm
                    context_dict = _create_vrm_site_forms(site_list, VRM, context_dict)
                    # add some messages
                    context_dict['message'] = "success"
                    #now get user sites
                    context_dict['form_type'] = "vrm"
                    context_dict['site_list'] = site_list
                    context_dict['no_sites'] = len(site_list)

            else:
                # if RMC site
                # Handle RMC account info
                #print "rmc request recieved is rmc request getting form ready"
                site_forms_factory = modelformset_factory( Sesh_Site,
                                                           form=SiteRMCForm,
                                                           extra=1,
                                                           can_delete=False
                                                           )
                form = site_forms_factory()
                context_dict['site_forms'] = form
                context_dict['form_type'] = 'rmc'
    else:
        context_dict['VRM_form'] = _create_vrm_login_form()

    return render(request,'seshdash/initial-login.html',context_dict)

def _download_data(request):
    """
    Trigger download of vrm upon loading site data
    """

    sites = _get_user_sites(request)
    for site in sites:
        if site.import_data:
            site_id = site.pk
            get_historical_BoM.delay(site_id, time_utils.get_epoch_from_datetime(site.comission_date))

def _aggregate_imported_data(sites):
    """
    Run aggregations on daily data
    """
    for site in sites:
        aggregate_daily_data()

def _validate_form(form,context_dict):
    """
    Validate forms basedo no form input
    """
    if form.is_valid():
        logger.debug("getting ready to save form %s")
        form = form.save(commit=False)
        context_dict['error'] =  False

    else:
         context_dict['message'] = "failure creating site"
         context_dict['error'] = True
         context_dict['site_forms'] = form

    return context_dict,form

def _get_user_sites(request, site_type='all'):
    """
    Helper function to get sites for user
    type = all, vrm, rmc
    """
    # Get sites for use

    sites = Sesh_Site.objects.filter(organisation=request.user.organisation)
    if site_type == 'vrm':
        sites = sites.filter(vrm_site_id__isnull=False)
    elif site_type == 'rmc':
        sites = sites.filter(vrm_site_id__isnull=True)
    else:
        return sites



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
    # Handle Form Errors
    if context_dict['error']:
        # Got Error return problem!
        # Delete VRM or RmC Account if this fails
        return render(request,'seshdash/initial-login.html',context_dict)

    for site in valid_form:
        # Finally
        site.save()

        # Initiate standard alarms
        generate_auto_rules(site.pk)

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
    logger.debug("Getting VRM m2m object %s"%VRM)
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
    return render(request,'seshdash/login.html')

def login_user(request):
    """
    Login motions for user logginng into system
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
    now = timezone.localtime(timezone.now())
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

"""
class UserList(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserDetail(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
"""


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
        #TODO return 403 permission denied
        return context_high_data

     now = timezone.localtime(timezone.now())
     five_day_past2 = now - timedelta(days=5)
     five_day_future2 = now + timedelta(days=6)

    # Getting climat conditions

     #high_cloud_cover = list(Site_Weather_Data.objects.filter(site=site,date__range=[five_day_past2,five_day_future2]).values_list('cloud_cover', flat=True).order_by('date'))
     #context_high_data['high_cloud_cover']=high_cloud_cover

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



@login_required
def get_notifications_alerts(request):

    sites =_get_user_sites(request)

    arr = []


    for site in sites:
        if(Sesh_Alert.objects.filter(isSilence=False ,site=site).count() != 0):
              arr.append({
                "site":site.site_name,
                "counter":Sesh_Alert.objects.filter(isSilence=False,site=site).count(),
                "site_id":site.id,
                })

    return HttpResponse(json.dumps(arr))


@login_required
def display_alert_data(request):
    # Getting the clicked alert via ajax
    alert_id = request.POST.get("alertId",'')

    if alert_id.isdigit():
        alert = Sesh_Alert.objects.filter(id=alert_id).first()
    else:
        raise Exception("Invalid alert id, alert id is not an integer")

    alert_values = {}
    point = alert_utils.get_alert_point(alert)

    if point:
        """
        If the point is from influx it comes as a dict
        if the point is from an sql db it comes as a model that needs to
        be converted to a dict
        """
        if type(point) != dict:
            alert_values = model_to_dict(point)
        else:
            alert_values = point

        # If the the time is from influx then we convert it to a python datetime
        if type(alert_values['time'])  == unicode:
            alert_values['time'] = parser.parse(alert_values['time'])

        alert_values['time'] = get_timesince(alert_values['time'])

        # Setting the id to the alert id (NEEDED FOR SILENCING ALERTS)
        alert_values['id'] =  alert_id
        return HttpResponse(json.dumps(alert_values))

    else:
        # Handling unecpexted data failure
        raise Exception("The alert has not related point,")

@login_required
def silence_alert(request):
    """
    View for silencing alerts
    """
    alert_id = request.POST.get("alert_id", '')

    if alert_id.isdigit():
        alert = Sesh_Alert.objects.filter(id=alert_id).first()
    else:
        raise Exception("In SILENCING ALERT, The alert id is not an integer and the value is %s" % alert_d)


    if alert:
        alert.isSilence = True
        alert.save()
        return HttpResponse(True);
    else:
        raise Exception("IN SILENCING ALERT, The alert id is an integer and is %s but has no corresponding alert" % alert_id)


@login_required
def get_latest_bom_data(request):
    """
    Returns the latest information of a site to be displayed in the status card
    The data is got from the influx db
    """
    # getting current site and latest rmc status object
    site_id = request.POST.get('siteId')
    site = Sesh_Site.objects.filter(id=site_id).first()

    # The measurement list contains attributes to be displayed in the status card,
    measurement_list = get_status_card_items(site)

    if measurement_list != 0:
        latest_points = get_measurements_latest_point(site, measurement_list)

        latest_point_data = []

        # If the points exist and the points returned are equal to the items in measurement list
        for measurement, point in latest_points.items():
            latest_point_data.append({"item":get_measurement_verbose_name(measurement),
                                      "value":str(round(latest_points[measurement]['value'], 2))
                                              + get_measurement_unit(measurement)
                             })

        if 'last_contact' in measurement_list:
            # Adding the last contact from the rmc status
            rmc_latest = RMC_status.objects.filter(site=site).last()
            if rmc_latest:
                last_contact = rmc_latest.minutes_last_contact
                last_contact_seconds = last_contact * 60
                last_contact = time_utils.format_timesince_seconds(last_contact_seconds)
                latest_point_data.append({"item":"Last Contact", "value": last_contact})
            else:
                logger.debug("No rmc_status points for site ")

        return HttpResponse(json.dumps(latest_point_data))

   # Requesting all site names and site id from the database


@login_required
def search(request):

    data=[]
    # Getting all user sites
    sites = _get_user_sites(request)
    for site in sites:
        data.append({"key":site.id,"value":site.site_name})
    return HttpResponse(json.dumps(data))

@login_required
def historical_data(request):
    # If ajax request
    if request.method == 'POST':
        sort_value = request.POST.get('sort_value', '')
        historical_data = get_historical_dict(column=sort_value)
        return HttpResponse(json.dumps(historical_data))

    # On page load
    else:
        sort_data_dict = get_model_verbose(Daily_Data_Point)
        # Removing values that are not data historical values
        sort_data_dict.pop('id')
        sort_data_dict.pop('site')
        sort_data_dict.pop('date')


        #sites = get_objects_for_user(request.user, 'seshdash.view_Sesh_Site')
        sites =  _get_user_sites(request)
        active_site = sites[0]
        context_dict = {}

        #sites witth weather and battery status
        user_sites =  sites
        sites_stats = get_quick_status(user_sites)
        context_dict['sites_stats'] = sites_stats

        #checking user permissions
        user = request.user
        permission = get_permissions(user)
        context_dict['permitted'] = get_org_edit_permissions(user)

        context_dict['sites'] = sites
        context_dict['site_id'] = 0
        context_dict['active_site'] = active_site
        context_dict['sort_keys'] = sort_data_dict.keys()
        context_dict['sort_dict'] = sort_data_dict
        return render(request, 'seshdash/data_analysis/historical-data.html', context_dict);


@require_GET
@login_required
def graphs(request):
    """
    Returns json, containing data that is used in data analysis graphs
    """
    results = []

    # Getting values from Post request
    time = request.GET.get('time', '') # This is the time range it has to be: 24h, 7d or 30d
    choices = request.GET.getlist('choice[]')
    active_id = request.GET.get('active_site_id', None)
    start_time = request.GET.get('start_time', datetime.now() - timedelta(weeks=1))
    end_time = request.GET.get('end_time', datetime.now())
    resolution = request.GET.get('resolution', '1h')
    current_site = Sesh_Site.objects.filter(id=active_id).first()


    if (not current_site) or current_site.organisation != request.user.organisation:
        return HttpResponseBadRequest("Invalid site id, No site was found for the given site id")

    time_delta_dict = {'24h':{'hours':24},
                       '7d': {'days':7},
                       '30d':{'days':30},
                    }

    time_bucket_dict = {'24h':'1h',
                        '7d':'1d',
                        '30d':'5d',
                    }
    if start_time and end_time:
        start_time = datetime.strptime(start_time, "%Y-%m-%d")
        end_time = datetime.strptime(end_time, "%Y-%m-%d")
    else:
        start_time = datetime.now() - timedelta(weeks=1)
        end_time = datetime.now()


    # processing post request values to be used in the influx queries
    for choice in choices:
        choice_dict = {}
        choice_dict['measurement'] = choice
        #time_delta = time_delta_dict[time]
        #time_bucket= time_bucket_dict[time]
        choice_dict['si_unit'] = get_measurement_unit(choice)

        # Gettting the values of the given element
        client = Influx()

        query_results = client.get_measurement_range_bucket(choice, start_time, end_time, group_by=resolution)


        #looping into values
        choice_data = []
        for result in query_results:
            choice_data_dict = {}
            result_time = parser.parse(result['time'])
            result_time = get_epoch_from_datetime(result_time)
            if result['mean'] is not None:
                result_value = round(result['mean'], 2)
            else:
                result_value = 0
            choice_data_dict['time'] = result_time
            choice_data_dict['value'] = result_value
            choice_data.append([result_time, result_value])


        choice_dict['data'] = choice_data
        results.append(choice_dict)

    return HttpResponse(json.dumps(results))


#function to editing existing sites
@login_required
@permission_required_or_403('auth.view_Sesh_Site')
def edit_site(request,site_Id=1):
    context_dict = {}
    site = get_object_or_404(Sesh_Site, id=site_Id)
    rmc_account = Sesh_RMC_Account.objects.filter(site=site).first();

    # If it is an rmc site create a rmc_form
    if rmc_account:
        site_form = SiteRMCForm(instance=site)
        rmc_form = RMCForm(instance=rmc_account)
        context_dict['RMCForm'] = rmc_form
    else:
        site_form = SiteVRMForm(instance=site)


    if request.method == 'POST':
        if rmc_account:
            site_form = SiteRMCForm(request.POST, instance=site)
            rmc_form = RMCForm(request.POST, instance=rmc_account)

            if site_form.is_valid() and rmc_form.is_valid():
                site_form.save()
                rmc_form.save()
            context_dict['RMCForm'] = rmc_form
        else:
            site_form = SiteVRMForm(request.POST, instance=site)
            if site_form.is_valid():
                site_form.save()


    user_sites = _get_user_sites(request)
    context_dict['VRM_form'] = VRMForm()
    context_dict['site_form']= site_form
    context_dict['sites']= user_sites
    context_dict['permitted'] = get_org_edit_permissions(request.user)
    context_dict['sites_stats'] = get_quick_status(user_sites)
    return render(request,'seshdash/settings/site_settings.html', context_dict)


@login_required
@permission_required_or_403('auth.view_Sesh_Site')
def site_add_edit(request):
    """
    This views renders the page for editing and
    adding new rmc sites
    """
    context_dict = {}
    sites = _get_user_sites(request)
    context_dict['sites_stats'] = get_quick_status(sites)
    context_dict['sites'] = sites
    context_dict['permitted'] = get_org_edit_permissions(request.user)
    user_vrm_accounts = (get_user_vrm_accounts(request))
    context_dict['has_vrm'] = False
    if user_vrm_accounts.get('items',''):
        context_dict.update(get_user_vrm_accounts(request)) # Add user VRM accounts
        context_dict['has_vrm'] = True
        context_dict['var_url'] = 'import-site-account' # for link generation on list
        context_dict['param'] = 'vrm_account' # for link generation on list

    else:
        context_dict['VRM_form'] = _create_vrm_login_form()


    return render(request, 'seshdash/settings/site_settings.html', context_dict)



@login_required
def settings_alert_rules(request):
    """
    To allow users to manage alert
    rules for given sites
    """
    context_dict = {}
    sites = _get_user_sites(request)

    user_sites = _get_user_sites(request)
    context_dict['permitted'] = get_org_edit_permissions(request.user)
    context_dict['sites_stats'] = get_quick_status(user_sites)
    context_dict['sites'] = sites
    return render(request, 'seshdash/settings/sites_alert_rules.html', context_dict)

@login_required
@permission_required_or_403('auth.view_Sesh_Site')
def site_alert_rules(request, site_id):
    """
    Alert rules for a given site
    """

    context_dict = {}
    site = Sesh_Site.objects.filter(id=site_id).first()
    alert_rules = Alert_Rule.objects.filter(site=site)
    form = AlertRuleForm()



    if request.method == 'POST':
        form = AlertRuleForm(request.POST)
        if form.is_valid():
            alert_rule = form.save(commit=False)
            alert_rule.site = site
            alert_rule.save()
            return redirect(reverse('site_alert_rules', args=[site.id]))


    context_dict['form'] = form
    context_dict['site'] = site
    context_dict['alert_rules'] = alert_rules
    user_sites = _get_user_sites(request)
    context_dict['permitted'] = get_org_edit_permissions(request.user)
    context_dict['sites_stats'] = get_quick_status(user_sites)
    return render(request, 'seshdash/settings/alert_rules.html', context_dict)


@login_required
@permission_required_or_403('auth.view_Sesh_Site')
def edit_alert_rule(request, alert_rule_id):
    """
    Editing alert rules for a given alert rule id
    """
    context_dict = {}
    alert_rule = Alert_Rule.objects.filter(id=alert_rule_id).first()
    form = AlertRuleForm(instance=alert_rule)

    if request.method == 'POST':
        form = AlertRuleForm(request.POST, instance=alert_rule)
        if form.is_valid():
            form.save()
            return redirect(reverse('site_alert_rules', args=[alert_rule.site.id]))


    context_dict['form'] = form
    return render(request, 'seshdash/settings/edit_alert_rule.html', context_dict)


@login_required
@permission_required_or_403('auth.view_Sesh_Site')
def delete_alert_rule(request, alert_rule_id):
    """
    Deleting an alert rule
    """
    alert_rule = Alert_Rule.objects.filter(id=alert_rule_id).first()
    site_id = alert_rule.site.id
    alert_rule.delete()
    return redirect(reverse('site_alert_rules', args=[site_id]))


# function of adding new site
@login_required
@permission_required_or_403('auth.view_Sesh_Site')
def add_rmc_site(request):
    """
    This adds an rmc site to
    the database
    """
    context_dict = {}

    if request.method == 'POST':
        form = SiteRMCForm(request.POST)

        if form.is_valid():
            form = form.save()
            return HttpResponseRedirect(reverse('add_rmc_account', args=[form.id]))

    else:
        form = SiteRMCForm()

    context_dict['form'] = form
    return render(request, 'seshdash/add_rmc_site.html', context_dict)



@login_required
@permission_required_or_403('auth.view_Sesh_Site')
def add_rmc_account(request, site_id):
    """
    This view is for adding a new rmc account
    to the database and associate it with a site
    """
    site = Sesh_Site.objects.filter(id=site_id).first()

    # sensors formset factories
    emonThFormSetFactory = formset_factory(SensorEmonThForm)
    emonTxFormSetFactory = formset_factory(SensorEmonTxForm)
    bmvFormSetFactory = formset_factory(SensorBMVForm)

    # formsets
    emonth_form_set = emonThFormSetFactory(prefix="emonth")
    emontx_form_set = emonTxFormSetFactory(prefix="emontx")
    bmv_form_set = bmvFormSetFactory(prefix="bmv")

    # emonpi form
    site_emonpi = Sensor_EmonPi.objects.filter(site=site).first()
    emonpi_form = SensorEmonPiForm(prefix='emonpi', instance=site_emonpi)

    context_dict = {}
    rmc_form = RMCForm()

    if request.method == 'POST':

        rmc_form = RMCForm(request.POST)
        emonpi_form = SensorEmonPiForm(request.POST, prefix='emonpi', instance=site_emonpi)
        emonth_form_set = emonThFormSetFactory(request.POST, prefix="emonth")
        emontx_form_set = emonTxFormSetFactory(request.POST, prefix="emontx")
        bmv_form_set = bmvFormSetFactory(request.POST, prefix="bmv")

        sensors_sets =  [emonth_form_set, emontx_form_set, bmv_form_set]

        if rmc_form.is_valid():
            rmc_account = rmc_form.save(commit=False)
            rmc_account.site = site
            rmc_account.save()
            associate_sensors_sets_to_site(sensors_sets, site)
            if emonpi_form.is_valid():
                emonpi_form.save()

            return redirect('index')


    context_dict['rmc_form'] = rmc_form
    context_dict['emonpi_form'] = emonpi_form
    context_dict['site_id'] = site_id
    context_dict['sensors_list'] = SENSORS_LIST
    context_dict['emonth_form'] = emonThFormSetFactory(prefix="emonth")
    context_dict['emontx_form'] = emonTxFormSetFactory(prefix="emontx")
    context_dict['bmv_form'] = bmvFormSetFactory(prefix="bmv")
    return render(request, 'seshdash/add_rmc_account.html', context_dict)


def get_rmc_config(request):
    """
    View to return the config file for a given rmc given
    an api key for the rmc account
    """
    context_dict = {}
    api_key = request.GET.get('api_key', '')
    context_dict['api_key'] = api_key

    rmc_account = Sesh_RMC_Account.objects.filter(api_key=api_key).first()

    if not rmc_account:
        logger.debug("There is no rmc account associated with the api key")
        logger.debug("Make sure you rmc site is configured on the server")
        return HttpResponseForbidden()

    site = rmc_account.site
    associated_sensors = get_all_associated_sensors(site)

    configuration, bmv_number = get_config_sensors(associated_sensors)
    context_dict['configuration']  = configuration
    context_dict['bmv_number'] = bmv_number

    conf = get_template('seshdash/configs/rmc_config.conf')

    return HttpResponse(conf.render(context_dict), content_type='text/plain')


@staff_member_required
def user_notifications(request):
    """
    Renders page to display users of an organization
    and their values to view the sites
    """
    context_dict = {}
    user = request.user

    organisation_users = Sesh_User.objects.filter(organisation=user.organisation) # all users belonging to the same organisations
    SeshUserFormSetFactory = modelformset_factory(Sesh_User, fields=('on_call', 'send_mail', 'send_sms',), extra=0)
    sesh_user_formset = SeshUserFormSetFactory(queryset=organisation_users)

    if request.method == 'POST':
        sesh_user_formset = SeshUserFormSetFactory(request.POST, queryset=organisation_users)
        if sesh_user_formset.is_valid():
            sesh_user_formset.save()
            return redirect('index')

    user_sites = _get_user_sites(request)
    context_dict['permitted'] = get_org_edit_permissions(request.user)
    context_dict['sites_stats'] = get_quick_status(user_sites)
    context_dict['user_formset'] = sesh_user_formset
    return render(request, 'seshdash/settings/user_notifications.html', context_dict)

@login_required
def manage_org_users(request):
    """
    View to manage the users of an organisation
    Should only be accessed by admin users of the organisation
    """
    if request.user.is_org_admin:
        context_dict = {}
        context_dict['organisation_users'] = request.user.organisation.get_users()
        context_dict['form'] = SeshUserForm()
        user_sites = _get_user_sites(request)
        context_dict['permitted'] = get_org_edit_permissions(request.user)
        context_dict['sites_stats'] = get_quick_status(user_sites)
        return render(request, 'seshdash/settings/organisation_users.html', context_dict)
    else:
        return HttpResponseForbidden()

@login_required
def add_sesh_user(request):
    """
    View for adding a new sesh user
    user should be an organisation admin
    """
    if request.user.is_org_admin:
        if request.method == 'POST':
            form = SeshUserForm(request.POST)
            if form.is_valid():
                user = form.save(commit=False)
                user.organisation = request.user.organisation
                user.save()
                return redirect('manage_org_users')
        else:
            return HttpResponseForbidden()
    else:
        return HttpResponseForbidden()


@login_required
def delete_sesh_user(request, user_id):
     """
     Deletes a sesh User
     the user to access the view should be an admin of the organisation
     """

     if request.user.is_org_admin:
         user = Sesh_User.objects.filter(id=user_id).first()
         user.delete()
         return redirect('manage_org_users')
     else:
         return HttpResponseForbidden()

@login_required
def edit_sesh_user(request, user_id):
    """
    Edits a sesh user
    the user loged in should be an admin of the organisation
    """
    if request.user.is_org_admin:
        context_dict = {}
        user = Sesh_User.objects.filter(id=user_id).first()
        form = SeshUserForm(instance=user)

        if request.method == 'POST':
            form = SeshUserForm(request.POST, instance=user)
            if form.is_valid():
                form.save()
                return redirect('manage_org_users')

        user_sites = _get_user_sites(request)
        context_dict['form'] = form
        context_dict['permitted'] = get_org_edit_permissions(request.user)
        context_dict['sites_stats'] = get_quick_status(user_sites)
        return render(request, 'seshdash/settings/edit_sesh_user.html', context_dict)
    else:
        return HttpResponseForbidden()


@login_required
def manage_reports(request, site_id):
    """
    Manages reports for a given site
    """
    context_dict = {}
    site = Sesh_Site.objects.filter(id=site_id).first()
    reports = Report_Job.objects.filter(site=site)

    context_dict['site'] = site
    context_dict['reports'] = reports
    return render(request, 'seshdash/settings/manage_reports.html', context_dict)


@login_required
def add_report(request, site_id):
    """
    View to help in managing the reports
    """
    site = Sesh_Site.objects.filter(id=site_id).first()
    context_dict = {}
    context_dict['report_attributes'] = get_report_table_attributes()
    attributes = []

    # if the user does not belong to the organisation or if the user is not an admin
    if not(request.user.organisation == site.organisation and request.user.is_org_admin):
        return HttpResponseForbidden()

    if request.method == "POST":
        # Getting all the checked report attribute values
        for key, value in request.POST.items():
            if value == 'on':
                attributes.append(demjson.decode(key))

        Report_Job.objects.create(site=site,
                              attributes=attributes,
                              duration=request.POST.get('duration', 'daily'),
                              day_to_report=0)
        return redirect(reverse('manage_reports', args=[site.id]))

    return render(request, 'seshdash/settings/add_report.html', context_dict)


@login_required
def edit_report(request, report_id):
    """
    View to edit a report given,
    a report id as an parameter
    """
    context_dict = {}
    report = Report_Job.objects.filter(id=report_id).first()
    attribute_list = []

    if request.method == 'POST':
        for key, value in request.POST.items():
            if value == 'on':
                attribute_list.append(demjson.decode(key))

        report.attributes = attribute_list
        report.duration = request.POST['duration']
        report.save()
        return redirect(reverse('manage_reports', args=[report.site.id]))

    context_dict['attributes'] = get_edit_report_list(report)
    context_dict['report'] = report
    context_dict['duration_choices'] = report.get_duration_choices()
    return render(request, 'seshdash/settings/edit_report.html', context_dict)



@login_required
def delete_report(request, report_id):
    """
    View to delete a report
    """
    context_dict = {}
    report = Report_Job.objects.filter(id=report_id).first()
    site = report.site
    report.delete()
    return redirect(reverse('manage_reports', args=[site.id]))


def export_csv_measurement_data(request):
    """
    Returns a csv of a given measurement a request

    """
    import csv
    context_dict = {}
    measurement = request.POST.get('measurement', '')
    start_time = request.POST.get('start-time', None)
    end_time = request.POST.get('end-time', None)
    site_name = request.POST.get('site-name', '')

    site = Sesh_Site.objects.filter(site_name=site_name).first()

    if request.method == 'POST':
        # Converting strings to date
        start_time = datetime.strptime(start_time, '%Y-%m-%d')
        end_time = datetime.strptime(end_time, '%Y-%m-%d')

        i = Influx()

        results = i.get_measurement_range(measurement, start_time, end_time, site=site)

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="%s.csv"' % ( site.site_name + '_' + measurement + '_sesh')
        writer = csv.DictWriter(response, ['site_name', 'time', 'value'])

        writer.writeheader()
        for result in results:
            del result['source']
            writer.writerow(result)

        return response

    i = Influx()
    user_sites = _get_user_sites(request)
    context_dict['sites'] = user_sites
    context_dict['measurements'] = i.get_measurements()
    context_dict['permitted'] = get_org_edit_permissions(request.user)
    context_dict['sites_stats'] = get_quick_status(user_sites)
    return render(request, 'seshdash/data_analysis/export-csv.html', context_dict)


@login_required
def edit_status_card(request, site_id):
    """
    Edits the status card of a site
    """
    context_dict = {}
    site = Sesh_Site.objects.filter(id=site_id).first()
    form = StatusCardForm(instance=site.status_card)

    if request.method == 'POST':
        if request.user.is_org_admin:
            form = StatusCardForm(request.POST, instance=site.status_card)
            if form.is_valid():
                status_card = form.save()
                return redirect(reverse('index', args=[site.id]))
        else:
            return HttpResponseBadRequest("You can not edit the status card, You are not and admin of your organisation")
