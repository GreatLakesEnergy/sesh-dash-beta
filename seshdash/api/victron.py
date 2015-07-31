import requests, json, logging
import urllib3
class VictronAPI:
    #API_BASE_URL = "http://juice.m2mobi.com/{call_type}/{function}"
    API_BASE_URL = "https://juice.victronenergy.com/{call_type}/{function}"

    API_HIST_LOGIN_URL = "https://vrm.victronenergy.com/user/login"
    API_HIST_FETCH_URL = "https://vrm.victronenergy.com/site/download-csv/site/{SITE_ID}/start_time/{START_TIME}/end_time/{END_TIME}"
    USERNAME = ""
    PASSWORD = ""

    SESSION_ID = ""
    VERIFICATION_TOKEN = "seshdev"

    API_VERSION = "220"
    SYSTEMS_IDS = []
    ATTRIBUTE_DICT = {}

    FORMAT = "json"
    IS_INITIALIZED = False

    """
    Provide API key and User Key to get started
    more info here:https://developer.enphase.com/docs/quickstart.html

    """
    def __init__(self , user_name, user_password, format_type=json):
        #TODO disabling sl warnings
        requests.packages.urllib3.disable_warnings()

        self.USERNAME = user_name
        self.PASSWORD = user_password

        self.initialize()
        if self.IS_INITIALIZED:
            print "system initialized"
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
                response="requests",
                username=self.USERNAME,
                password=self.PASSWORD)
        if response.status_code == 403:
            logging.error("Access denied unable to initialize \nresponse: %s:" %response)
            self.IS_INITIALIZED = False
        if response.status_code== 200:
            response_parsed = response.json()
            if response_parsed.has_key("data"):
                self.SESSION_ID = response_parsed["data"]["user"]["sessionid"]
                v_sites = self.get_site_list()
                print "gettin site list"
                for site in v_sites:
                    self.SYSTEMS_IDS.append((site['idSite'],site['name']))
                    logging.info("initializing sites, getting attributes")
                    atr = self.get_site_attributes_list(site['idSite'])
                    #make attribute dictionary more usefull
                    atr [site['idSite']] =  atr['attributes']
                    self.ATTRIBUTE_DICT = self._reformat_attr_dict(atr)
                    self.IS_INITIALIZED = True
            else:
                logging.error("Problem getting session id")
                self.IS_INITIALIZED = False
        else:
                logging.error("other error while initializing %s"% response.status_code)


    """
    reformat attribute dic so it's easier to use
    """
    def _reformat_attr_dict(self,atr_dict):
        flatten_dict = {}
        for site in  self.SYSTEMS_IDS:
            flat = {}
            c =  map(lambda x:{x['customLabel']:x},atr_dict[site[0]])
            for val in c:
                flat[val.keys()[0]] = val[val.keys()[0]]
            flatten_dict[site[0]] = flat
        return flatten_dict

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
        logging.debug(data)
        if  data:
            r = requests.post(formated_URL,data=data, headers = headers)
        else:
            r = requests.post(formated_URL, headers = headers)
        if r.status_code == 200:
            if response == "json":
                return r.json()
            else:
                return r
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
    Get the
    """
    def get_system_stats(self,site_id):
        code_arr = []
        code_arr.append(self.ATTRIBUTE_DICT[site_id]['VE.Bus state'])
        code_arr.append(self.ATTRIBUTE_DICT[site_id]['Input power 1'])
        code_arr.append(self.ATTRIBUTE_DICT[site_id]['AC Input 1 '])
        code_arr.append(self.ATTRIBUTE_DICT[site_id]['Input frequency 1'])
        code_arr.append(self.ATTRIBUTE_DICT[site_id]['Output power 1'])
        code_arr.append(self.ATTRIBUTE_DICT[site_id]['AC Consumption L1'])
        code_arr.append(self.ATTRIBUTE_DICT[site_id]['Input voltage phase 1'])
        code_arr.append(self.ATTRIBUTE_DICT[site_id]['Output current phase 1'])
        code_arr.append(self.ATTRIBUTE_DICT[site_id]['Output voltage phase 1'])
        return self.get_site_attribute(site_id,code_arr)

    """
    Get the battery stats:
    """
    def get_battery_Stats(self,site_id):
        code_arr = []
        code_arr.append(self.ATTRIBUTE_DICT[site_id]['Battery State of Charge (System)'])
        code_arr.append(self.ATTRIBUTE_DICT[site_id]['Battery Current (System)'])
        code_arr.append(self.ATTRIBUTE_DICT[site_id]['Battery voltage'])
        code_arr.append(self.ATTRIBUTE_DICT[site_id]['Battery Power (System)'])
        code_arr.append(self.ATTRIBUTE_DICT[site_id]['Battery state'])
        return self.get_site_attribute(site_id,code_arr)


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

    IS_HIST_INITIALIZED = False

    def __init__(self , user_name, user_password, timezone=-4,dl_fldr="/tmp"):
         requests.packages.urllib3.disable_warnings()
         self.USERNAME = user_name
         self.PASSWORD = user_password
         self.DOWNLOAD_FOLDER = dl_fldr
         self.TIMEZONE = timezone
         self.SESSION = requests.Session()
         self.initialize()

    def initialize(self):
         data= {}
         data['password'] = self.PASSWORD
         data['username'] = self.USERNAME
         data['local_timezone'] = self.TIMEZONE
         data['is_dst'] = 0

         r = self.SESSION.post(self.API_HIST_LOGIN_URL,data=data)
         self.SESSION_COOKIES = r.cookies

         if r.status_code == 200:
                self.IS_HIST_INITIALIZED = True
                logging.info("Victron historical API initialized")

    def get_data(self,site_id,start_at,end_at):
        """
        Will download a csv containt all data for provided seconds from epoch time window.
        """
        chunksize = 10
        filename = self.DOWNLOAD_FOLDER
        formated_URL = self.API_HIST_FETCH_URL.format(
               SITE_ID = site_id,
               START_AT = start_at,
               END_AT = end_at
                )
        headers  = {'user-agent':self.USER_AGENT}
        data = self.SESSION.get(formated_URL,headers=headers)
        print data.text
        with open(filename, 'wb') as fd:
            for chunk in data.iter_content(chunksize):
                fd.write(chunk)
                print writing chunks to file



