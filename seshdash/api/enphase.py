import requests, json, logging
from lxml import html
from datetime import datetime

logger = logging.getLogger(__name__)

class EnphaseAPI:
    API_BASE_URL = "https://api.enphaseenergy.com/api/v2/systems/{system_id}/{function}?key={key}&user_id={user_id}"
    API_BASE_URL_INDEX = "https://api.enphaseenergy.com/api/v2/systems/?key={key}&user_id={user_id}"
    FORMAT = "json"

    """
    Provide API key and User Key to get started
    more info here:https://developer.enphase.com/docs/quickstart.html

    """
    def __init__(self , key, user_id, format_type=json):
        self.IS_INITIALIZED = False
        self.SYSTEMS_IDS = {}
        self.SYSTEMS_INFO = {}
        self.KEY = key
        self.FORMAT =  format_type
        self.USER_ID = user_id

        self._initialize()
        if self.IS_INITIALIZED:
            print "system initialized"
            logger.info("System Initialized with %s systems"%len(self.SYSTEMS_IDS))
        else:
            logger.error("unable to initialize the api")
    """
    Initialization function This will talk to enphase and get aall system ids
    """
    def _initialize(self):
        formatedURL = self.API_BASE_URL_INDEX.format(
                    key = self.KEY,
                    user_id = self.USER_ID,
                )
        response = requests.get(formatedURL)
        #check that everything is good with the request here
        if response.status_code == 401:
            logger.error("Access denied unable to initialize \nresponse: %s:" %response)
            self.IS_INITIALIZED = False
        if response.status_code== 200:
            response_parsed = response.json()
            if response_parsed.has_key("systems"):
                for system in response_parsed['systems']:
                    #extract the system id, we'll need this later
                    self.SYSTEMS_IDS[system["system_id"]] = system['system_name']
                    #Get System summary for each site so we can get critical system stats:
                    sys_sum = self.get_summary(system["system_id"])
                    self.SYSTEMS_INFO[system["system_id"]] = sys_sum

                self.IS_INITIALIZED = True
            else:
                logger.warning("No systems registerd")
                self.SYSTEMS_IDS = []
                self.IS_INITIALIZED = False

    """
    clean up results before returning them
    """
    def parse_response(self,response_json):
        parsed = json.loads(response_json)
        return parsed

    """
    Utility function to prepare our requests before sending them
    """
    def make_request(self,function_name,system_id,**kwargs):
        #format string with our paramters can do this with requests as well
        formatedURL = self.API_BASE_URL.format(
                    system_id = system_id,
                    key = self.KEY,
                    user_id = self.USER_ID,
                    function = function_name
                )

        r = requests.get(formatedURL,params=kwargs)
        print r.url
        return r.json()

    """
    Get system summary
    @param:  summary_date: Get summary for this date (optional)
    """
    def get_summary(self,system_id,summary_date=None):
        if summary_date:
            return self.make_request("summary",system_id,summary_date=summary_date)
        return self.make_request("summary",system_id)

    """
    Get system stats for provided system_id
    optional start end endtime times (isoformat) will give stats within that interval
    @params: system_id
             start_date  (optional)
             end_date (mandatory if start_date  provided)
    """

    def get_stats(self,system_id,start=0,end=0,datetime_format='epoch'):
        if start and end:
            print "#systemid %s start %s end %s"%(system_id,start,end)
            return self.make_request(function_name="stats",
                                     system_id=system_id,
                                    start_at=start,
                                    end_at=end,
                                    datetime_format=datetime_format)
        if start:
            print "#systemid %s start %s end %s"%(system_id,start,end)
            return self.make_request(function_name="stats",
                                     system_id=system_id,
                                    start_at=start,datetime_format=datetime_format)

        return self.make_request("stats",system_id,datetime_format=datetime_format)

    """
    return monthly production from start date
    @params: start_data
    """
    def get_monthly_production(self,system_id,start_date):
         return self.make_request("monthly_production",system_id,start_date=start_date)




<<<<<<< Updated upstream
class EnphaseLocalAPI:

	_ENVOY_IP = '0.0.0.0'
	_IS_INTIALIZED = False

	_ENVOY_URL = 'http://{ip}/{path}?locale=en'
	_CURRENT_DATA = {}

	_XPATH_DICT = {
			'current_production':'/html/body/div[1]/table/tr[2]/td[2]/text()',
			'today_production':'/html/body/div[1]/table/tr[3]/td[2]/text()',
			'past_week_production':'/html/body/div[1]/table/tr[4]/td[2]/text()',
			'since_installation_production':'/html/body/div[1]/table/tr[5]/td[2]/text()'
			}


	def __init__(self, ip ):
		self._ENVOY_IP = ip

		self._initialize()

		if self._IS_INTIALIZED:
			logger.info('ENHPASE LOCAL API initialised')

	def _initialize(self):

		formated_url = self._ENVOY_URL.format(ip = self._ENVOY_IP,path = 'production')
		envoy_page  = requests.get(formated_url)
		page_html = html.fromstring(envoy_page.text)

		if envoy_page.status_code == 200:
			print "API initialized getting data"
			self._CURRENT_DATA = self._parse_production_data(page_html)
			self._IS_INTIALIZED = True
		else:
			logger.error("unable to initialize API error: %s"%envoy_page.status_code)
			self._IS_INTIALIZED = False

	def _parse_production_data(self,page_html):

		parsed_result = {'':datetime.now()}

		for key in self._XPATH_DICT.keys():
			value = page_html.xpath(self._XPATH_DICT[key])
			parsed_result[key] = value[0].strip()
		return parsed_result

	def get_current_prod_data(self):
		return self._CURRENT_DATA




=======
>>>>>>> Stashed changes
