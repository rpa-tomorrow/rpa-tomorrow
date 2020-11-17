import spacy
import asyncio
import logging

from lib import Error

# Module logger
log = logging.getLogger(__name__)


class ModelPool:
    """
    ModelPool contains a pool of spacy models to be shared between
    different automation modules. When a model is acquired a lock will
    be put on it such that no other modules can use it. When a lock is released
    the model can be used by the next module that is requesting it.

    Uses non-thread-safe locks!
    """
    # Stored as (name, model, lock)
    pool = []

    def __init__(self, model_names):
        """
        From the given model names, loads the models into memory, in the shared
        model pool.
        :param shared_models: Names of the spacy models to be shared.
        :type list[string]
        """
        for name in model_names:
            model = spacy.load(name)
            lock = asyncio.Lock()
            self.pool.append((name, model, lock))
        log.debug("Initialized shared models in pool")

    async def acquire_model(self, model_name):
        """
        Acquires a spacy model in the model pool. If the model is already in
        use, it will wait until the model is released, lock it and then return
        the model. If the model is not found, an exception will be raised.
        :param model_name: The name of the spacy model to acquire.
        :type model_name: string
        :return: The spacy model
        """
        for name, model, lock in self.pool:
            if name == model_name:
                log.debug("Waiting to acquire lock for model %s", name)
                await lock.acquire()
                log.debug("Acquired lock for model %s", name)
                return model

        raise NoModelFoundError("No model by the name %s found", model_name)

    def release_model(self, model_name):
        """
        Relases the lock for a model such that others can use it.
        :param model_name: The name of the spacy model to release.
        :type model_name: string
        """
        for name, _, lock in self.pool:
            if name == model_name:
                lock.release()
                log.debug("Released lock for model %s", name)


class NoModelFoundError(Error):
    pass
