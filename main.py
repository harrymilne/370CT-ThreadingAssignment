from threading import Thread, Condition, active_count
from time import sleep
import random

DELAY = 1
DISTANCE = 5

##wheel initialisation
WHEEL_NO = 6
WHEEL_SENSORS = [None] * WHEEL_NO ##shared memory

##states
STATE = None
MOVE_TYPES = ["LIFT_WHEEL", "LOWER_WHEEL", "CALL_HOME", "REVERSE"]
ERRORS = ["FREEWHEEL", "BLOCKED", "SINKING"]
SOLUTIONS = {
    "FREEWHEEL": ["LOWER_WHEEL"],
    "BLOCKED": ["LIFT_WHEEL", "REVERSE", "LOWER_WHEEL"],
    "SINKING": ["LIFT_WHEEL"]
}

class RandomError:
    def __init__(self):
        self.wheel = random.randint(0, WHEEL_NO - 1)
        self.err = ERRORS[random.randint(0, len(ERRORS) - 1)]

class Runtime(Thread):
    global STATE
    def __init__(self, cv, threads, distance=5):
        global STATE
        Thread.__init__(self)
        self.cv = cv
        self.threads = threads
        self.distance = distance

        self.traveled = 0
        STATE = "VECTOR"

    def run(self):
        global STATE
        errs = []
        while self.traveled < self.distance:
            with self.cv:
                while STATE != "VECTOR":
                    self.cv.wait()
                print("VECTOR thread running...")
                ##readability delay
                sleep(DELAY)
                ##error occured?
                err_toss = random.randint(0, 1)
                if err_toss:
                    ##generate multiple? errors 
                    errs = [RandomError() for i in range(1, 3)]
                    ##show errors occurred
                    print("Error occurred! {} on wheels {}.".format(
                        ", ".join([err.err for err in errs]), 
                        ", ".join([str(err.wheel) for err in errs])
                    ))
                    ##for each error occurred
                    for err in errs:
                        attempts = 0
                        fixed = False
                        while not fixed and attempts < 5:
                            print("Attempt {}".format(attempts + 1))
                            for action in SOLUTIONS[err.err]:
                                STATE = action
                                self.threads[action].set_motor(err.wheel)
                                self.cv.notify_all()
                                while STATE != "VECTOR":
                                    self.cv.wait()
                                fixed = bool(random.randint(0, 1)) ##random y/n
                                if fixed:
                                    ##break from solution attempts
                                    print("Solution succeeded!")
                                    break
                                else:
                                    print("Solution failed... Retrying...")
                                attempts += 1

                        ##if error unfixable from onboard attempts
                        if not fixed and attempts > 4:
                            print("Max attempts reached, calling home...")
                            ##switch to CH thread
                            STATE = "CALL_HOME"
                            self.cv.notify_all()
                            while STATE != "VECTOR":
                                self.cv.wait()
                else:
                    self.traveled += 1
                    print("Successfully vectored 1m... ({}/{})".format(self.traveled, self.distance))

        ##shutdown and notify threads
        with self.cv:
            STATE = None ##setting STATE to None tells threads to join
            self.cv.notify_all()

##default task
class Task(Thread):
    def __init__(self, cv, move_type):
        Thread.__init__(self)
        self.cv = cv
        self.thread_type = move_type
        self.motor_id = None

    def set_motor(self, wheel_no):
        self.motor_id = wheel_no

    def reset_motor(self):
        self.motor_id = None

    def run(self):
        global STATE
        while STATE:
            with self.cv: ##acquire condition
                while STATE and STATE != self.thread_type: ##while bot alive + not passing to this thread; wait
                    self.cv.wait()
                if STATE == self.thread_type: ##if thread switched to, run logic
                    if self.motor_id:
                        print("{} thread running on motor {}... (id:{})".format(self.thread_type, self.motor_id, self.ident))
                    else:
                        print("{} thread running... (id:{})".format(self.thread_type, self.ident))
                    sleep(DELAY)
                    STATE = "VECTOR" ##return back to main runtime
                    self.cv.notify_all()
        print("{} thread (id:{}) terminated.".format(self.thread_type, self.ident))


if __name__ == "__main__":
    print("Welcome to the Mars Rover interface.")
    print("This is running on the default python interpreter thread ;)")
    print("\tOptions")
    print("\t1. Run with default options (vector: {}m, thread delay: {}s)".format(DISTANCE, DELAY))
    print("\t\tBy default, exceptions are raised by random.")
    print("\t2. Enter your own variables")
    option_selected = False
    vars_set = True

    while not option_selected:
        op = raw_input("[1]: ")
        print
        if op in ["", "1"]:
            print("Default selected, random errors and vector {}m with {}s delay.".format(DISTANCE, DELAY))
            option_selected = True
        elif op == "2":
            print("Custom selected, proceeding to variable selection...")
            option_selected = True
            vars_set = False

    print

    while not vars_set:
        try:
            secs = abs(int(raw_input("\tEnter how many seconds you would like the threads to sleep for each switch: ")))
            vect = abs(int(raw_input("\tEnter how far the bot must vector before terminating: ")))
            vars_set = True
        except ValueError:
            print("Please enter integers.")
            continue
        DELAY = secs
        DISTANCE = vect

    print

    cv = Condition()
    threads = {}
    for state in MOVE_TYPES:
        t = Task(cv, state)
        threads[state] = t

    main = Runtime(cv, threads, DISTANCE)
    main.start()

    for thread in threads.values():
        thread.start()

    print("{} threads spawned.".format(active_count() - 1))

    for thread in threads.values():
        thread.join()

    main.join()

