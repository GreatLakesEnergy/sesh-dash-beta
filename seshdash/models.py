from django.contrib.auth.models import User, Group
from django.db import models
from datetime import timedelta
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.contrib import admin
from django.contrib.auth.models import AbstractUser
from geoposition.fields import GeopositionField
from django.utils import timezone

from django.core.exceptions import ValidationError

from django_mysql.models import JSONField

from seshdash.data.db.kapacitor import Kapacitor

# Create your models here.
class VRM_Account(models.Model):
    """
    seperating VRM account for simplicity
    """
    vrm_user_id = models.CharField(max_length=100,default="",primary_key=True)
    vrm_password = models.CharField(max_length=100,default="")
    number_of_sites = models.IntegerField(default=0)

    def __str__(self):
        return self.vrm_user_id


    class Meta:
        verbose_name = 'VRM Account'
        verbose_name_plural = 'VRM Accounts'
        permissions = (
            ('view_VRM_Accounts', 'View VRM Acccount'),
        )


class Sesh_Organisation(models.Model):
    name = models.CharField(max_length=40)
    send_slack = models.BooleanField(default=False)
    slack_token = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.name

    def get_users(self):
        return Sesh_User.objects.filter(organisation=self)

class Sesh_User(AbstractUser):
    """
    In creating Sesh_User instances,
    Always remember to user create_user instead of create,
    Sesh_User.objects.create_user
    """
    department = models.CharField(max_length=100)
    organisation = models.ForeignKey(Sesh_Organisation, null=True)
    is_org_admin = models.BooleanField(default=False)
    phone_number =  models.CharField(max_length=12, blank=True, null=True)
    on_call = models.BooleanField(default=False)
    send_mail = models.BooleanField(default=False)
    send_sms = models.BooleanField(default=False)

    def __str__(self):
        return self.username


    class Meta:
         verbose_name = 'User'
         verbose_name_plural = 'Users'


class Slack_Channel(models.Model):
    organisation = models.ForeignKey(Sesh_Organisation, related_name='slack_channel')
    name = models.CharField(max_length=40)
    is_alert_channel = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Status_Card(models.Model):
     """
     Contains the rows to be displayed in the
     status card
     """

     ROW_CHOICES = (
         ('AC_Load_in', 'AC Load in'),
         ('AC_Load_out', 'AC Load out'),
         ('AC_Voltage_in', 'AC Voltage in'),
         ('AC_Voltage_out', 'AC Voltage out'),
         ('AC_input', 'AC input'),
         ('AC_output', 'AC output' ),
         ('AC_output_absolute', 'AC output absolute'),
         ('battery_voltage', 'Battery Voltage'),
         ('genset_state', 'Genset state'),
         ('main_on', 'Main on'),
         ('pv_production', 'PV production'),
         ('relay_state', 'Relay state'),
         ('soc', 'State of Charge'),
         ('trans', 'Trans'),
         ('last_contact', 'Last Contact'),
     )


     row1 = models.CharField(max_length=30, choices=ROW_CHOICES, default='soc')
     row2 = models.CharField(max_length=30, choices=ROW_CHOICES, default='battery_voltage')
     row3 = models.CharField(max_length=30, choices=ROW_CHOICES, default='AC_output_absolute')
     row4 = models.CharField(max_length=30, choices=ROW_CHOICES, default='last_contact')


     def __str__(self):
         return "For site: " + self.sesh_site.site_name


class Site_Measurements(models.Model):
    """
    Contains measurements to be displayed in graphs dropdowns
    """
    ROW_CHOICES = (
         ('AC_Load_in', 'AC Load in'),
         ('AC_Load_out', 'AC Load out'),
         ('AC_Voltage_in', 'AC Voltage in'),
         ('AC_Voltage_out', 'AC Voltage out'),
         ('AC_input', 'AC input'),
         ('AC_output', 'AC output' ),
         ('AC_output_absolute', 'AC output absolute'),
         ('battery_voltage', 'Battery Voltage'),
         ('genset_state', 'Genset state'),
         ('main_on', 'Main on'),
         ('pv_production', 'PV production'),
         ('relay_state', 'Relay state'),
         ('soc', 'State of Charge'),
         ('trans', 'Trans'),
         ('cloud_cover', 'Cloud Cover'),
         ("daily_battery_charge","Daily Battery Charge"),
         ("daily_grid_outage_n", "Daily Grid Outage N"),
         ("daily_grid_outage_t", "Daily Grid Outage T"),
         ("daily_grid_usage", "Daily Grid Usage"),
         ("daily_no_of_alerts", "Daily Number of Alerts"),
         ("daily_power_cons_pv", "Daily Power Cons Pv"),
         ("daily_power_consumption_total", "Daily Power Consumption Total"),
         ("daily_pv_yield", "Daily Pv Yield"),
    )

    row1 = models.CharField(max_length=30, choices=ROW_CHOICES,  default='soc')
    row2 = models.CharField(max_length=30, choices=ROW_CHOICES,  default='battery_voltage')
    row3 = models.CharField(max_length=30, choices=ROW_CHOICES,  default='AC_output_absolute')
    row4 = models.CharField(max_length=30, choices=ROW_CHOICES,  default='AC_Load_in')
    row5 = models.CharField(max_length=30, choices=ROW_CHOICES,  default='AC_Load_out')
    row6 = models.CharField(max_length=30, choices=ROW_CHOICES,  default='AC_Voltage_in')
    row7 = models.CharField(max_length=30, choices=ROW_CHOICES,  default='AC_Voltage_out')
    row8 = models.CharField(max_length=30, choices=ROW_CHOICES,  default='AC_input')
    row9 = models.CharField(max_length=30, choices=ROW_CHOICES,  default='AC_output')
    row10 = models.CharField(max_length=30, choices=ROW_CHOICES, default='cloud_cover')
    row11 = models.CharField(max_length=30, choices=ROW_CHOICES, default='daily_pv_yield')
    row12 = models.CharField(max_length=30, choices=ROW_CHOICES, default='daily_battery_charge')
    row13 = models.CharField(max_length=30, choices=ROW_CHOICES, default='daily_power_consumption_total')
    row14 = models.CharField(max_length=30, choices=ROW_CHOICES, default='daily_power_cons_pv')
    row15 = models.CharField(max_length=30, choices=ROW_CHOICES, default='daily_grid_outage_n')

    def __str__(self):
        return self.sesh_site.site_name


class Sesh_Site(models.Model):
    """
    Model for each PV SESH installed site
    """
    site_name = models.CharField(max_length=100, unique = True)
    organisation = models.ForeignKey(Sesh_Organisation, null=True, blank=True)
    comission_date = models.DateTimeField('date comissioned')
    location_city = models.CharField(max_length = 100)
    location_country = models.CharField(max_length = 100)
    time_zone = models.CharField(max_length = 100, default='Africa/Kigali')
    position = GeopositionField()
    installed_kw = models.FloatField()
    system_voltage = models.IntegerField()
    number_of_panels = models.IntegerField()
    #enphase_ID = models.CharField( max_length = 100)
    #TODO need to figure a way to show this in admin to automatically populate
    #enphase_site_id = models.IntegerField()
    import_data = models.BooleanField(default=False)
    battery_bank_capacity = models.IntegerField()
    has_genset = models.BooleanField(default=False)
    has_grid = models.BooleanField(default=False)
    vrm_account = models.ForeignKey(VRM_Account,default=None,blank=True,null=True)
    vrm_site_id = models.CharField(max_length=20,default="",blank=True, null=True)
    status_card = models.OneToOneField(Status_Card,default=None,blank=True,null=True, on_delete=models.SET_NULL)
    site_measurements = models.OneToOneField(Site_Measurements, default=None,blank=True,null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.site_name


    def save(self, *args, **kwargs):
        # If site is being created
        if self.pk is None:
            self.status_card = Status_Card.objects.create()
            self.site_measurements = Site_Measurements.objects.create()
            super(Sesh_Site, self).save(*args, **kwargs)
            Sensor_Node.objects.create(site=self)
        else:
            super(Sesh_Site, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Delete the site and its associated status card
        status_card = self.status_card
        site_measurements = self.site_measurements
        site_measurements.delete()
        status_card.delete()
        super(Sesh_Site, self).delete(*args, **kwargs)

    #Row based permissioning using django guardian not every user should be able to see all sites

    class Meta:
        verbose_name = 'Sesh Site'
        verbose_name_plural = 'Sesh Sites'
        permissions = (
            ('view_Sesh_Site', 'View Sesh Site'),
        )

class Sesh_RMC_Account(models.Model):
    """
    API key used by SESH EMON node to communicate
    """
    site = models.OneToOneField(Sesh_Site, on_delete = models.CASCADE, primary_key = True)
    api_key = models.CharField(max_length=130,default="", unique=True)
    api_key_numeric = models.CharField(max_length=130, default="", unique=True)

    def __str__(self):
        return "alphanum:%s numeric:%s "%(self.api_key,self.api_key_numeric)

    def save(self, **kwargs):
        """
        Generate numeric version of api key
        """
        numeric_key = ""
        for l in self.api_key:
            numeric_key = numeric_key + str(ord(l));
        self.api_key_numeric = numeric_key[:len(self.api_key)]

        super(Sesh_RMC_Account,self).save(**kwargs)

    class Meta:
        verbose_name = "RMC API Account"


class Alert_Rule(models.Model):
    """
    Basic Alert rule model

    Alerts are defined through field choices.
    if an alert is defined as <model-name>#<field> this will be checking the MYSQL db
    if an alert is simple  <field-name> it will be queried in influx


    """
    OPERATOR_CHOICES = (
        ("eq" , "equals"),
        ("lt" , "less than"),
        ("gt" , "greater than"),
        )

    OPERATOR_MAPPING = {
            'eq' : '=',
            'lt' : '<',
            'gt' : '>',
            }

    FIELD_CHOICES = (('BoM_Data_Point#battery_voltage','battery voltage'),
                     ('BoM_Data_Point#soc','System State of Charge'),
                     ('BoM_Data_Point#AC_output','AC Loads'),
                     ('BoM_Data_Point#pv_production','Solar Energy Produced'),
                     ('BoM_Data_Point#main_on','Grid Availible'),
                     ('BoM_Data_Point#genset_state','Generator on'),
                     ('RMC_status#minutes_last_contact', 'RMC Last Contact'),
                     ('battery_voltage', 'Battery Voltage in influx rule'),
                )

    site = models.ForeignKey(Sesh_Site)
    check_field = models.CharField(choices=FIELD_CHOICES,max_length=100)
    value = models.FloatField()
    operator = models.CharField(max_length=2,
                                      choices=OPERATOR_CHOICES,
                                      default="lt")

    #TODO a slug field with the field operator and value info can be added
    #TODO this is vastly incomplete!! fields need to be mapable and chooices need to exist
    def __str__(self):
        return "If %s is %s %s" % (self.get_check_field_display(), self.get_operator_display() ,self.value)

    class Meta:
         verbose_name = 'System Alert Rule'
         verbose_name_plural = 'System Alert Rules'

#TODO Add alert Object to save alerts
class Sesh_Alert(models.Model):
    site = models.ForeignKey(Sesh_Site)
    alert = models.ForeignKey(Alert_Rule, related_name="alert_point")
    date = models.DateTimeField()
    isSilence = models.BooleanField()
    emailSent = models.BooleanField()
    smsSent = models.BooleanField()
    slackSent = models.BooleanField()
    point_model = models.CharField(max_length=40, default="BoM_Data_Point")
    point_id = models.CharField(max_length=40)

    # def __str__(self):  #
    #     return "Some texting text " #  % (self.alert.check_field, self.alert.operator, self.alert.value )

    def __str__(self):

       # TODO make this print useful information
       return str(self.alert)


    class Meta:
        verbose_name = 'System Alert'
        verbose_name_plural = 'System Alerts'


class RMC_status(models.Model):
    """
    Table containing status information for each RMC unit
    """
    # Removing due to infinitae migration error
    #rmc_account = models.OneToOneField(Sesh_RMC_Account,on_delete=models.CASCADE, related_name="rmc_status")
    site = models.ForeignKey(Sesh_Site, blank=True, null=True)
    ip_address = models.GenericIPAddressField(default=None, null=True)
    minutes_last_contact = models.IntegerField(default=None)
    signal_strength = models.IntegerField(default=None, null=True)
    data_sent_24h = models.IntegerField(default=None, null=True)
    time = models.DateTimeField()
    target_alert = models.ForeignKey(Sesh_Alert, blank=True, null=True )

    def clean(self):
        if not self.site:
            raise ValidationError("RMC status object requires either rmc account or sesh site reference")

    class Meta:
        verbose_name = 'RMC Status'
        verbose_name_plural = 'RMC Status\'s'


class BoM_Data_Point(models.Model):
    """
    BoM data Soc,, battery voltage system voltage etc
    Currently comes from Victron
    """
    #TODO unique together contraing on time and site
    site = models.ForeignKey(Sesh_Site)
    time = models.DateTimeField()
    soc = models.FloatField(default=0)
    battery_voltage = models.FloatField(default=0)
    AC_Voltage_in = models.FloatField(default=0)
    AC_Voltage_out = models.FloatField(default=0)
    AC_input = models.FloatField(default=0)
    AC_output = models.FloatField(default=0)
    AC_output_absolute = models.FloatField(default=0)
    AC_Load_in = models.FloatField(default=0)
    AC_Load_out = models.FloatField(default=0)
    #NEW  victron now tells us pv production
    pv_production = models.FloatField(default=0)
    inverter_state = models.CharField(max_length = 100, blank=True, null=True)
    target_alert = models.ForeignKey(Sesh_Alert, blank=True, null=True )
    main_on = models.BooleanField(default=False)
    genset_state = models.IntegerField(default=0)
    #TODO relay will likely need to be it's own model
    relay_state = models.IntegerField(default=0)
    trans = models.IntegerField(default=0)

    def __str__(self):
        return " %s : %s : %s" %(self.time,self.site,self.soc)

    class Meta:
         verbose_name = 'Data Point'
         unique_together = ('site','time')

class Data_Point(models.Model):
    """
    Successor to Daily Data Point
    Moving to single field to have a variable number of fields
    """

    UNITS_DICTIONARY = (
        ("id", ''),
        ("soc","%"),
        ("battery_voltage", "V"),
        ("AC_Voltage_in" , "V"),
        ("AC_Voltage_out" , "V"),
        ("AC_input" , "W"),
        ( "AC_output" , "W"),
        ( "AC_Load_in" , "A"),
        ( "AC_Load_out" , "A"),
        ( "cloud_cover","%"),
        ( "pv_production" , "W"),
        ( "main_on" , ""),
        ( "relay_state", ""),
        ( "trans" , ""),
        ( "genset_state" , ""),
        ( "site" , ""),
        ( "AC_output_absolute" , "W"),
        ( "minutes_last_contact" , "min"),
        ( "daily_battery_charge", "Wh"),
        ( "daily_grid_outage_n", "minute"),
        ( "daily_grid_outage_t", ""),
        ( "daily_grid_usage", "Wh"),
        ( "daily_no_of_alerts", "alert"),
        ( "daily_power_cons_pv", "W"),
        ( "daily_power_consumption_total", "Wh"),
        ("daily_pv_yield", "Wh"),
        )


    MEASUREMENTS_VERBOSE_NAMES = (
        ("soc","State of Charge"),
        ("battery_voltage", "Battery Voltage"),
        ("AC_Voltage_in", "AC Voltage In"),
        ("AC_Voltage_out", "AC Voltage Out"),
        ("AC_input", "AC Input"),
        ("AC_output", "AC Output"),
        ("AC_Load_in", "AC Load in"),
        ("AC_Load_out", "AC Load out"),
        ("pv_production", "PV Production"),
        ("main_on", "Main On"),
        ("relay_state", "Relay State"),
        ("trans", " Trans"),
        ("genset_state", "Genset State"),
        ("AC_output_absolute", "AC Output absolute"),
        ("minutes_last_contact", "Minutes last Contact"),
        ("daily_battery_charge", "Daily Battery Charge"),
        ("daily_grid_outage_n", "Daily Grid Outage N"),
        ("daily_grid_outage_t", "Daily Grid Outage T"),
        ("daily_grid_usage", "Daily Grid Usage"),
        ("daily_no_of_alerts", "Daily Number of Alerts"),
        ("daily_power_cons_pv", "Daily Power Cons Pv"),
        ("daily_power_consumption_total", "Daily Power Consumption Total"),
        ("daily_pv_yield", "Daily Pv Yield"),
        ("cloud_cover", "Cloud Cover"),
    )

    site = models.ForeignKey(Sesh_Site)
    field_name = models.FloatField(default=0,
            verbose_name="Data Point Name",  choices=MEASUREMENTS_VERBOSE_NAMES)
    field_unit = models.FloatField(default=0,
            verbose_name="Data Point Name",  choices=UNITS_DICTIONARY)
    #TODO Perhaps add scale as well?

class Daily_Data_Point(models.Model):
    """
    Daily aggregate of data points
    """

    UNITS_DICTIONARY = {
        "id": '',
        "soc":"%",
        "battery_voltage": "V",
        "AC_Voltage_in" : "V",
        "AC_Voltage_out" : "V",
        "AC_input" : "W",
        "AC_output" : "W",
        "AC_Load_in" : "A",
        "AC_Load_out" : "A",
        "cloud_cover":"%",
        "pv_production" : "W",
        "main_on" : "",
        "relay_state": "",
        "trans" : "",
        "genset_state" : "",
        "site" : "",
        "AC_output_absolute" : "W",
        "minutes_last_contact" : "min",
        "daily_battery_charge": "Wh",
        "daily_grid_outage_n": "minute",
        "daily_grid_outage_t": "",
        "daily_grid_usage": "Wh",
        "daily_no_of_alerts": "alert",
        "daily_power_cons_pv": "W",
        "daily_power_consumption_total": "Wh",
        "daily_pv_yield": "Wh",
    }


    MEASUREMENTS_VERBOSE_NAMES = {
        "soc":"State of Charge",
        "battery_voltage": "Battery Voltage",
        "AC_Voltage_in": "AC Voltage In",
        "AC_Voltage_out": "AC Voltage Out",
        "AC_input": "AC Input",
        "AC_output": "AC Output",
        "AC_Load_in": "AC Load in",
        "AC_Load_out": "AC Load out",
        "pv_production": "PV Production",
        "main_on": "Main On",
        "relay_state": "Relay State",
        "trans": " Trans",
        "genset_state": "Genset State",
        "AC_output_absolute": "AC Output absolute",
        "minutes_last_contact": "Minutes last Contact",
        "daily_battery_charge": "Daily Battery Charge",
        "daily_grid_outage_n": "Daily Grid Outage N",
        "daily_grid_outage_t": "Daily Grid Outage T",
        "daily_grid_usage": "Daily Grid Usage",
        "daily_no_of_alerts": "Daily Number of Alerts",
        "daily_power_cons_pv": "Daily Power Cons Pv",
        "daily_power_consumption_total": "Daily Power Consumption Total",
        "daily_pv_yield": "Daily Pv Yield",
        "cloud_cover": "Cloud Cover",
    }




    site = models.ForeignKey(Sesh_Site)
    daily_pv_yield = models.FloatField(default=0,
            verbose_name="Daily PV Yield") # Aggregate pv produced that day Kwh
    daily_power_consumption_total = models.FloatField(default=0,
            verbose_name="Daily Power Consumption")
    daily_power_cons_pv = models.FloatField(default=0,
            verbose_name="Power consumption pv" )
    daily_battery_charge = models.FloatField(default=0,
            verbose_name="Battery Charge") # Amount of charge put in battery
    daily_grid_outage_t = models.FloatField(default=0,
            verbose_name="Grid outage t") # Amount of time the grid was off
    daily_grid_outage_n = models.FloatField(default=0,
            verbose_name="Grid outagen n") # Aggregate amount times  grid was off
    daily_grid_usage = models.FloatField(default=0,
            verbose_name="Grid usage" ) # Aggregate amount of grid used
    daily_no_of_alerts = models.IntegerField(default=0, verbose_name="Number of alerts")
    date = models.DateTimeField()


    class Meta:
         verbose_name = 'Daily Aggregate Data Point'
         unique_together = ('site','date')

    def __str__(self):
        return " sitename:%s \n pv_yield:%s \n power_used:%s \n daily_batt_charge:%s \n grid power used: %s" % (self.site.site_name,
                  self.daily_pv_yield,
                  self.daily_power_cons_pv,
                  self.daily_battery_charge,
                  self.daily_grid_usage)


class Trend_Data_Point(models.Model):
    """
    Succesor to aggregate data points. Each site can have almost an unlimited number
    of aggregate data points, using Trend_Data _point to succede this
    """
    site = models.ForeignKey(Sesh_Site)
    aggrge_field_name = models.FloatField(default=0)


class Site_Weather_Data(models.Model):
    """

    weather data to overlay with each stite

    """
    site = models.ForeignKey(Sesh_Site)
    date = models.DateTimeField('date',unique_for_date=True)
    temp = models.IntegerField()
    condition = models.CharField(max_length=20)
    cloud_cover = models.FloatField()
    sunrise = models.TimeField()
    sunset = models.TimeField()

    class Meta:
        verbose_name = 'Weather Data'
        unique_together = ('site','date')


class Status_Rule(models.Model):
    """
    battery_voltage rules and pv pv_production rules
    """
    battery_rules = {
                     50 : "red",
                     70 : "yellow",
                     100: "green"
                    }
    weather_rules = {
               0.7 : "green",
               1 : "yellow"
               }
    def __str__(self):
        return self.battery_rules + self.pv_rules



# Used globally?
SENSORS_LIST = {
    'Tx',
    'Th',
    'Pe'
}



class Sensor_Node(models.Model):
     """
     Table representative for the emon tx
     """
     NODE_ID_CHOICES = (
                         (19, 19),
                         (20, 20),
                         (21, 21),
                         (22, 22),
                         (23, 23),
                         (24, 24),
                         (25, 25),
                         (26, 26),
                         (27, 27),
                         (28, 28),
                         (29, 29),
                     )
     SENSOR_TYPE_CHOICES = (
                        ('th','Temperature Humidity'),
                        ('tx','Power Voltage'),
                        ('pe','Ph Ethenoal'),
                    )

     site = models.ForeignKey(Sesh_Site)
     node_id = models.IntegerField(default=0, choices=NODE_ID_CHOICES)
     sensor_type = models.CharField(max_length=40, choices=SENSOR_TYPE_CHOICES)
     index1 = models.CharField(max_length=40, default="ac_power1")
     index2 = models.CharField(max_length=40, default="pv_production", blank=True, null=True)
     index3 = models.CharField(max_length=40, default="consumption", blank=True, null=True)
     index4 = models.CharField(max_length=40, default="grid_in", blank=True, null=True)
     index5 = models.CharField(max_length=40, default="AC_Voltage_out", blank=True, null=True)
     index6 = models.CharField(max_length=40, blank=True, null=True)
     index7 = models.CharField(max_length=40, blank=True, null=True)
     index8 = models.CharField(max_length=40, blank=True, null=True)
     index9 = models.CharField(max_length=40, blank=True, null=True)
     index10 = models.CharField(max_length=40, blank=True, null=True)
     index11 = models.CharField(max_length=40, blank=True, null=True)
     index12 = models.CharField(max_length=40, blank=True, null=True)

     def __str__(self):
         return "Sensor Node " + str(self.sensor_type) + " for " + self.site.site_name + " with id "+ str(self.node_id)

     def save(self, *args, **kwargs):
         if not Sensor_Mapping.objects.filter(site_id=self.site.id, node_id=self.node_id,sensor_type=self.sensor_type):
             Sensor_Mapping.objects.create(site_id=self.site.id, node_id=self.node_id, sensor_type=self.sensor_type)
         super(Sensor_Node,self).save(*args, **kwargs)

     def delete(self, *args, **kwargs):
        Sensor_Mapping.objects.filter(site_id=self.site.id, node_id=self.node_id,
                                  sensor_type=self.sensor_type).delete()

        super(Sensor_Node,self).delete(*args, **kwargs)

class Sensor_Mapping(models.Model):
    """
    To contain informations about the sensor mapping
    of sensors node_ids and sites

    This helps in the writing of data to the database by
    the sesh-api-helper
    """
    site_id = models.IntegerField()
    node_id = models.IntegerField()
    sensor_type = models.CharField(max_length=40)

    def __str__(self):
        return "Site_id: " + str(self.site_id) + "  node_id: " + str(self.node_id) + ": " + str(self.sensor_type)

    class Meta:
        unique_together =  ('site_id', 'node_id', 'sensor_type')


class Report_Job(models.Model):
    """
    Model to contain the reports that should be sent,
    to users of specific sites
    """
    DURATION_CHOICES = (
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    )
    site = models.ForeignKey(Sesh_Site)
    duration = models.CharField(max_length=40, choices=DURATION_CHOICES)
    day_to_report = models.IntegerField() # This will contain an integer value showing the day the reports will execute, if it is a weekly report and the number is 2 then it would execute on Tuesday
    attributes = JSONField()

    def __str__(self):
        return self.get_duration_display() + " report for " + self.site.site_name

    def get_duration_choices(self):
        duration_list = []
        for item in self.DURATION_CHOICES:
            duration_list.append(item[0])

        return duration_list

    def get_kapacitor_tasks(self): 
        kap = Kapacitor()
        pattern = self.site.site_name + '_' + self.duration + "*"
        return kap.list_tasks(pattern=pattern)

    def save(self, *args, **kwargs):
        """
        On save add kapacitor task referencing the report
        """
        self.add_kapacitor_tasks()
        super(Report_Job, self).save(*args, **kwargs)

    def add_kapacitor_tasks(self):
        """
        Adds the kapacitor tasks for the report
        """
        from seshdash.utils.reporting import add_report_kap_tasks
        add_report_kap_tasks(self)
        
    def delete(self, *args, **kwargs):
        """
        On delete delet kapacitor tasks referencing the report Job
        """
        self.delete_kapacitor_tasks()
        super(Report_Job, self).delete(*args, **kwargs)


    def delete_kapacitor_tasks(self):
        """
        Deletes the kapacitor tasks attached to the report
        """ 
        kap = Kapacitor()
        pattern =  self.site.site_name + '_' + self.duration + "*" # tasks begining with site_name_duration
        return kap.delete_tasks(pattern)


    class Meta:
        unique_together = (('site','duration'),)
        

class Report_Sent(models.Model):
    """
    Store each report sent for later viewing or resending
    """
    report_job = models.ForeignKey(Report_Job)
    title = models.CharField(max_length = 60)
    date = models.DateTimeField()
    status = models.CharField(max_length = 100)
    content = models.TextField()
    sent_to = JSONField() # list of users report was sent to


class Data_Process_Rule(models.Model):
    """
    for building aggregate batch proccesing functions
    """
    FUNCTION_CHOICES = (
        ("mean" , "average"),
        ("sum" , "aggregate"),
        ("min" , "minimum"),
        ("max" , "maximum"),
        ("mid" , "median"),
        ("std" , "standard deviation"),
        )

    TIME_BUCKETS = (
            ("5m", "5 minutes"),
            ("10m", "10 minutes"),
            ("30m", "30 minutes"),
            ("1h", "1 hour"),
            ("2h", "2 hours"),
            ("5h", "5 hours")
        )

    DURATION = (
            ("12h", "12 hours"),
            ("24h", "24 hours"),
            ("48h", "48 hours"),
            ("7d", "7 days"),
            ("31d", "1 month"),
            )

    site = models.ForeignKey(Sesh_Site)
    function_type = models.CharField(max_length=40, default="aggregate", choices=FUNCTION_CHOICES )
    input_field = models.ForeignKey(Daily_Data_Point)
    duration = models.CharField(max_length=40, default="24h", choices=DURATION)
    interval = models.CharField(max_length=10, default="5m", choices=TIME_BUCKETS)
    output_field = models.ForeignKey(Trend_Data_Point)


class Tick_Script(models.Model):
    """ 
    This is a model to hold data about the 
    tick scripts
    """
    SCRIPT_TYPE_CHOICES = (
        ('stream', 'Stream'),
        ('batch', 'Batch'),
    )

    site = models.ForeignKey(Sesh_Site)
    input_field_name = models.CharField(max_length=40)  # The influx measurement to operate on
    output_field_name = models.CharField(max_length=40)  # The influx measurement to output results of the operation
    script = models.TextField() 
    function = models.CharField(max_length=20) # Influx function operation to use
    interval = models.CharField(max_length=10) # The interval the task script runs on e.g 1min, 1h, 1d, 1w
    script_type = models.CharField(max_length=10, choices=SCRIPT_TYPE_CHOICES)
    
    
