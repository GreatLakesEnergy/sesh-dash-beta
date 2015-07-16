import requests, json, logging

class VictronAPI:
    #API_BASE_URL = "http://juice.m2mobi.com/{call_type}/{function}"
    API_BASE_URL = "https://juice.victronenergy.com/{call_type}/{function}"
    USERNAME = ""
    PASSWORD = ""

    SESSION_ID = ""
    VERIFICATION_TOKEN = ""

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
        login_payload = {
                         'version':self.API_VERSION,
                         'username':self.USERNAME,
                         'password':self.PASSWORD,
                         'verification_token':self.API_VERSION
                        }
        response  = self.make_request("user","login",response="requests",data=login_payload)
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

    def parse_response(self,response_json):
        parsed = json.loads(response_json)
        return parsed

    """
    Utiliy function to make requsts.
    Will return json or request based on response parameter
    Data needs to be passed with data keyword
    """
    def make_request(self,call_type,function,response="json",**data):
        #format string with our paramters can do this with requests as well

        formated_URL = self.API_BASE_URL.format(call_type=call_type,function=function)

        headers = {"content-type":" application/x-www-form-urlencoded"}
        if  data:
            r = requests.post(formated_URL,data=data["data"], headers = headers)
        else:
            r = requests.post(formated_URL, headers = headers)
        if response == "json":
            return r.json()
        else:
            return r

    """
    Get system summary
    """
    def get_summary(self,system_id):
         return self.make_request("summary",system_id)

    """
    Get system stats for provided system_id
    """
    def get_stats(self,system_id):
         return self.make_request("stats",system_id)

    """
    return monthly production from start date
    @params: start_data
    """
    def get_monthly_production(self,system_id,start_date):
         payload = {"start_date":start_date}
         return self.make_request("monthly_production",system_id, payload)


