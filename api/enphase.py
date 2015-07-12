import requests, json, logging

class EnphaseAPI:
    API_BASE_URL = "https://api.enphaseenergy.com/api/v2/systems/{system_id}/{function}?key={key}&user_id={user_id}"
    API_BASE_URL_INDEX = "https://api.enphaseenergy.com/api/v2/systems/?key={key}&user_id={user_id}"
    KEY = ""
    SYSTEMS_IDS = []
    USER_ID = ""
    FORMAT = "json"
    IS_INITIALIZED = False

    """
    Provide API key and User Key to get started
    more info here:https://developer.enphase.com/docs/quickstart.html

    """
    def __init__(self , key, user_id, format_type=json):
        self.KEY = key
        self.FORMAT =  format_type
        self.USER_ID = user_id

        self.initialize()
        if self.IS_INITIALIZED:
            print "system initialized"
            logging.info("System Initialized with %s systems"%len(self.SYSTEMS_IDS))
        else:
            logging.error("unable to initialize the api")

    def initialize(self):
        formatedURL = self.API_BASE_URL_INDEX.format(
                    key = self.KEY,
                    user_id = self.USER_ID,
                )
        response = requests.get(formatedURL)

        if response.status_code == 401:
            logging.error("Access denied unable to initialize \nresponse: %s:" %response)
            self.IS_INITIALIZED = False
        if response.status_code== 200:
            response_parsed = response.json()
            if response_parsed.has_key("systems"):
                for system in response_parsed['systems']:
                    self.SYSTEMS_IDS.append(system["system_id"])
                self.IS_INITIALIZED = True
            else:
                logging.warning("No systems registerd")
                self.SYSTEMS_IDS = []
                self.IS_INITIALIZED = False

    def parse_response(self,response_json):
        parsed = json.loads(response_json)
        return parsed


    def make_request(self,function_name,system_id,**kwargs):
        #format string with our paramters can do this with requests as well
        formatedURL = self.API_BASE_URL.format(
                    system_id = system_id,
                    key = self.KEY,
                    user_id = self.USER_ID,
                    function = function_name
                )

        r = requests.get(formatedURL,params=kwargs)
        return r.json()

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


