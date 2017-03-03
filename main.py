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
        self.wheel = random.randint(0, WHEEL_NO - 1)
        self.err = random.randint(0, len(ERRORS) - 1)

class Runtime(Thread):
    global C_STATE
    def __init__(self, cv, distance=5):
        global C_STATE
        super().__init__()
        self.cv = cv
        self.traveled = 0
        self.distance = distance
        C_STATE = "VECTOR" ##initial bot state

    def run(self):
        global C_STATE
        errs = []
        while self.traveled < self.distance:
            with self.cv:
                while C_STATE != "VECTOR":
                    self.cv.wait()
                print("Vectoring...")
                sleep(1)
                err_toss = random.randint(0, 1)
                if err_toss: 
                    err = RandomError()
                    print("Error occurred! {} on wheel {}.".format(ERRORS[err.err], err.wheel))
                    C_STATE = MOVE_TYPES[random.randint(0, len(MOVE_TYPES)-1)]
                    self.cv.notify_all()
                else:
                    self.traveled += 1
                    print("Successfully vectored 1m... ({}/{})".format(self.traveled, self.distance))

        ##shutdown and notify threads
        with self.cv:
            C_STATE = None ##setting C_STATE to None tells threads to join
            self.cv.notify_all()

##default task
class Movement(Thread):
    def __init__(self, cv, move_type):
        super().__init__()
        self.cv = cv
        self.thread_type = move_type

    def run(self):
        global C_STATE
        while C_STATE:
            with self.cv: ##acquire condition
                while C_STATE and C_STATE != self.thread_type: ##while bot alive + not passing to this thread; wait
                    self.cv.wait()
                if C_STATE == self.thread_type: ##if thread switched to, run logic
                    print("{} thread running...".format(self.thread_type))
                    sleep(1)
                    C_STATE = "VECTOR" ##return back to main runtime
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

    for thread in threads:
        thread.join()
    main.join()

