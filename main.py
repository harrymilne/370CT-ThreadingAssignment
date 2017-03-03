from threading import Thread, Condition
from time import sleep
import random

##wheel initialisation
WHEEL_NO = 6
WHEEL_SENSORS = [None] * WHEEL_NO ##shared memory

##states
C_STATE = None
MOVE_TYPES = ["LIFT_WHEEL", "LOWER_WHEEL", "CALL_HOME", "REVERSE"]
ERRORS = ["FREEWHEEL", "STUCK", ""]
SOLUTIONS = {
    "FREEWHEEL": ["LIFT_WHEEL", "LOWER_WHEEL"],
    "STUCK": ["REVERSE"]
}

class RandomError:
    def __init__(self):
        self.wheel = random.randint(0, WHEEL_NO)
        self.err = random.randint(0, len(ERRORS))

class Runtime(Thread):
    global C_STATE
    def __init__(self, cv):
        global C_STATE
        super().__init__()
        self.cv = cv
        C_STATE = "VECTOR"

    def run(self):
        global C_STATE
        errs = []
        while True:
            with self.cv:
                while C_STATE != "VECTOR":
                    self.cv.wait()
                C_STATE = "VECTOR"
                print("Vectoring...")
                sleep(1)
                err_toss = random.randint(0, 1)
                if err_toss: 
                    err = RandomError()
                    C_STATE = MOVE_TYPES[random.randint(0, len(MOVE_TYPES)-1)]
                    self.cv.notify_all()

    def freewheel(self):
        pass

    def stuck(self):
        pass

##default task
class Movement(Thread):
    def __init__(self, cv, move_type):
        super().__init__()
        self.cv = cv
        self.thread_type = move_type

    def run(self):
        global C_STATE
        while True:
            with self.cv:
                while C_STATE != self.thread_type:
                    self.cv.wait()
                C_STATE = self.thread_type
                print("{} thread running...".format(self.thread_type))
                sleep(1)
                C_STATE = "VECTOR"
                self.cv.notify_all()

if __name__ == "__main__":
    cv = Condition()
    main = Runtime(cv)
    threads = []
    for state in MOVE_TYPES:
        t = Movement(cv, state)
        t.start()
        threads.append(t)
    main.start()

