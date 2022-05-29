import json

class PersistentStore:
    ACCEPTED_TYPES = [str, int, bool, float, None]

    def __init__(self, filename='runtime-store.json'):
        if not hasattr(PersistentStore, '__instance'):
            self.__f = open(filename, 'r+')
            self.__f.seek(0, 0)

            buf = self.__f.read()
            if len(buf) > 0:
                self.__config = json.loads(buf)
            else:
                self.__config = {}
                self.update()
        else:
            raise RuntimeException('PersistentStore is singleton')

    @staticmethod
    def get_instance():
        if not hasattr(PersistentStore, '__instance'):
            PersistentStore.__instance = PersistentStore()

        return PersistentStore.__instance

    def __getitem__(self, key):
        return self.__config[key]

    def __setitem__(self, key, value):
        if type(value) not in PersistentStore.ACCEPTED_TYPES:
            raise Exception('Value not a valid type')

        self.__config[key] = value
        self.update()

    def __contains__(self, key):
        return key in self.__config

    def update(self):
        self.__f.seek(0)
        json.dump(self.__config, self.__f)
        self.__f.flush()
