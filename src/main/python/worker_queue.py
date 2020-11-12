from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

import time
import traceback, sys

# class WorkerSignals(QObject):
#     finished = pyqtSignal()
#     error = pyqtSignal(tuple)
#     result = pyqtSignal(object)
#     progress = pyqtSignal(int)

# class Worker(QRunnable):
#     def __init__(self, fn, name, *args, **kwargs):
#         super(Worker, self).__init__()
#         self.fn = fn
#         self.name = name
#         self.args = args
#         self.kwargs = kwargs
#         self.signals = WorkerSignals()

#     @pyqtSlot()
#     def run(self):
#         try:
#             result = self.fn(*self.args, **self.kwargs)
#         except:
#             traceback.print_exc()
#             exctype, value = sys.exc_info()[:2]
#             self.signals.error.emit((exctype, value, traceback.format_exc()))
#         else:
#             self.signals.result.emit(result)
#         finally:
#             self.signals.finished.emit()


class Worker:
    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()
        self.fn = fn
        self.name = name
        self.args = args
        self.kwargs = kwargs

    def run(self):
        return self.fn(*self.args, **self.kwargs)

        # try:
        # except:
        # traceback.print_exc()
        # exctype, value = sys.exc_info()[:2]
        # self.signals.error.emit((exctype, value, traceback.format_exc()))
        # else:
        # self.signals.result.emit(result)
        # finally:
        # self.signals.finished.emit()


def exit_process(out_queue):
    out_queue.put(Worker(exit_process))
    out_queue.close()
    out_queue.join_thread()


def load_nlp_model(self, out_queue, *args, **kwargs):
    out_queue.put(Worker(set_info_message, "Loading models..."))
    backend.nlp = NLP(*args, **kwargs)


class Backend:
    def __init__(self):
        self.nlp = None

    def run_backend_proc(in_queue, out_queue):
        while True:
            task = in_queue.get()
            if task is isinstance(Task):
                task.run(self)
