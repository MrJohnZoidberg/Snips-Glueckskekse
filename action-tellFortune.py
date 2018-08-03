#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import ConfigParser
import io
import paho.mqtt.client as mqtt
import json
import random

CONFIGURATION_ENCODING_FORMAT = "utf-8"
CONFIG_INI = "config.ini"
FORTUNE_TOPICS = ["tips", "sprueche", "wusstensie", "murphy", "fussball", "bahnhof",
                  "ms", "letzteworte", "regeln", "quiz", "sprichworte", "unfug", "witze",
                  "warmduscher", "zitate", "kinderzitate", "doppelsinnig", "lieberals"]


class SnipsConfigParser(ConfigParser.SafeConfigParser):
    def to_dict(self):
        return {section: {option_name: option for option_name, option in self.items(section)} for section in self.sections()}


def read_configuration_file(configuration_file):
    try:
        with io.open(configuration_file, encoding=CONFIGURATION_ENCODING_FORMAT) as f:
            conf_parser = SnipsConfigParser()
            conf_parser.readfp(f)
            return conf_parser.to_dict()
    except (IOError, ConfigParser.Error) as e:
        return dict()


conf = read_configuration_file(CONFIG_INI)
print("Conf:", conf)

# MQTT client to connect to the bus
mqtt_client = mqtt.Client()


def on_connect(client, userdata, flags, rc):
    client.subscribe("hermes/intent/domi:tellFortune")


def on_message(client, userdata, msg):
    if msg.topic == 'hermes/intent/domi:tellFortune':
        data = json.loads(msg.payload.decode("utf-8"))
        session_id = data['sessionId']
        slots = {slot['slotName']: slot['value']['value'] for slot in data['slots']}
        if fortunes.fortunes_status:
            action_wrapper(client, slots, session_id)
        else:
            result_sentence = "Fehler: Glückskekse konnten nicht eingelesen werden. Bitte schaue in der Beschreibung" \
                              "dieser App nach, wie man Fortunes installiert."
            say(session_id, result_sentence)
    elif msg.topic == 'hermes/asr/textCaptured':
        data = json.loads(msg.payload.decode("utf-8"))
        if data['text'] == "":
            session_id = data['sessionId']
            print("Trying to end session...")
            end(session_id)
            start("Noch ein Spruch?", ["domi:confirmOtherCookie"])
    elif msg.topic == 'hermes/intent/domi:confirmOtherCookie':
        data = json.loads(msg.payload.decode("utf-8"))
        session_id = data['sessionId']
        slots = {slot['slotName']: slot['value']['value'] for slot in data['slots']}
        answer = slots['answer']
        if "yes" in answer:
            action_wrapper(client, slots, session_id)
        else:
            fortunes.last_topic = None
            end(session_id)


def action_wrapper(client, slots, session_id):
    if 'topic' in slots:
        topic = slots['topic'].lower()
        fortunes.last_topic = topic
    elif fortunes.last_topic:
        topic = fortunes.last_topic
    else:
        topic = None
    result_sentence = fortunes.say(topic)
    client.subscribe("hermes/intent/domi:confirmOtherCookie")
    client.subscribe("hermes/asr/textCaptured")
    dialogue(session_id, result_sentence, ["domi:confirmOtherCookie"])


def say(session_id, text):
    mqtt_client.publish('hermes/dialogueManager/endSession', json.dumps({'init': {'text': text, "sessionId": session_id}}))

def start(text, intent_filter):
    mqtt_client.publish('hermes/dialogueManager/startSession',
                        json.dumps({'type': "action", 'text': text, 'canBeEnqueued': True,
                                    'intentFilter': intent_filter}))

def end(session_id):
    mqtt_client.publish('hermes/dialogueManager/endSession', json.dumps({"sessionId": session_id}))


def dialogue(session_id, text, intent_filter):
    mqtt_client.publish('hermes/dialogueManager/continueSession',
                        json.dumps({'text': text, "sessionId": session_id, "intentFilter": intent_filter}))


class Fortunes:
    def __init__(self, config, topics):
        self.topics = topics
        try:
            self.max_length = int(config['global']['fortunes_max_laenge'])
        except KeyError:
            self.max_length = 100
        self.all_fortunes = {}
        self.fortunes_status = None
        self.last_topic = None

    def read_files(self):
        try:
            fortunes = {}
            for topic in self.topics:
                with io.open("de/" + topic, 'r') as f:
                    fortunes[topic] = f.read().encode('utf8').split('%')
                cookies = []
                for cookie in fortunes[topic]:
                    if self.max_length >= len(cookie) > 1:
                        cookies.append(cookie)
                fortunes[topic] = cookies  # without cookies over maximum length
            self.all_fortunes = fortunes
            return 1  # status is ok
        except IOError as e:
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
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    mqtt_client.connect("localhost", "1883")
    mqtt_client.loop_forever()
