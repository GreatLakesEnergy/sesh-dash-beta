# Utility
import requests, json, logging
import csv
import urllib2
from os import path, remove
from pprint import pprint
from datetime import datetime,timedelta
from ..utils import time_utils

import pprint

# Configuration
from django.conf import settings

# Instantiating a logger
logger = logging.getLogger(__name__)

class VictronAPI:
    #API_BASE_URL = "http://juice.m2mobi.com/{call_type}/{function}"
    API_BASE_URL = "https://juice.victronenergy.com/{call_type}/{function}"

    API_HIST_LOGIN_URL = "https://vrm.victronenergy.com/user/login"
    API_HIST_FETCH_URL = "https://vrm.victronenergy.com/site/download-csv/site/{SITE_ID}/start_time/{START_TIME}/end_time/{END_TIME}"
    VERIFICATION_TOKEN = "seshdev"
    _SYSTEM_STAT_KEYS = [
       'VE.Bus state',
        'Input power 1',
        'AC Input 1 ',
        'Input frequency 1',
        'Output power 1',
        'AC Consumption L1',
        'Input voltage phase 1',
        'Input current phase 1',
        'Output current phase 1',
        'Output voltage phase 1',
        'PV - AC-coupled on output L1'
        ]

    _BATTERY_STAT_KEYS = [
        'Battery State of Charge (System)',
        'Battery current',
        'Battery voltage',
        'Battery Power (System)',
        'Battery state']

    API_VERSION = "220"
    ATTRIBUTE_DICT = {}

    FORMAT = "json"

    def __init__(self , user_name, user_password, format_type=json):
        """
        Provide API key and User Key to get started
        more info here:https://developer.enphase.com/docs/quickstart.html

        """
        #Initiate object constants within object
        self.SYSTEMS_IDS = []
        self.USERNAME = ""
        self.PASSWORD = ""
        self.SESSION_ID = ""
        self.IS_INITIALIZED = False

        #TODO disabling sl warnings
        #requests.packages.urllib3.disable_warnings()

        self.USERNAME = user_name
        self.PASSWORD = user_password

        self.initialize()
        if self.IS_INITIALIZED:
            logger.info("System Initialized with %s systems"%len(self.SYSTEMS_IDS))
        else:
            logger.error("unable to initialize the api")

    def initialize(self):
        """
        Initialize the system.
        Do this so by making a request to VRM portal logging in and obtaining user session ID
        TODO: print out user info gatherd from system
        """
        response  = self._make_request(
                "user",
                "login",
                username=self.USERNAME,
                password=self.PASSWORD)
        if response['status']['code'] == 403:
            logger.error("Access denied unable to initialize check credentials \nresponse: %s:" %response)
            self.IS_INITIALIZED = False
            return None
        if response.has_key("data"):
            self.SESSION_ID = response["data"]["user"]["sessionid"]
            v_sites = self.get_site_list()
            #Populate sites  under account
            for site in v_sites:
                self.SYSTEMS_IDS.append((site['idSite'],site['name']))
                #logger.debug("initializing sites, getting attributes")
                site_id =  site['idSite']
                atr = self.get_site_attributes_list(site_id)
                #make attribute dictionary more usefull
                atr_site = {}
                atr_site[site_id] =  atr['attributes']
                #create a dictionary with site_id as key
                self.ATTRIBUTE_DICT[site_id] = self._reformat_attr_dict(atr_site[site_id])

                self.IS_INITIALIZED = True
        else:
            logger.error("Problem getting session id %s"%response)
            self.IS_INITIALIZED = False


    def _reformat_attr_dict(self,atr_dict):
        """
        reformat attribute dictionary so it's easier to use
        """
        flat = {}
        c =  map(lambda x:{x['customLabel']:x},atr_dict)
        for val in c:
                flat[val.keys()[0]] = val[val.keys()[0]]
        return flat


    def _make_request(self,call_type,function,response="json",**data):
        """
        Utiliy function to make requsts.
        Will return json or request based on response parameter
        Data needs to be passed with data keyword
        """
        #format string with our paramters can do this with requests as well
        formated_URL = self.API_BASE_URL.format(call_type=call_type,function=function)

        #these  paramters are mandatory
        headers = {"content-type":" application/x-www-form-urlencoded"}
        data['version'] = self.API_VERSION
        data['sessionid'] = self.SESSION_ID
        data['verification_token'] = self.VERIFICATION_TOKEN
        ###
        #logger.debug(data)
        if  data:
            r = requests.post(formated_URL,data=data, headers = headers)

        else:
            r = requests.post(formated_URL, headers = headers)
        if r.status_code == 200:
                return r.json()
        elif r.status_code == 401:
            logger.error("recieved error code %s %s"%(r.status_code,r.json()))
            logger.error("The system needs o be re_initialized please run intialize()")
            return r.json()
        else:
            return r.json()


    def _parse_results(self,results,key=None):
        """
        unwrap each package
        """
        result = {}
        if results['status']['code'] == 200:
            if key:
                result = results['data'][key]
            else:
                result = results['data']
        else:
            logger.error("error in response %s"%results)
        return result

    def get_site_list(self):
        """
        Get system list
        """
        key = "sites"
        result  = self._make_request("sites","get")
        result = self._parse_results(result,key)
        return result

    def get_site_stats(self,site_id):
        """
        Get system stats for provided system_id
        @params: site_id
        """
        key = "sites"
        result =  self._make_request(key,"get_site",siteid=site_id)
        result = self._parse_results(result,key)
        return result

    def get_energy_data(self,site_id):
        """
        return monthly production from start date
        @params: site_id
        """
        result =  self._make_request("sites","get_energy_data", siteid=site_id, instance = 0)
        result = self._parse_results(result)
        return result

    def get_site_attributes_list(self,site_id):
        """
        Get all associated attributes with a site
        @params: site_id
        """
        result =  self._make_request("sites","get_site_attributes", siteid=site_id, instance = 0)
        return self._parse_results(result)

    def get_site_attribute(self,site_id,attribute_code_arr):
        """
        Get all attribute data from  with a site
        @params: site_id, attribute_code_arr
        """
        codes_arr_json = json.dumps(attribute_code_arr)
        results = self._make_request("sites","attributes_by_code",codes=codes_arr_json, siteid=site_id, instance = 0)
        parsed = self._parse_results(results,'attributes')
        return parsed


    def get_system_stats(self,site_id):
        """
        Get the  basic system stats
        """
        code_arr = []
        for key in self._SYSTEM_STAT_KEYS:
            if self.ATTRIBUTE_DICT[site_id].has_key(key):
                code_arr.append(self.ATTRIBUTE_DICT[site_id][key]['code'])
        result_arr = self.get_site_attribute(site_id,code_arr)
        resut_dict = self._reformat_attr_dict(result_arr)
        return resut_dict

    def get_battery_stats(self,site_id):
        """
        Get the battery stats:
        """
        #TODO  merge this function with system stats and other stas as they are identical
        #TODO: UNCOMMENT THE logging.debug // COMMENT Them out for proper priting
        print "NOW INT THE BATTERRY STATS"
        print "THE Battery Stat keys is: ",
        print self._BATTERY_STAT_KEYS
        print "BUT THE ATTRIBUTE DICT CONTAINS",
        pretty_printer = pprint.PrettyPrinter(indent=4)
        print pretty_printer.pprint(self.ATTRIBUTE_DICT[site_id])
        code_arr = []
        for key in self._BATTERY_STAT_KEYS:
            code_arr.append(self.ATTRIBUTE_DICT[site_id][key]['code'])

        result_arr = self.get_site_attribute(site_id,code_arr)
        resut_dict = self._reformat_attr_dict(result_arr)
        print "The returned data from the get battery stats is: ",
        print resut_dict
        return resut_dict


class VictronHistoricalAPI:
    """
    API to get historical data from the VRM
    """

    #TODO make logging activated
    API_HIST_LOGIN_URL = "https://vrm.victronenergy.com/user/login"
    #API_HIST_FETCH_URL = "https://vrm.victronenergy.com/site/download-csv/site/{SITE_ID}/start_time/{START_AT}/end_time/{END_AT}"
    API_HIST_FETCH_URL = "https://vrm.victronenergy.com/site/{SITE_ID}/download-data/log/csv/{START_AT}/{END_AT}"
    USERNAME = ""
    PASSWORD = ""
    SESSION_COOKIES = []
    TIMEZONE = 0
    SESSION = None
    DOWNLOAD_FOLDER = settings.TEMP_FOLDER
    USER_AGENT = "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36"

    CSV_KEYS = ['Date Time',
                'Input voltage phase 1',
                'Input current phase 1',
                'Input frequency 1',
                'Input power 1',
                'Output voltage phase 1',
                'Output current phase 1',
                'Output frequency',
                'Output power 1',
                'Battery voltage',
                'Battery current',
                'Phase count',
                'Active input',
                'Active input current limit',
                'VE.Bus state of charge',
                'VE.Bus state',
                'VE.Bus Error',
                'Switch Position',
                'Temperature alarm',
                'Low battery alarm',
                'Overload alarm',
                'PV-AC',
                'AC Consumption L1',
                'Grid L1 Battery Voltage (System)',
                'Battery Current (System)',
                'VE.Bus charge current (System)',
                'Battery Power (System)',
                'VE.Bus charge power (System)',
                'Battery State of Charge (System)',
                'Battery staate',
                'Position',
                'L1 Voltage',
                'L1 Current',
                'L1 Power',
                'L1 Energy']

    def __init__(self , user_name, user_password, timezone=-4, dl_fldr=DOWNLOAD_FOLDER):
         self.IS_HIST_INITIALIZED = False
         requests.packages.urllib3.disable_warnings()
         self.USERNAME = user_name
         self.PASSWORD = user_password
         self.DOWNLOAD_FOLDER = dl_fldr
         self.TIMEZONE = timezone
         self.SESSION = requests.Session()
         self.SESSION_COOKIES = {}
         self._csv_reader = None
         self._csv_file = None
         self._csv_file_path = None
         self.initialize()

    def initialize(self):
         """
         Login to the portal and save the cookie for later reuse
         """
         data = {}
         first_cookies = {}
         second_cookies = {}
         # Setup Headers
         data['password'] = self.PASSWORD
         data['username'] = self.USERNAME
         data['local_timezone'] = self.TIMEZONE
         data['is_dst'] = 0

         # Make Request
         r = self.SESSION.post(self.API_HIST_LOGIN_URL,data=data,verify=False)


         try:
            # Handle our tricky cookie situation
             first_cookies = r.history[0].cookies.get_dict()
             second_cookies  = r.cookies.get_dict()
         except Exception,e:
             self.IS_HIST_INITIALIZED = False
             logger.error("Victron Hist apI error getting cookies "%str(e))

         # Merge our cookie dictionaries

         first_cookies.update(second_cookies)
         self.SESSION_COOKIES = first_cookies
         #TODO this is border line screan scraping so this error condition will not be caught
         if r.status_code == 200 and self.SESSION_COOKIES.has_key('VRM_session_id'):
                self.IS_HIST_INITIALIZED = True
                logger.info("Victron historical API initialized")
         else:
                self.IS_HIST_INITIALIZED = False
                logger.warning("Problem initializing Victorn Hist API")


    def get_data(self,site_id,start_at,end_at=None):
        """
        Will download a csv containt all data for provided seconds from epoch time window.
        """

        if not self.IS_HIST_INITIALIZED:
            return None
        if not end_at:
            end_at = time_utils.get_epoch_from_datetime(datetime.now()-timedelta(days=1))
        chunksize = 10
        formated_URL = self.API_HIST_FETCH_URL.format(
               SITE_ID = site_id,
               START_AT = start_at,
               END_AT = end_at
                )
        filepath = self.DOWNLOAD_FOLDER
        filename = "%s_%s_dump.csv"%(site_id,start_at)
        full_file = path.join(self.DOWNLOAD_FOLDER,filename)
        self._csv_file_path = full_file
        #need to trick the VRM
        headers  = {'user-agent':self.USER_AGENT}
        #data = self.SESSION.get(formated_URL,stream=True)
        data = self.SESSION.get(formated_URL,stream=True,verify=False)
        #logger.debug(" starting downloading csv file")
        with open(full_file, 'wb') as fd:
            #logger.debug("writing csv file to %s"%full_file)
            for chunk in data.iter_content(chunksize):
                fd.write(chunk)

        #DEBUG
        #logger.debug("finished downloading csv")
        self._csv_file = full_file
        return self._parse_csv_data(full_file)

    def _parse_csv_data(self,csv_data_file):
        """
        return iterable csv reader object

        """
        #logger.debug("parsing csv data %s"%csv_data_file)
        #data_arr = []
        try:
            self._csv_file = open(csv_data_file)
            #need to skip first row
            self._csv_file.readline()
            self.CSV_KEYS = self._csv_file.readline().replace('"','').split(',')
            # First column should always be date time
            self.CSV_KEYS[0] = 'Date Time'
            self._csv_file.readline()
            self._csv_reader =  csv.DictReader(self._csv_file,self.CSV_KEYS)
            return self._csv_reader

        except Exception,e:
            logger.error("unable to find file or key %s"%e)
            remove(csv_data_file)
            self._csv_file.close()

    def flush(self):
        try:
            self._csv_file.close()
            remove(self._csv_file_path)
        except Exception, e:
            logger.exception("Unable to flush csv files %s : %s"%(self._csv_file,e))
