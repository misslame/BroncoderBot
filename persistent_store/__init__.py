from copy import deepcopy
import json
from os.path import isfile

class PersistentStore:
    def __init__(self, filename='runtime-store.json'):
        if not hasattr(PersistentStore, '__instance'):
            if not isfile(filename):
                self.__f = open(filename, 'w+')
            else:
                self.__f = open(filename, 'r+')

            self.__f.seek(0, 0)
            buf = self.__f.read()
            if len(buf) > 0:
                self.__store = json.loads(buf)
            else:
                self.__store = {}
                self.sync()
        else:
            raise RuntimeException('PersistentStore is singleton')

    @staticmethod
    def get_instance():
        if not hasattr(PersistentStore, '__instance'):
            PersistentStore.__instance = PersistentStore()

        return PersistentStore.__instance

    def __getitem__(self, key):
        # Ensure the user cannot externally modify internal dict state
        if key in self:
            return deepcopy(self.__store[key])

        raise KeyError()

    def __setitem__(self, key, value):
        # Ensure we don't have a reference to the original value
        self.__store[key] = deepcopy(value)
        self.sync()

    def __contains__(self, key):
        return key in self.__store

    def update(self, *args, **kwargs):
        self.__store.update(*args, **kwargs)
        self.sync()

    def sync(self):
        self.__f.seek(0)
        json.dump(self.__store, self.__f)
        self.__f.flush()
