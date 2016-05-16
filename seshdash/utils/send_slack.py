""" 
For sending messages to Slack
"""
# Python libs
import logging

from django.conf import settings

from slacker import Slacker


class Slack():
    
    def __init__(self, auth_token):
        self.slack_client = Slacker(auth_token)
        
    def send_message_to_channel(self, channel, message):
        """ Sends a message to a slack channel """
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
            self.slack_client.channels.create(channel)
            self.slack_client.chat.post_message(channel, message)
            logging.error('Slack Channel not Found')
            return True

        return False
        

