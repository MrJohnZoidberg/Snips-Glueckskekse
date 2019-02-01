#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import configparser
import io
import paho.mqtt.client as mqtt
import json
import random

CONFIG_INI = "config.ini"
FORTUNE_TOPICS = ["tips", "sprueche", "wusstensie", "murphy", "fussball", "bahnhof",
                  "ms", "letzteworte", "regeln", "quiz", "sprichworte", "unfug", "witze",
                  "warmduscher", "zitate", "kinderzitate", "doppelsinnig", "lieberals"]


def read_configuration_file(configuration_file):
    try:
        cp = configparser.ConfigParser()
        with io.open(configuration_file, encoding="utf-8") as f:
            cp.read_file(f)
        return {section: {option_name: option for option_name, option in cp.items(section)}
                for section in cp.sections()}
    except (IOError, configparser.Error):
        return dict()


conf = read_configuration_file(CONFIG_INI)

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
        client.unsubscribe("hermes/asr/textCaptured")
        data = json.loads(msg.payload.decode("utf-8"))
        if data['text'] == "":
            session_id = data['sessionId']
            end(session_id)
            if fortunes.question_repetitions < fortunes.max_question_repetitions:
                fortunes.question_repetitions += 1
                client.subscribe("hermes/asr/textCaptured")
                start("Noch ein Spruch?", ["domi:confirmOtherCookie"])
            else:
                client.unsubscribe("hermes/intent/domi:confirmOtherCookie")
                client.unsubscribe("hermes/nlu/intentNotRecognized")
    elif msg.topic ==  'hermes/nlu/intentNotRecognized':
        client.unsubscribe("hermes/nlu/intentNotRecognized")
        data = json.loads(msg.payload.decode("utf-8"))
        session_id = data['sessionId']
        end(session_id)
        if fortunes.question_repetitions < fortunes.max_question_repetitions:
            fortunes.question_repetitions += 1
            client.subscribe("hermes/asr/textCaptured")
            client.subscribe("hermes/nlu/intentNotRecognized")
            start("Noch ein Spruch?", ["domi:confirmOtherCookie"])
        else:
            client.unsubscribe("hermes/intent/domi:confirmOtherCookie")
    elif msg.topic == 'hermes/intent/domi:confirmOtherCookie':
        client.unsubscribe("hermes/nlu/intentNotRecognized")
        client.unsubscribe("hermes/intent/domi:confirmOtherCookie")
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
    client.subscribe("hermes/nlu/intentNotRecognized")
    fortunes.question_repetitions = 0
    dialogue(session_id, result_sentence, ["domi:confirmOtherCookie"])


def say(session_id, text):
    mqtt_client.publish('hermes/dialogueManager/endSession', json.dumps({'text': text, "sessionId": session_id}))


def start(text, intent_filter):
    mqtt_client.publish('hermes/dialogueManager/startSession',
                        json.dumps({'init': {'type': "action", 'text': text, 'canBeEnqueued': True,
                                    'intentFilter': intent_filter}}))


def end(session_id):
    mqtt_client.publish('hermes/dialogueManager/endSession', json.dumps({"sessionId": session_id}))


def dialogue(session_id, text, intent_filter):
    mqtt_client.publish('hermes/dialogueManager/continueSession',
                        json.dumps({'text': text, "sessionId": session_id, "intentFilter": intent_filter}))


class Fortunes:
    def __init__(self, config, topics):
        self.topics = topics
        if 'fortunes_max_laenge' in config['global'].keys():
            self.max_length = config['global']['fortunes_max_laenge']
            if not self.max_length:
                self.max_length = 100
            else:
                self.max_length = int(self.max_length)
        else:
            self.max_length = 100
        if 'max_frage_wdh' in config['global'].keys():
            self.max_question_repetitions = config['global']['max_frage_wdh']
            if not self.max_question_repetitions:  # if dictionaray not filled with values
                self.max_question_repetitions = 1
            else:
                self.max_question_repetitions = int(self.max_question_repetitions)
        else:
            self.max_question_repetitions = 1
        self.all_fortunes = {}
        self.fortunes_status = None
        self.last_topic = None
        self.question_repetitions = 0

    def read_files(self):
        try:
            fortunes_dict = {}
            for topic in self.topics:
                with io.open("de/" + topic, 'r') as f:
                    fortunes_dict[topic] = f.read().encode('utf8').split(b'%')
                cookies = []
                for cookie in fortunes_dict[topic]:
                    if self.max_length >= len(cookie) > 1:
                        cookies.append(cookie)
                fortunes_dict[topic] = cookies  # without cookies over maximum length
            self.all_fortunes = fortunes_dict
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
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    mqtt_client.connect("localhost", "1883")
    mqtt_client.loop_forever()
