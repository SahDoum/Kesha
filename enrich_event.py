#-*- coding utf8 -*-
import re
from vk_api.bot_longpoll import VkBotEventType

admin_id = 10819599

class Map(dict):
    """dot.notation access to dictionary attributes"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


class EnrichEvent:
    parsers = {}

    def __init__(self, event, server):
        user_id = event.object.from_id

        print('Object:', event.object)
        # print('Event: ', event)

        self.event = event
        self.type = event.type

        self.parse_message()
        self.parse_user(server)

        self.chat = Map({
            'id': event.object.peer_id,
        })

        self.facts = Map()
        if self.message and self.message.text:
            for name, parser in EnrichEvent.parsers.items():
                self.facts[name] = []
                for match in parser.findall(self.message.text):
                    print(match.fact)
                    self.facts[name].append(match.fact)

    @staticmethod
    def register(name, parser):
        print('Register parser:', name)
        EnrichEvent.parsers[name] = parser

    def parse_message(self):
        if self.event.type != VkBotEventType.MESSAGE_NEW:
            self.message = None
            return

        self.message = Map()
        self.message['id'] = self.event.object.id
        self.parse_text()
        self.parse_attachments()

    def parse_user(self, server):
        user_id = self.event.object.from_id

        user_info = server.vk_api.users.get(user_id=user_id, fields='sex')[0]

        self.user = Map({
            'id': user_id,
            'name': user_info['first_name'],
            'sex': user_info['sex'],
            'is_admin': (user_id == admin_id)
        })
        try:
            self.user['city'] = server.vk_api.users.get(user_id=user_id, fields="city")[0]["city"]['title']
        except Exception:
            self.user['city'] = None

    def parse_text(self):
        self.message['text'] = self.event.object.text
        self.message['type'] = self.event.type
        self.message['words'] = re.findall(r'(?:\b[а-яА-Яa-zA-Z]+\b)', self.event.object.text)

    def parse_attachments(self):
        self.message['attachments'] = []
        for attach in self.event.object.attachments:
            try:
                type = attach['type']
                attach_str = "{}{}_{}_{}".format(
                    type,
                    attach[type]['owner_id'],
                    attach[type]['id'],
                    attach[type]['access_key']
                    )
                self.message.attachments.append(attach_str)
            except Exception as e:
                print('Attachmentt exception: ', e)
