from threading import Thread, Condition
from time import sleep

##wheel initialisation
WHEEL_NO = 6
WHEEL_SENSORS = [None] * WHEEL_NO ##shared memory

class MonitorTask(Thread):
    def __init__(self):
        super().__init__()
        self.WHEEL_ERRS = {
            "freewheel": self.freewheel,
            "stuck": self.stuck,
            "": None
        }

    def run(self):
        errs = []
        while True:
            print(WHEEL_SENSORS)
            for wheel in WHEEL_SENSORS:
                if WHEEL_SENSORS[wheel] in self.WHEEL_ERRS:
                    errs.append((wheel, self.WHEEL_ERRS[WHEEL_SENSORS[wheel]]))

            if len(errs) > 0:
                print(WHEEL_SENSORS)

            sleep(1)

    def freewheel(self):
        pass

    def stuck(self):
        pass

##default task
class NavigateTask(Thread):
    def run(self):
        sleep(5)

if __name__ == "__main__":
    nav = NavigateTask()
    mon = MonitorTask()
    nav.start()
    mon.start()
    sleep(3)
    WHEEL_SENSORS[0] = "freewheel"

