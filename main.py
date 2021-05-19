from slack import RTMClient
import requests
import os
from os.path import join, dirname
from dotenv import load_dotenv
import traceback

# Authenticate with slacker

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)
SLACK_TOKEN = os.environ.get("SLACK_TOKEN_")
JOKE_API_URL = os.environ.get("JOKE_API_URL_")




@RTMClient.run_on(event="message")
def amusebot(**payload):
    """
    This function triggers when someone sends
    a message on the slack
    """
    data = payload["data"]
    web_client = payload["web_client"]
    bot_id = data.get("bot_id", "")
    subtype = data.get("subtype", "")
    try:
        if bot_id == "" and subtype == "":
            channels = web_client.conversations_list()['channels']
            idS = []
            for channel in channels:
                idS.append(channel['id'])  
            channel_id = data["channel"]
            
            text = ''
            callBot = False
            for block in data['blocks']:
                for element in block["elements"]:
                    for e in element["elements"]:
                        if e['type']=='text':
                            text = e['text']
                        elif e['type']=='user':
                            callBot = True
            if not callBot and channel_id in idS:
                return
            params = list(filter(None, text.split(" ")))
            if len(params) != 2:
                response ='You must enter 2 parameters text (Search text) language (cs, de, en, es, fr, pt)'
            else:
                contains = params[0].strip()
                lang = params[1].strip()
            
                joke_json_response = requests.get(JOKE_API_URL+"?lang="+lang+"&contains="+contains).json()
    
                if joke_json_response['error']:
                    response = joke_json_response['message']
                else:
                    if joke_json_response['type']=='twopart':
                        response = joke_json_response['setup']+'\n'+joke_json_response['delivery']
                    else:
                        response = joke_json_response['joke']
            web_client.chat_postMessage(channel=channel_id, text=response,reply_broadcast=False)
    except Exception:
        traceback.print_exc()

try:
    rtm_client = RTMClient(token=SLACK_TOKEN)
    print("Bot is up and running!")
    rtm_client.start()
except Exception :
    traceback.print_exc()