import schedule


class CroneMessages:
    def __init__(self, server):
        self.server = server

    def handle(self):
        res = self.check()
        if res:
            self.process()

    def check(self):
        return True


class Scheduler(CroneMessages):
    def check(self):
        # check if me online
        return False

    def process(self):
        today = get_today_date
        schedule.get_schedule(today)
        # send schedule
