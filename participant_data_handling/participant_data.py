import json
from participant_data_handling.participant import Participant
from heapq import nlargest

'''************************************************************
    CLASS: ParticipantData:
    Handle Particpant information during & after competition. 
************************************************************'''
class ParticipantData:

    # Static Member: participants - holds participant stats
    particpants_stats: dict
    particpants_stats = {} # Participants

    # Static Member: point_map - hold points of the competition
    point_map: dict
    point_map = {}

    # Singleton requirement: Static Instance representing the class
    __instance = None

    # Implemented singleton design pattern to prevent multiple instantiations of UserData class.
    def __init__(self):
        if ParticipantData.__instance == None:
            ParticipantData.__instance = self
        else:
            raise Exception("[ERROR]: Cannot create another instance of class: Points. Singlton implemented.")

    @staticmethod
    def get_instance():
        if ParticipantData.__instance == None:
            ParticipantData.__instance = ParticipantData()    
        return ParticipantData.__instance

    def init_points(self):
        # create file if doesnt exist
        with open('participant_data_handling/pointsData.json', 'a+') as f:
            pass

        with open('participant_data_handling/pointsData.json', 'r') as f:
            fileContent: str = f.read()
            
        if fileContent == "":
            self.pointMap = {}
            
        else:
            self.pointMap = json.loads(fileContent)

    """NOT FOR PUBLIC USE: internal method only. """
    def __add_points(self, userID: int , points=1):
        userID = str(userID)
        if self.pointMap.get(userID) == None:
            self.pointMap[userID] = 0
        self.pointMap[userID] += points
        self.update()

        #updates personal stats for participant
        #self.updatePoints(userID, points, True)

    def add_participant(self, userID: int): #add participant upon getting role / leave stats if role removed?
        print("hello")
        userID = str(userID)
        if self.particpants_stats.get(userID) == None:
            self.particpants_stats[userID] = Participant()

    def get_participant_printed_stats(self, userID: int):
        userID = str(userID)
        return self.particpants_stats[userID].to_string()

    # get top scores
    def get_top(self, amount=20) -> list[int]:
        return nlargest(amount, self.pointMap, key=self.pointMap.get)


    # get points of an individual user
    def get_points(self, userID: int ):
        userID = str(userID)
        if self.pointMap.get(userID) == None:
            self.pointMap[userID] = 0
        return self.pointMap[userID]
    
    def update_win_stats(self, userID: int):
        self.particpants_stats[userID].update_win()

    def update_stats(self, userID: int, difficulty: str, points_recieved: int, was_first: bool):
        self.__add_points(userID, points_recieved)
        self.particpants_stats[userID].update_stats(difficulty, points_recieved, was_first)

    #TODO: Add functionality for participant data
    # updates file (idk im just calling it everytime there's a change just in case the bot crashes)
    def update_file(self):
        with open('points_table/pointsData.json', 'w') as f:
            f.write(json.dumps(self.pointMap, indent=2))

    # clears current scores
    def clear(self):
        self.pointMap = {}
        self.update_file()

    '''  Don't think we need this handled here. Moved.
    def update_points(self, userID: int, difficulty: int, first: bool):
        baseValue, multiplier, firstBonus= 0,1,0
        userID = str(userID)
        user = self.particpants[userID]

        if first:
            user.first += 1
            firstBonus = 1
        user.problemsSolved += 1
        user.totalPoints += baseValue + difficulty*multiplier + firstBonus
        if difficulty == "1":
            user.easy += 1
        elif difficulty == "2":
            user.medium += 1
        elif difficulty == "3":
            user.hard += 1
    '''