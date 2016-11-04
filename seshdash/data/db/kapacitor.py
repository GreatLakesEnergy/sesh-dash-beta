import requests
import json
import logging

# Django specific settings
from django.conf import settings


logger = logging.getLogger(__name__)

class Kapacitor:

    HOST = 'localhost'
    PORT =  9092

    _ENDPOINTS = {
            'template': 'kapacitor/v1/templates',
            'get_template': 'kapacitor/v1/templates/{template_id}',
            'tasks' : 'kapacitor/v1/tasks',
            'ping' : 'kapacitor/v1/ping'
            }
    _REQUEST_URL  = "http://{host}:{port}/{path}"

    IS_INITIALIZED = False

    def __init__(self):
        """
        Kapacitor API method object used to call kapacitor
        tasks through

        @param host - hostname kapacitor is running on
        @param port - port kapacitor is listening

        """

        self.HOST = settings.KAPACITOR_HOST
        self.PORT = settings.KAPACITOR_PORT

        ping = self._make_request('ping', type_of_request='GET')

        if ping[0] == 204:
            logger.debug ("Kapacitor initialized")
            self.IS_INITIALIZED = True
        else:
            logger.error("Kapacitor couldn't connect to host %s %s"%ping)

    def get_template(self, template_id):
        """
        Get information on template that's already been created

        @param template_id -  Unique indentifier used for template to fetch

        """

        data = {'template_id':template_id }
        re = self._make_request('get_template', path_params = data, type_of_request='GET')
        logger.debug("got response %s %s"%re)
        return re[1]

    def delete_template(self, template_id):
        """
        Delete template that's already been created

        @param template_id -  Unique indentifier used for template to fetch

        """

        data = {'template_id':template_id }
        re = self._make_request('get_template', path_params = data, type_of_request='DELETE')
        logger.debug("got response %s %s"%re)
        return re[1]


    def list_templates(self,pattern='',fields=[]):
        """
        List template that's already been created

        @param template_id -  Unique indentifier used for template to fetch

        """
        data = {}
        if pattern:
            data['pattern'] = pattern
        if fields:
            data['fields'] = fields

        re = self._make_request('template', data = data, type_of_request='GET')
        logger.debug("got response %s %s"%re)
        return re[1]




    def create_template(self, template_id, template_type,  template_script):
        """
        Use this method to create or modify TICK script templates for jobs

        @param template_id -  Unique indentifier used for template
        @param template_stype -  The template type: stream or batch.
        @param template_script -  The content of the script.

        """

        data_dict  = {
                'id': template_id,
                'type': template_type,
                'script': template_script
                }

        re = self._make_request('template', data=data_dict)
        logger.debug("got response %s %s"%re)
        return re[1]

    def update_template(self, template_id, template_script):
        """
        Update existing template

        @param template_id -  Unique indentifier used for template
        @param template_script -  The content of the script you wish to update

        """

        data_dict  = {'script': template_script }
        path_params = {'template_id' : template_id}

        re = self._make_request('get_template',
                                data=data_dict,
                                type_of_request='PATCH',
                                path_params=path_params)

        logger.debug("got response %s %s"%re)
        return re[1]




    def _make_request(self, endpoint, data = {}, type_of_request='POST', path_params={}):
        """
        helper function to handle requests and responses

        @param endpoint - which endpoint to use for kapacitor
        @param data - data to append to the POST request in the form of a dictionary
        @param type_of_request - POST or GET
        """
        path = self._ENDPOINTS.get(endpoint,None).format(**path_params)

        endpoint_to_send = self._REQUEST_URL.format(
                host = self.HOST,
                port = self.PORT,
                path = path
                )

        logger.debug("Sending request type %s : %s"% (type_of_request, endpoint_to_send))
        logger.debug("with data %s"%data)
        if type_of_request.lower() == "post":
            r = requests.post(endpoint_to_send, json=data)
        elif type_of_request.lower() == "get":
            r = requests.get(endpoint_to_send, params=data)
        elif type_of_request.lower() == "patch":
            r = requests.patch(endpoint_to_send, json=data)
        elif type_of_request.lower() == "delete":
            r = requests.delete(endpoint_to_send, data=data)



        try:
            return (r.status_code, r.json())
        except ValueError, e:
            return (r.status_code, {})

        #TODO bring in proper logging
        #logger.exception("Recieved error code %s"% r.status_code)
        #logger.exception("Message %s"%r.response)



