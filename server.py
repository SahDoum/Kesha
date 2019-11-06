import vk_api.vk_api

from vk_api.bot_longpoll import VkBotLongPoll

import random
from enrich_event import EnrichEvent

import datetime

alextours_id = 2000000001
shit_id = -120534549
my_id = 10819599

class Server:
    def __init__(self, api_token, group_id, server_name: str="Empty"):
        self.server_name = server_name
        self.vk = vk_api.VkApi(token=api_token)
        self.long_poll = VkBotLongPoll(self.vk, group_id, wait=20)
        self.vk_api = self.vk.get_api()

        self.handlers = []

    def start(self):
        # create new thread for crone operations

        for event in self.long_poll.listen():
            if event.object.from_id == shit_id:
                continue

            enrich_event = EnrichEvent(event, self)

            start = datetime.datetime.now()
            prev = start
            for h in self.handlers:
                try:
                    if h.meta_handle(enrich_event):
                        now = datetime.datetime.now()
                        print(h.__class__, now - prev)
                        prev = now
                        break
                    now = datetime.datetime.now()
                    print(h.__class__, now - prev)
                    prev = now
                except Exception as e:
                    self.traceback(e)

            now = datetime.datetime.now()
            print("Total: ", now - start)

    def register(self, classname):
        handler = classname(self)
        self.handlers.append(handler)

    def register_with_crone(self, classname, crone):
        # future implementation
        return

    def send_message(self, peer_id, message, **kwargs):
        self.vk_api.messages.send(
            peer_id=peer_id,
            message=message,
            random_id=random.randint(0, 2**32),
            **kwargs
        )

    def traceback(self, error):
        if not error:
            return

        text = 'Сэр, что-то пошло не так. Я перезапущен и снова работоспособен. Логи об ошибках:\n{}\n{}'.format('-' * 10, error)

        print(error)
        self.send_message(my_id, text)
