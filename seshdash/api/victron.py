import requests, json, logging
import csv
import urllib2

from os import path
from pprint import pprint
from datetime import datetime,timedelta
from ..utils import time_utils

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
        'Output voltage phase 1']

    _BATTERY_STAT_KEYS = [
        'Battery State of Charge (System)',
        'Battery current',
        'Battery voltage',
        'Battery Power (System)',
        'Battery state']

    API_VERSION = "220"
    ATTRIBUTE_DICT = {}

    FORMAT = "json"

    """
    Provide API key and User Key to get started
    more info here:https://developer.enphase.com/docs/quickstart.html

    """
    def __init__(self , user_name, user_password, format_type=json):
        #Initiate object constants within object
        self.SYSTEMS_IDS = []
        self.USERNAME = ""
        self.PASSWORD = ""
        self.SESSION_ID = ""
        self.IS_INITIALIZED = False

        #TODO disabling sl warnings
        requests.packages.urllib3.disable_warnings()

        self.USERNAME = user_name
        self.PASSWORD = user_password

        self.initialize()
        if self.IS_INITIALIZED:
            logging.info("System Initialized with %s systems"%len(self.SYSTEMS_IDS))
        else:
            logging.error("unable to initialize the api")

    """
    Initialize the system.
    Do this so by making a request to VRM portal logging in and obtaining user session ID
    TODO: print out user info gatherd from system
    """
    def initialize(self):
        response  = self._make_request(
                "user",
                "login",
                username=self.USERNAME,
                password=self.PASSWORD)
        if response['status']['code'] == 403:
            logging.error("Access denied unable to initialize check credentials \nresponse: %s:" %response)
            self.IS_INITIALIZED = False
        if response.has_key("data"):
            self.SESSION_ID = response["data"]["user"]["sessionid"]
            v_sites = self.get_site_list()
            #Populate sites  under account
            for site in v_sites:
                self.SYSTEMS_IDS.append((site['idSite'],site['name']))
                logging.info("initializing sites, getting attributes")
                atr = self.get_site_attributes_list(site['idSite'])
                #make attribute dictionary more usefull
                atr_site = {}
                atr_site[site['idSite']] =  atr['attributes']
                for site in  self.SYSTEMS_IDS:
                    #create a dictionary with site_id as key
                    self.ATTRIBUTE_DICT[site[0]] = self._reformat_attr_dict(atr_site[site[0]])

                self.IS_INITIALIZED = True
        else:
            logging.error("Problem getting session id %s"%response)
            self.IS_INITIALIZED = False


    """
    reformat attribute dictionary so it's easier to use
    """
    def _reformat_attr_dict(self,atr_dict):
        flat = {}
        c =  map(lambda x:{x['customLabel']:x},atr_dict)
        for val in c:
                flat[val.keys()[0]] = val[val.keys()[0]]
        return flat

    """
    Utiliy function to make requsts.
    Will return json or request based on response parameter
    Data needs to be passed with data keyword
    """
    def _make_request(self,call_type,function,response="json",**data):
        #format string with our paramters can do this with requests as well
        formated_URL = self.API_BASE_URL.format(call_type=call_type,function=function)

        #these  paramters are mandatory
        headers = {"content-type":" application/x-www-form-urlencoded"}
        data['version'] = self.API_VERSION
        data['sessionid'] = self.SESSION_ID
        data['verification_token'] = self.VERIFICATION_TOKEN
        ###
        logging.info(data)
        if  data:
            r = requests.post(formated_URL,data=data, headers = headers)

        else:
            r = requests.post(formated_URL, headers = headers)
        if r.status_code == 200:
                return r.json()
        elif r.status_code == 401:
            logging.error("recieved error code %s %s"%(r.status_code,r.json()))
            logging.error("The system needs o be re_initialized please run intialize()")
            return r.json()
        else:
            return r.json()

    """
    unwrap each package
    """
    def _parse_results(self,results,key=None):
        result = {}
        if results['status']['code'] == 200:
            if key:
                result = results['data'][key]
            else:
                result = results['data']
        else:
            logging.error("error in response %s"%results)
        return result

    """
    Get system list
    """
    def get_site_list(self):
        key = "sites"
        result  = self._make_request("sites","get")
        result = self._parse_results(result,key)
        return result

    """
    Get system stats for provided system_id
    @params: site_id
    """
    def get_site_stats(self,site_id):
         key = "sites"
         result =  self._make_request(key,"get_site",siteid=site_id)
         result = self._parse_results(result,key)
         return result

    """
    return monthly production from start date
    @params: site_id
    """
    def get_energy_data(self,site_id):
         result =  self._make_request("sites","get_energy_data", siteid=site_id, instance = 0)
         result = self._parse_results(result)
         return result

    """
    Get all associated attributes with a site
    @params: site_id
    """
    def get_site_attributes_list(self,site_id):
         result =  self._make_request("sites","get_site_attributes", siteid=site_id, instance = 0)
         return self._parse_results(result)

    """
    Get all attribute data from  with a site
    @params: site_id, attribute_code_arr
    """
    def get_site_attribute(self,site_id,attribute_code_arr):
         codes_arr_json = json.dumps(attribute_code_arr)
         results = self._make_request("sites","attributes_by_code",codes=codes_arr_json, siteid=site_id, instance = 0)
         parsed = self._parse_results(results,'attributes')
         return parsed

    """
    Get the  basic system stats
    """
    def get_system_stats(self,site_id):
        code_arr = []
        for key in self._SYSTEM_STAT_KEYS:
            code_arr.append(self.ATTRIBUTE_DICT[site_id][key]['code'])
        result_arr = self.get_site_attribute(site_id,code_arr)
        resut_dict = self._reformat_attr_dict(result_arr)
        return resut_dict

    """
    Get the battery stats:
    """
    def get_battery_stats(self,site_id):
        #TODO  merge this function with system stats and other stas as they are identical
        code_arr = []
        for key in self._BATTERY_STAT_KEYS:
            code_arr.append(self.ATTRIBUTE_DICT[site_id][key]['code'])

        result_arr = self.get_site_attribute(site_id,code_arr)
        resut_dict = self._reformat_attr_dict(result_arr)
        return resut_dict


class VictronHistoricalAPI:
    """
    API to get historical data from the VRM
    """

    API_HIST_LOGIN_URL = "https://vrm.victronenergy.com/user/login"
    API_HIST_FETCH_URL = "https://vrm.victronenergy.com/site/download-csv/site/{SITE_ID}/start_time/{START_AT}/end_time/{END_AT}"
    USERNAME = ""
    PASSWORD = ""
    SESSION_COOKIES = []
    TIMEZONE = 0
    SESSION = None
    DOWNLOAD_FOLDER = "/tmp/"
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
                'Battery current Phase count',
                'Active input',
                'Active input current limit',
                'VE.Bus state of charge VE.Bus state',
                'VE.Bus Error',
                'Switch Position',
                'Temperature alarm',
                'Low battery alarm',
                'Overload alarm',
                'AC Consumption L1',
                'Grid L1 Battery Voltage (System)',
                'Battery Current (System)',
                'VE.Bus charge current (System)',
                'Battery Power (System)',
                'VE.Bus charge power (System)',
                'Battery State of Charge (System)',
                'Battery state']

    def __init__(self , user_name, user_password, timezone=-4,dl_fldr="/tmp"):
         self.IS_HIST_INITIALIZED = False
         requests.packages.urllib3.disable_warnings()
         self.USERNAME = user_name
         self.PASSWORD = user_password
         self.DOWNLOAD_FOLDER = dl_fldr
         self.TIMEZONE = timezone
         self.SESSION = requests.Session()
         self.initialize()

    def initialize(self):
         """
         Login to the portal and save the cookie for later reuse
         """
         data= {}
         data['password'] = self.PASSWORD
         data['username'] = self.USERNAME
         data['local_timezone'] = self.TIMEZONE
         data['is_dst'] = 0
         r = self.SESSION.post(self.API_HIST_LOGIN_URL,data=data)
         self.SESSION_COOKIES = r.cookies.get_dict()
         #TODO this is border line screan scraping so this error condition will not be caught
         if r.status_code == 200 and self.SESSION_COOKIES:
                self.IS_HIST_INITIALIZED = True
                logging.info("Victron historical API initialized")

    def get_data(self,site_id,start_at,end_at=None):
        """
        Will download a csv containt all data for provided seconds from epoch time window.
        """

        if not end_at:
            print "minus 1 day"
            end_at = time_utils.get_epoch_from_datetime(datetime.now()-timedelta(days=1))
        chunksize = 10
        formated_URL = self.API_HIST_FETCH_URL.format(
               SITE_ID = site_id,
               START_AT = start_at,
               END_AT = end_at
                )
        print  "getting %s"%formated_URL
        filepath = self.DOWNLOAD_FOLDER
        filename = "%s.csv"%(start_at)
        full_file = path.join(self.DOWNLOAD_FOLDER,filename)
        #need to trick the VRM
        headers  = {'user-agent':self.USER_AGENT}
        print "skipping headers"
        print "Manual Labour"
        #data = self.SESSION.get(formated_URL,stream=True)
        data = self.SESSION.get(formated_URL,stream=True)
        with open(full_file, 'wb') as fd:
            logging.debug("writing csv file to %s"%full_file)
            for chunk in data.iter_content(chunksize):
                fd.write(chunk)

        #DEBUG
        return self._parse_csv_data(full_file)

    def _parse_csv_data(self,csv_data_file):
        """
        return iterable csv reader object

        """
        logging.debug("parsing csv data %s")
        data_arr = []
        try:
            csvfile  = open(csv_data_file)
            #need to skip first row
            csvfile.readline()
            csvfile.readline()
            print "skipping first 2 lines"
            reader = csv.DictReader(csvfile,self.CSV_KEYS)
            for row in reader:
                data_arr.append(row)
            csvfile.close()
            return data_arr
        except Exception,e:
            logging.error("unable to find file or key %s"%e)
        finally:
            csvfile.close()
