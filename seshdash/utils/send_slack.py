""" 
For sending messages to Slack
"""
# Python libs
import logging

from django.conf import settings

from slacker import Slacker


class Slack():
    
    def __init__(self):
        self.slack_client = Slacker(settings.SLACK_KEY)
        
    def send_message_to_channel(self, channel, message):
        """ Sends a message to a slack channel """
        if channel[0] == '#':
            pass
        else:
            channel = '#' + channel
     
        try:
            self.slack_client.chat.post_message(channel, message)
        except Exception, e: 
            print 'Slack Channel not found'
            logging.error('Slack Channel not Found')
            return False

        return True
        

