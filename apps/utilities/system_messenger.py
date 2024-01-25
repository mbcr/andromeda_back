import os
import requests
import logging
from django.conf import settings

def dispatch(message:str):
    logger = logging.getLogger('system_messenger')
    # Fetch config variables
    bot_identifier = settings.SYSTEM_MESSENGER_BOT
    target_chat_id = settings.SYSTEM_MESSENGER_TARGET_CHAT_ID 

    if not message:
        print('No message provided')
        logger.error('dispatch: No message provided')
        return
    api_url = 'https://api.telegram.org/bot'
    api_method='/sendMessage'
    def send_message(message_str: str):
        message_parameters = {
            'chat_id': target_chat_id,
            'text': message_str
        }
        logger.info(f"Message sent: {message_str}")
        response = requests.get(api_url+bot_identifier+api_method, params=message_parameters, timeout=4)
        return response.json()

    try:
        send_message(message)
    except Exception as e:
        logger.error(f"An error occurred while sending the message: {e}")
        return






