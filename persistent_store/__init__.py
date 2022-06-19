from copy import copy, deepcopy
import json
from os.path import isfile


class PersistentStore:
    __instance = None

    def __init__(self, filename="runtime-store.json"):
        if PersistentStore.__instance == None:
            PersistentStore.__instance = self
            if not isfile(filename):
                self.__f = open(filename, "w+")
            else:
                self.__f = open(filename, "r+")

            self.__f.seek(0, 0)
            buf = self.__f.read()
            if len(buf) > 0:
                self.__store = json.loads(buf)
            else:
                self.__store = {}
                self.sync()
        else:
            raise RuntimeError("PersistentStore is singleton")

    @staticmethod
    def get_instance():
        if PersistentStore.__instance == None:
            PersistentStore()

        return PersistentStore.__instance

    def __getitem__(self, key):
        if type(key) is int:
            key = str(key)

        # Ensure the user cannot externally modify internal dict state
        if key in self:
            return deepcopy(self.__store[key])

        raise KeyError()

    def __setitem__(self, key, value):
        if type(key) is int:
            key = str(key)

        # Ensure we don't have a reference to the original value
        v = deepcopy(value)

        if type(v) is dict:
            self.__clean_keys(v)

        self.__store[key] = v
        self.sync()

    def __contains__(self, key):
        if type(key) is int:
            key = str(key)

        return key in self.__store

    def __delitem__(self, key):
        if type(key) is int:
            key = str(key)

        del self.__store[key]
        self.sync()

    def update(self, data):
        self.__clean_keys(data)
        self.__store.update(data)
        self.sync()

    def sync(self):
        self.__f.seek(0)
        json.dump(self.__store, self.__f, indent=1)
        self.__f.truncate()
        self.__f.flush()

    def __clean_keys(self, dic):
        for k, v in list(dic.items()):
            if type(k) is int:
                if str(k) in dic:
                    raise Exception(f"Duplicate keys in dict: {str(k)}")

                dic[str(k)] = v
                del dic[k]

            if type(v) is dict:
                self.__clean_keys(v)
