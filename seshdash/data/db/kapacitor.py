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
            'get_tasks' : 'kapacitor/v1/tasks/{task_id}',
            'ping' : 'kapacitor/v1/ping',
            'recordings': 'kapacitor/v1/recordings/{method}',
            'a_recording': 'kapacitor/v1/recordings/{recording_id}',
            'list_recordings': 'kapacitor/v1/recordings'
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


    def create_task(self, task_id, script='', dbrps=[{}] ,template_id=None, task_type='stream', status='enabled', task_vars = {} ):
        """
        Create a task based on a new sript or already existing template.

        @param task_id - unique string for task
        @param script - TICK Script for task if not using template
        @param template_id - template id if usig template instead of new tick script
        @param task_type -  type of task 'batch' or 'stream'
        @param status - weather to create the task as 'enabled' or 'disabled'
        @param task_vars - Varbiables if any that should get over written when creating a task from a template.
        """

        data_dict  = {
                      'id': task_id,
                      'status' :  status,
                      'vars' : task_vars,
                      'dbrps' : dbrps
                       }

        if template_id:
                data_dict['template-id '] = template_id
        else:
                data_dict['script'] = script
                data_dict['type' ] =  task_type

        re = self._make_request('tasks',
                                data=data_dict,
                                )

        logger.debug("got response %s %s"%re)
        return re[1]



    def get_task(self, task_id ):
        """
        Get details on a specific task that's been created

        @param task_id - unique string for task to retrieve
        """

        data_dict  = {
                      'task_id': task_id,
                       }


        re = self._make_request('get_tasks',
                                type_of_request = 'GET',
                                path_params = data_dict
                                )

        logger.debug("got response %s %s"%re)
        return re[1]


    def list_tasks(self, pattern=''):
        """
        List the current tasks in kapacitor
        @param pattern - This specifies a pattern to query kapacitor with, Note: it uses go pattern matching syntax
        """
        data_dict = {
            'pattern': pattern,
        }
         
        re = self._make_request('tasks', 
                                type_of_request = 'GET',
                                path_params = data_dict,
                                )

        logger.debug("got response %s %s" % re)
        return re[1]



    def update_task(self, task_id ):
        """
        Get details on a specific task that's been created

        @param task_id - unique string for task to retrieve
        """

        data_dict  = {
                      'task_id': task_id,
                       }


        re = self._make_request('get_tasks',
                                type_of_request = 'PATCH',
                                path_params = data_dict
                                )

        logger.debug("got response %s %s"%re)
        return re[1]




    def delete_task(self, task_id ):
        """
        Delete a created task

        @param task_id - unique string for task to delete
        """

        data_dict  = {
                      'task_id': task_id
                       }


        re = self._make_request('get_tasks',
                                type_of_request = 'DELETE',
                                path_params = data_dict
                                )

        logger.debug("got response %s %s"%re)
        return re[1]


    def delete_all_tasks(self):
        """
        Delete all the tasks in kapacitor
        """
        tasks = self.list_tasks()
         
        for task in tasks["tasks"]:
            self.delete_task(task['id'])
 
        return True


    def create_recording(self, task_id, stop, method='stream', id=None):
        """
        Creates a kapacitor recording

        @param task_id - id of a task, used to only record for the dbrps of the task
        @param method - the method to use, stream, batch or query
        @param stop - the time to stop recording data
        @param id - the id to give to the recording, not required

        TODO: This should also support batch and query methods
        """
        data = {
                     'task': task_id,
                     'stop': stop.isoformat() + 'Z',                   
                      }

        
        re = self._make_request('recordings',
                                type_of_request = 'POST',
                                path_params = {'method': method},
                                data = data
                               )
 
        logger.debug("got response %s %s" % re)
        return re[1]

    def get_recording(self, recording_id):
        """
        Returns the status of a recording
      
        @param recording_id - a recording id 
        """
        re = self._make_request('a_recording', 
                                type_of_request='GET',
                                path_params={'recording_id': recording_id}
                               )
  
        logger.debug("got response %s %s" % re)
        return re[1]
     
    def delete_recording(self, recording_id):
        """
        Deletes a kapacitor recording
  
        @param recording_id - a recording id
        """
        re = self._make_request('a_recording', 
                                type_of_request='DELETE',
                                path_params={'recording_id': recording_id}
                               )

        logger.debug("got response %s %s" % re)
        return re[1]

    def list_recordings(self):
        """
        Retuns a list of all kapacitor recordings
        """
        re = self._make_request('list_recordings', 
                                type_of_request='GET',
                                path_params={'method': ''}
                               )

        logger.debug("got response %s %s" % re)
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
        if data:
            logger.debug("with data %s"%json.dumps(data))
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



