#-*- coding utf8 -*-

from enum import Enum
from vk_api.bot_longpoll import VkBotEventType
import random

# ---- some decorators ----


def respect(func):
    respect_texts = [
        'Конечно, ',
        'Секунду, ',
        'Готов служить, ',
        'В вашем распоряжении, ',
    ]

    def wrapper(self, event):
        text = random.choice(respect_texts)
        if event.user.sex == 2:
            text = text + "сэр."
        else:
            text = text + "госпожа!"
        self.server.send_message(event.chat.id, text)
        func(self, event)
    return wrapper


# ---- handlers ----

# You should inherite basic class
# Redefine method handle or pair of methods: check and process
# Use meta variables to set behaviour of your handler


class MessageHandler:
    __text_only__ = True
    __admin_only__ = False
    __process_and_pass__ = False

    def __init__(self, server):
        self.server = server

    def meta_handle(self, event):
        if self.__class__.__text_only__:
            if not event.message or not event.message.text:
                return False
        if self.__class__.__admin_only__:
            if not event.user.is_admin:
                return False

        return self.handle(event) and not self.__class__.__process_and_pass__

    def handle(self, event):
        res = self.check(event)
        if res:
            self.process(event)
        return res

    def check(self, event):
        return self.__class__.__process_and_pass__

class StatesMessageHandler(MessageHandler):
    # You should implement this part of inherited classes

    States = Enum('States', 'NONE')

    def check_start(self, event):
        return False

    processers = {
        States.NONE: check_start
    }

    # ----

    def __init__(self, server):
        super().__init__(server)
        self.chats = {}

    def handle(self, event):
        cid = event.chat.id
        if cid not in self.chats:
            self.chats[cid] = self.__class__.States.NONE

        return self.processers[self.chats[cid]](self, event)

    def set_state(self, event, state):
        self.chats[event.chat.id] = state

    def reset_state(self, event):
        self.chats[event.chat.id] = self.__class__.States.NONE

