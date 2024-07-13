# from time import sleep
# import threading
# from _thread import interrupt_main
# import sys
# from io import StringIO


# class CustomThread(threading.Thread):
#     def __init__(self, *args, **kwargs):
#         super(CustomThread, self).__init__(*args, **kwargs)
#         self._stopper = threading.Event()

#     def stop(self):
#         self._stopper.set()

#     def stopped(self):
#         return self._stopper.is_set()

#     def run(self):
#         sleep(5)
#         while not self.stopped():
#             interrupt_main()


# def runCode(code, myglobals):
#     oldStdOUT = sys.stdout
#     redirectedOutput = sys.stdout = StringIO()
#     oldStdERR = sys.stderr
#     redirectedOutput2 = sys.stderr = StringIO()
#     result = ""
#     thread = CustomThread()
#     try:
#         thread.start()
#         exec(code, myglobals)
#         result = redirectedOutput.getvalue()
#     except Exception as e:
#         # print(repr(e))
#         result = repr(e)
#     except SystemExit as s:
#         # print(repr(s))
#         result = redirectedOutput2.getvalue()
#     except KeyboardInterrupt as k:
#         result = "timed out"
#     thread.stop()
#     myglobals.popitem()
#     sys.stdout = oldStdOUT
#     sys.stderr = oldStdERR
#     # print(result)
#     # print("maaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")

#     return result

import threading
import sys
from io import StringIO
from time import sleep


class CustomThread(threading.Thread):
    def __init__(self, *args, **kwargs):
        super(CustomThread, self).__init__(*args, **kwargs)
        self._stopper = threading.Event()
        self.exc_info = None

    def stop(self):
        self._stopper.set()

    def stopped(self):
        return self._stopper.is_set()
    
    def start(self, code, myglobals):
        self._stopper.clear()
        self.run(code, myglobals)

    def run(self, code, myglobals):
        try:
            sleep(5)
            if not self.stopped():
                # Simulate an exception
                raise TimeoutError("Execution timed out")
            # Execute the code
            exec(code, myglobals)
        except Exception as e:
            self.exc_info = sys.exc_info()
        except TimeoutError as e:
            result = "Execution timed out"

def runCode(code, myglobals):
    oldStdOUT = sys.stdout
    redirectedOutput = sys.stdout = StringIO()
    oldStdERR = sys.stderr
    redirectedOutput2 = sys.stderr = StringIO()
    result = ""
    thread = CustomThread()
    try:
        thread.start(code, myglobals)
        # thread.join(5.1)  # Wait for the thread to finish with a timeout
        if thread.exc_info:
            # Re-raise the exception
            raise thread.exc_info[0](thread.exc_info[1]).with_traceback(thread.exc_info[2])
        result = redirectedOutput.getvalue()
    except Exception as e:
        # print(repr(e))
        result = repr(e)
        # result = ""
    finally:
        thread.stop()
        myglobals.popitem()
        sys.stdout = oldStdOUT
        sys.stderr = oldStdERR
    return result
