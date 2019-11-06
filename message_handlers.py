#-*- coding utf8 -*-

import config
from handlers_lib import MessageHandler, StatesMessageHandler, respect
import users
import schedule

from collections import deque
from datetime import datetime, timedelta
from enum import Enum
import os
import re
import random


reboot_texts = [
    'Перезагружаюсь, сэр!',
    'Отключаюсь, сэр. Надеюсь мы встретимся снова.',
    'Ухожу в ребут.',
    'С вами было приятно работать, сэр! Отключаюсь.'
]


class CommonMessageHandler(MessageHandler):
    def check(self, event):
        return event.user.id == event.chat.id

    def process(self, event):
        if event.user.is_admin:
            self.server.send_message(event.chat.id, "Не разобрал вас, сэр.")
        else:
            self.server.send_message(event.chat.id, "Привет, пёс! Ничё не пнл.")


class AppealHandler(MessageHandler):
    def check(self, event):
        return not not event.facts.appeals

    def process(self, event):
        for appeal in event.facts.appeals:
            name = appeal.name
            if appeal.comma:
                name += ','
            appeal_words = ['Да,', name, appeal.start, appeal.end]
            text = ' '.join(filter(None.__ne__, appeal_words))
            self.server.send_message(event.chat.id, text)


class CommandsHandler(MessageHandler):
    def check(self, event):
        return event.facts.commands \
               and any(command.markall for command in event.facts.commands)

    @respect
    def process(self, event):
        for command in event.facts.commands:
            if command.markall:
                self.markall(event)

    def markall(self, event):
        text = users.get_alextours_markup()
        self.server.send_message(event.chat.id, text)


class AdminCommandsHandler(MessageHandler):
    __admin_only__ = True

    def check(self, event):
        return event.facts.admin_commands \
               and any(command.reboot for command in event.facts.admin_commands)

    @respect
    def process(self, event):
        for command in event.facts.admin_commands:
            if command.reboot:
                self.reboot(event)

    def reboot(self, event):
        text = random.choice(reboot_texts)
        self.server.send_message(event.chat.id, text)
        os.execl('/bin/bash', 'bash', 'bot_update.sh')


class ResendHandler(StatesMessageHandler):
    __admin_only__ = True

    resend_id = config.alextours_id

    States = Enum('States', 'NONE LISTENING')

    def check_start(self, event):
        if event.facts.admin_commands \
           and any(command.resend for command in event.facts.admin_commands):
            self.server.send_message(event.chat.id, "Слушаю, сэр.")
            self.set_state(event, self.States.LISTENING)
            return True
        return False

    def listen(self, event):
        attachments = ','.join(event.message.attachments)
        self.server.send_message(self.resend_id, event.message.text, attachment=attachments)
        self.reset_state(event)

    processers = {
        States.NONE: check_start,
        States.LISTENING: listen
    }


class KeshaHandler(MessageHandler):
    def check(self, event):
        return (event.message.text == "Кеша, спасибо" or event.message.text == "Спасибо, Кеша")

    def process(self, event):
        if (event.user.sex == 2):
            text = "Рад служить, сэр."
        else:
            text = "Рад служить, госпожа!"
        self.server.send_message(event.chat.id, text, reply_to=event.message.id)


class VovaDoeba(MessageHandler):
    __process_and_pass__ = True

    def __init__(self, server):
        super().__init__(server)

        self.stoptime = datetime.now()
        self.downtime = timedelta(hours=2)
        self.in_work = True

    def process(self, event):
        # if self.stoptime + self.downtime < datetime.now():
        #     self.in_work = True
        #
        # if event.user.is_admin and event.message.text == "Кеша, перестань":
        #     self.server.send_message(event.chat.id, "Простите, сэр.")
        #     self.stoptime = datetime.now()
        #     self.in_work = False
        #     return True

        if self.in_work and random.randint(0, 30) == 0:
            text = event.message.text
            space_count = len(text.split())-1
            if space_count < 3:
                return

            text = self.filter(text)
            self.server.send_message(event.chat.id, text)

    @staticmethod
    def filter(text):
        defect_dict = {
            r'р' : 'л',
            r'ч' : 'т',
            r'з' : 'д',
            r'ж' : 'з',
            r'с' : 'ш',
            r'ао' : 'я',

            # r'(?<=[лтмдмс])о' : 'ё',
            r'(?<=[лтдмнс])э' : 'е',
            r'(?<=[лтдмнс])ы' : 'и',
            r'(?<=[лтдмнс])у' : 'ю',
            r'(?<=[лтдмнс])а' : 'я',

            r'([лтдмнс](?![аеёиоуыэюяьъ]))' : r'\1ь',
        }

        for key, rep in defect_dict.items():
            text = re.sub(key, rep, text, flags=re.IGNORECASE)

        return text


class Elektrybałt(MessageHandler):
    __process_and_pass__ = True

    def process(self, event):
        if not event.message.words:
            return

        great_answers = {
            "да": "Пизда.",
            "нет": "Пидора ответ.",
            "da": "Pizda.",
            "net": "Faggot otvet.",
        }

        last_word = event.message.words[-1].lower()
        if last_word in great_answers:
            self.server.send_message(event.chat.id, great_answers[last_word])


class BuyElephant(MessageHandler):
    def __init__(self, server):
        super().__init__(server)

        self.victim = None
        self.messages_count = 0
        self.potential_victims = {}

    def handle(self, event):
        if not self.select_victim(event.user.id):
            return False

        text = self.create_answer(event)
        if self.messages_count == 0 or len(event.facts.elephant) > 0 or random.randint(0, 1) == 0:
            self.server.send_message(event.chat.id, text, reply_to=event.message.id)
            self.messages_count += 1
            return True
        else:
            return False

    def select_victim(self, user_id):
        victim_history_len = self.update_user_history(self.victim, False)
        user_history_len = self.update_user_history(user_id, True)

        # check if current victim stil current
        if victim_history_len == 0:
            self.victim = None

        # check if new user could be victim
        if not self.victim and user_history_len > 5:
            self.victim = user_id
            self.messages_count = 0
            return True

        if self.victim == user_id:
            return True

        return False

    def create_answer(self, event):
        if self.messages_count == 0:
            return "{}, купи слона!".format(event.user.name)
        if any(elephant.agreement for elephant in event.facts.elephant):
            self.potential_victims[self.victim].clear()
            self.victim = None
            return "Отлично, {}, вот здесь слона посмотри:\nhttps://market.yandex.ru/search?text=слон".format(event.user.name)
        if any(elephant.disagreement for elephant in event.facts.elephant):
            return "Ну как же так, {}, слон всем нужен!".format(event.user.name)
        return "{}, все говорят {}, а ты купи слона!".format(event.user.name, event.message.text)

    def update_user_history(self, user_id, new_message=False):
        if not user_id:
            return 0

        if user_id not in self.potential_victims:
            self.potential_victims[user_id] = deque()

        now = datetime.now()
        while len(self.potential_victims[user_id]) > 0 \
              and now - self.potential_victims[user_id][0] > timedelta(minutes=3):
            self.potential_victims[user_id].popleft()

        if new_message:
            self.potential_victims[user_id].append(now)

        return len(self.potential_victims[user_id])



# class ScheduleSetter(MessageHandler):
#     __text_only__ = True

#     def __init__(self, server):
#         self.server = server

#     def check(self, event):
#         # check command
#         return False

#     def process(self, event):
#         sc_time = self.get_date(event.text)
#         res = schedule.get_schedule(sc_time)

#         res = "{}".format(res)
#         self.server.send_message(event.chat.id, res)
#         return

#     def get_date(self, text):
#         # future implementation
#         return None
