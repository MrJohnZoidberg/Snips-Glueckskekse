#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import ConfigParser
from hermes_python.hermes import Hermes
from hermes_python.ontology import *
import io
import random

CONFIGURATION_ENCODING_FORMAT = "utf-8"
CONFIG_INI = "config.ini"
FORTUNE_TOPICS = ["tips", "sprueche", "wusstensie", "murphy", "fussball", "bahnhof",
                  "ms", "letzteworte", "regeln", "quiz", "sprichworte", "unfug", "witze",
                  "warmduscher", "zitate", "kinderzitate", "doppelsinnig", "lieberals"]

class SnipsConfigParser(ConfigParser.SafeConfigParser):
    def to_dict(self):
        return {section : {option_name : option for option_name, option in self.items(section)} for section in self.sections()}

def read_configuration_file(configuration_file):
    try:
        with io.open(configuration_file, encoding=CONFIGURATION_ENCODING_FORMAT) as f:
            conf_parser = SnipsConfigParser()
            conf_parser.readfp(f)
            return conf_parser.to_dict()
    except (IOError, ConfigParser.Error) as e:
        return dict()

def subscribe_intent_callback(hermes, intentMessage):
    user,intentname = intentMessage.intent.intent_name.split(':')  # the user can fork the intent with this method
    if intentname == "tellFortune":
        if fortunes.fortunes_status:
            conf = read_configuration_file(CONFIG_INI)
            action_wrapper(hermes, intentMessage, conf)
        else:
            result_sentence = "Fehler: Glückskekse konnten nicht eingelesen werden. Bitte schaue in der Beschreibung dieses Skills nach, wie man Fortunes installiert."
            hermes.publish_end_session(intentMessage.session_id, result_sentence)
    elif intentname == "confirmOtherCookie":
        if "confirmOtherCookie" in fortunes.wanted_intents:
            fortunes.wanted_intents = []
            answer = intentMessage.slots.answer.first().value
            if "yes" in answer:
                conf = read_configuration_file(CONFIG_INI)
                action_wrapper(hermes, intentMessage, conf)
            else:
                fortunes.last_topic = None
                hermes.publish_end_session(intentMessage.session_id, "")

def action_wrapper(hermes, intentMessage, conf):
    """ Write the body of the function that will be executed once the intent is recognized. 
    In your scope, you have the following objects : 
    - intentMessage : an object that represents the recognized intent
    - hermes : an object with methods to communicate with the MQTT bus following the hermes protocol. 
    - conf : a dictionary that holds the skills parameters you defined 
    """
    if intentMessage.slots.topic.all():
        topic = intentMessage.slots.topic.first().value.lower()
        fortunes.last_topic = topic
    elif fortunes.last_topic:
        topic = fortunes.last_topic
    else:
        topic = None
    result_sentence = fortunes.say(topic)
    fortunes.wanted_intents = ["confirmOtherCookie"]
    current_session_id = intentMessage.session_id
    hermes.publish_continue_session(current_session_id, result_sentence, ["domi:confirmOtherCookie"])

class Fortunes:
    def __init__(self, config, topics):
        self.wanted_intents = []
        self.topics = topics
        self.max_length = config['global']['fortunes_max_laenge']
        self.all_fortunes = {}
        self.fortunes_status = None
        self.last_topic = None

    def read_files(self):
        try:
            fortunes = {}
            for topic in self.topics:
                with io.open("/usr/share/games/fortunes/de/" + topic, 'r') as f:
                    fortunes[topic] = f.read().encode('utf8').split('%')
                cookies = []
                for cookie in fortunes[topic]:
                    # TODO: Lengths are not shorter than before...
                    print("max_length:", self.max_length)
                    if len(cookie) <= self.max_length:
                        cookies.append(cookie)
                fortunes[topic] = cookies  # without cookies over maximum length
            self.all_fortunes = fortunes
            return 1  # status is ok
        except IOError:
            return 0  # error

    def say(self, topic):
        cookies = []
        if topic:
            cookies = self.all_fortunes[topic]
        while not cookies:
            topic = random.choice(self.topics)
            cookies = self.all_fortunes[topic]
        if topic == "witze":
            right_cookies = []
            for cookie in cookies:
                if "--" not in cookie:  # quotes will be deleted (not funny)
                    right_cookies.append(cookie)
            cookies = right_cookies
        random_cookie = random.choice(cookies).replace('\n', ' ')
        response = "{cookie} . Noch ein Spruch?".format(cookie=random_cookie)
        return response
        
if __name__ == "__main__":
    fortunes = Fortunes(read_configuration_file(CONFIG_INI), FORTUNE_TOPICS)
    fortunes.fortunes_status = fortunes.read_files()
    with Hermes("localhost:1883") as h:
        h.subscribe_intents(subscribe_intent_callback).start()
