"""
For sending messages to Slack
"""
# Python libs
import logging

from django.conf import settings

from slacker import Slacker


# Instantiating the logger
logger = logging.getLogger(__name__)

class Slack():

    def __init__(self, auth_token):
        """
        Instantiates the slack api
        """
        self.slack_client = Slacker(auth_token)

    def send_message_to_channel(self, channel, message):
        """ 
        Sends a message to a slack channel 
        """
        if channel[0] == '#':
            pass
        else:
            channel = '#' + channel


        try:
            # Posting the message
            self.slack_client.chat.post_message(channel, message)
            return True
        except Exception, e:
            # Try creating the channel and post the message
            logger.warning('Slack channel not found, System trying to create one')            
        
            try:
                self.slack_client.channels.create(channel)
                self.slack_client.chat.post_message(channel, message)
            except Exception, e:
                logger.error('Slack Error: Try checking the auth token if is valid')
                logger.error('Slack Error message %s' % e)
            return True

        return False
