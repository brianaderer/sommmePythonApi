from utilities.parser import Parser
from utilities.firebase import Firebase
from utilities.save import Save
from utilities.queryDB import Query
from utilities.cacher import Cacher
from utilities.similarity import Similarity
from utilities.recommender import Recommender
from utilities.crons import Crons
from utilities.user import User
from utilities.handle_user_wine import HandleUserWine


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
            cls._instance.Similarity = Similarity()
            cls._instance.Recommender = Recommender()
            cls._instance.Crons = Crons()
            cls._instance.User = User()
            cls._instance.HandleUserWine = HandleUserWine()
        return cls._instance
