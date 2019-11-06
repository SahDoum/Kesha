#-*- coding utf8 -*-

from server import Server
import message_handlers
import crone_messages

import kesha_grammatics

import config

import os


def register_handlers(server):
    server.register(message_handlers.KeshaHandler)
    server.register(message_handlers.VovaDoeba)
    server.register(message_handlers.BuyElephant)
    server.register(message_handlers.Elektrybałt)

    server.register(message_handlers.AdminCommandsHandler)
    server.register(message_handlers.CommandsHandler)
    server.register(message_handlers.AppealHandler)
    server.register(message_handlers.ResendHandler)

    # server.register(message_handlers.ScheduleSetter)
    # server.register_with_crone(crone_messages.Scheduler, "")

    server.register(message_handlers.CommonMessageHandler)


current_error = None
while __name__ == "__main__":
    try:
        server = Server(config.vk_api_token, 120534549, "server1")
        register_handlers(server)

        server.traceback(current_error)
        current_error = None

        server.start()
    # добавить кэтч HTTPSConnectionPool
    except KeyboardInterrupt as e:
        os._exit(0)
    except Exception as e:
        current_error = e
        print(e)
