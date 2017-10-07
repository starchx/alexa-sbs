"""
This SBS Alexa skill demonstrates a simple skill built with the Amazon Alexa Skills Kit.
The Intent Schema, with AWS Lambda service
"""

from __future__ import print_function

import json
import datetime
import calendar
import pytz


# --------------- Helpers that build all of the responses ----------------------

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': "SessionSpeechlet - " + title,
            'content': "SessionSpeechlet - " + output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }

def build_audio_response(title, output, reprompt_text, should_end_session, audio_action, audio_url):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': "SessionSpeechlet - " + title,
            'content': "SessionSpeechlet - " + output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        "directives": [
            {
                "type": "AudioPlayer." + audio_action,
                "playBehavior": "REPLACE_ALL",
                "audioItem": {
                    "stream": {
                        "token": "this-is-the-audio-token",
                        "url": audio_url,
                        "offsetInMilliseconds": 0
                    }
                }
            }
        ],
        'shouldEndSession': should_end_session
    }

def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }


# --------------- Functions that control the skill's behavior ------------------

def get_welcome_response():
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """

    session_attributes = {}
    card_title = "Welcome"
    speech_output = "Welcome to Alexa SBS Skill. " \
                    "You can start by saying, " \
                    "today's news in Mandarin, or " \
                    "yesterday's news in English."
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "Please tell me what you want to hear by saying, " \
                    "today's news in Mandarin, or " \
                    "yesterday's news in English."
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = "Thank you for trying the SBS Alexa Skills. " \
                    "Have a nice day! "
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    audio_action = "Stop"

    return build_response({}, build_audio_response(
        card_title, speech_output, None, should_end_session, audio_action, None))


def play_sbs_news(intent, session):
    session_attributes = {}
    reprompt_text = None
    should_end_session = True
    audio_action = "Play"

    try:
        slot_language = intent['slots']['Language']['value'].lower()
    except KeyError:
        slot_language = "mandarin"

    sbs_news_time_dict = {
        "mandarin": "07",
        "english": "18",
        "vietnamese": "19",
        "korean": "21"
    }
    
    try:
        slot_when = intent['slots']['When']['value']
        slot_date = datetime.datetime.strptime(slot_when, "%Y-%m-%d").date()
    except KeyError:
        slot_date = datetime.datetime.now(pytz.timezone('Australia/Sydney'))
    
    # Handel supportted languages
    if slot_language not in sbs_news_time_dict:
        speech_output = slot_language + " is currently not supported. " \
                        "Currently supported languages are: "
        for key in sbs_news_time_dict:
            speech_output += key + ", "
        speech_output += "Please try again."
        should_end_session = False
        return build_response(session_attributes, build_speechlet_response(
                intent['name'], speech_output, reprompt_text, should_end_session))

    # Handle date and News mp3 file availability
    slot_weekday = calendar.day_name[slot_date.weekday()]
    #current_datetime = datetime.datetime.now(pytz.timezone('Australia/Sydney'))

    # All good - proceed to play
    speech_output = "Playing SBS " + slot_weekday + " News in " + slot_language

    audio_file = slot_weekday + "_ONDemand_SBS_RADIO1_" + sbs_news_time_dict[slot_language] + "_00.mp3"
    audio_url = "https://media.sbs.com.au/ondemand/audio/" + audio_file
    
    return build_response(session_attributes, build_audio_response(
        intent['name'], speech_output, reprompt_text, should_end_session, audio_action, audio_url))


# --------------- Events ------------------

def on_session_started(session_started_request, session):
    """ Called when the session starts """

    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """

    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_welcome_response()


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    print("on_intent intent variable: ")
    print(json.dumps(intent, indent = 4))

    # Dispatch to your skill's intent handlers
    if intent_name == "SBSNewsIntent":
        return play_sbs_news(intent, session)
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or \
         intent_name == "AMAZON.StopIntent" or \
         intent_name == "AMAZON.PauseIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.

    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here


# --------------- Main handler ------------------

def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("event.session.application.applicationId=" +
            event['session']['application']['applicationId'])
    """
    Uncomment this if statement and populate with your skill's application ID to
    prevent someone else from configuring a skill that sends requests to this
    function.
    """
    #if (event['session']['application']['applicationId'] !=
    #        "amzn1.ask.skill.9d43b814-44eb-4ff5-af92-942d369dfca9"):
    #    raise ValueError("Invalid Application ID")

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])
