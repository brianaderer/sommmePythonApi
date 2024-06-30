from utilities.parser import Parser
from utilities.firebase import Firebase
from utilities.save import Save
from utilities.queryDB import Query
from utilities.cacher import Cacher

class Singleton:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            print("Creating the Singleton object")
            cls._instance = super(Singleton, cls).__new__(cls)
            # Instantiate and attach child classes directly
            cls._instance.Parser = Parser()
            # cls._instance.Parser2 = Parser2()
            cls._instance.Firebase = Firebase()
            cls._instance.Save = Save()
            cls._instance.Query = Query()
            cls._instance.Cacher = Cacher()
        return cls._instance

    def hello(self):
        return 'world'
