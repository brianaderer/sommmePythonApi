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
from utilities.cleanse_wine import CleanseWine
from utilities.fcm import FCM
# from utilities.flight import Flight
from utilities.group import Group
from utilities.shares import Shares
from utilities.messages import Messages
from utilities.p3 import P3
from utilities.props import Props
from lookups.Dependencies import Dependencies


class Singleton:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            print("Creating the Singleton object")
            cls._instance = super(Singleton, cls).__new__(cls)
            cls._instance.Parser = Parser()
            cls._instance.Firebase = Firebase()
            cls._instance.Save = Save()
            cls._instance.Query = Query()
            cls._instance.Cacher = Cacher()
            cls._instance.Similarity = Similarity()
            cls._instance.Recommender = Recommender()
            cls._instance.Crons = Crons()
            cls._instance.User = User()
            cls._instance.HandleUserWine = HandleUserWine()
            cls._instance.CleanseWine = CleanseWine()
            # cls._instance.Flight = Flight()
            cls._instance.Group = Group()
            cls._instance.Shares = Shares()
            cls._instance.Messages = Messages()
            cls._instance.P3 = P3()
            cls._instance.Dependencies = Dependencies()
            cls._instance.Props = Props()
            cls._instance.FCM = FCM()
        return cls._instance
