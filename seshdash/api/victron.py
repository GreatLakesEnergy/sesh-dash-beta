import requests, json, logging

class VictronAPI:
    #API_BASE_URL = "http://juice.m2mobi.com/{call_type}/{function}"
    API_BASE_URL = "https://juice.victronenergy.com/{call_type}/{function}"
    USERNAME = ""
    PASSWORD = ""

    SESSION_ID = ""
    VERIFICATION_TOKEN = "seshdev"

    API_VERSION = "220"
    SYSTEMS_IDS = []

    FORMAT = "json"
    IS_INITIALIZED = False

    """
    Provide API key and User Key to get started
    more info here:https://developer.enphase.com/docs/quickstart.html

    """
    def __init__(self , user_name, user_password, format_type=json):
        self.USERNAME = user_name
        self.PASSWORD = user_password

        self._initialize()
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
    def _initialize(self):
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
                self.IS_INITIALIZED = True
            else:
                logging.error("Problem getting session id")
                self.IS_INITIALIZED = False
        else:
                logging.error("other error while initializing %s"% response.status_code)

    """
    Utility function perhaps deleet this
    """
    def _parse_response(self,response_json):
        parsed = json.loads(response_json)
        return parsed

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
        print data
        if  data:
            r = requests.post(formated_URL,data=data, headers = headers)
        else:
            r = requests.post(formated_URL, headers = headers)
        if response == "json":
            return r.json()
        else:
            return r

    """
    Get system list
    """
    def get_site_list(self):
         if self.IS_INITIALIZED:
            return self._make_request("sites","get")

    """
    Get system stats for provided system_id
    @params: site_id
    """
    def get_site_stats(self,site_id):
         return self._make_request("sites","get_site",siteid=site_id)

    """
    return monthly production from start date
    @params: site_id
    """
    def get_energy_data(self,site_id):
         return self._make_request("sites","get_energy_data", siteid=site_id, instance = 0)

    """
    Get all associated attributes with a site
    @params: site_id
    """
    def get_site_attributes_list(self,site_id):
         return self._make_request("sites","get_site_attributes", siteid=site_id, instance = 0)

    """
    Get all attribute data from  with a site
    @params: site_id, attribute_code
    """
    def get_site_attribute(self,site_id,attribute_code_arr):
         return self._make_request("sites","attributes_by_code",codes=attribute_code_arr, siteid=site_id, instance = 0)


