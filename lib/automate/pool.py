import spacy
import threading
import logging

from lib import Error

# Module logger
log = logging.getLogger(__name__)


class SharedModel:
    """
    SharedModel is a wrapper around a preloaded spacy model
    that locks the model when in use and unlocks after it has
    been used. Multiple references can exist to the SharedModel, but
    only one request to use it is allowed at a time.

    Usage:
    The recommended usage is with in a `with` statement. If an
    exception occurs the model will be automatically unlocked. E.g.
    ```
    s = SharedModel("en_core_web_sm", "en_core_web_sm")
    # `s` Locks when calling the code below
    with s:
        model = s.acquire_model()
    # `s` is unlocked here even during exception

    ```
    """

    def __init__(self, name, model):
        self._name = name
        self._model = model
        self._lock = threading.Lock()

    def __enter__(self):
        log.debug("Waiting to acquire lock for model %s", self._name)
        self._lock.acquire()
        log.debug("Acquired lock for model %s", self._name)

    def __exit__(self, exc_type, exc_value, traceback):
        self._lock.release()
        log.debug("Released lock for model %s", self._name)

    def name(self):
        return self._name

    def acquire_model(self):
        """
        acquire_model returns whatever spacy model that
        the SharedModel contains.
        :return Spacy model
        """
        return self._model


class ModelPool:
    """
    ModelPool contains a pool of SharedModels (spacy model wrappers) to be
    shared between different automation modules. When a SharedModel is acquired
    it will return a reference to that object. When calling methods to the
    SharedModel object it will be locked and unlocked automatically. If the
    SharedModel is locked when trying to use it, the call will be blocked until
    the object is unlocked.

    Uses thread-safe locks.
    """

    # Pool of objects with type SharedModel
    pool = dict()

    def __init__(self, model_names):
        """
        From the given model names, loads the models into memory, in the shared
        model pool as SharedModels.
        :param model_names: Names of the spacy models to be shared.
        :type list[string]
        """
        for name in model_names:
            model = spacy.load(name)
            self.pool[name] = SharedModel(name, model)
        log.debug("Initialized shared models in pool")

    def get_shared_model(self, model_name):
        """
        Acquires a SharedModel in the model pool. Once acquired there is
        no need to return the SharedModel, as the SharedModel object will
        be automatically locked/unlocked when in use/not in use. If the model
        is not found, a NoModelFoundError exception will be raised.

        :param model_name: The name of the spacy model to acquire.
        :type model_name: string
        :return: The shared model
        :rtype: SharedModel
        """
        if model_name in self.pool:
            return self.pool[model_name]

        raise NoModelFoundError("No model by the name %s found", model_name)


class NoModelFoundError(Error):
    pass
