import discord
import json
from heapq import nlargest


class Points:
    pointMap: dict

    __instance = None
    pointMap = {}

    def __init__(self):
        if Points.__instance == None:
            Points.__instance = self
        else:
            raise Exception("[ERROR]: Cannot create another instance of class: Points. Singlton implemented.")

    @staticmethod
    def get_instance():
        if Points.__instance == None:
            Points.__instance = Points()    
        return Points.__instance


    def init_points(self):

        # create file if doesnt exist
        with open('points_table/pointsData.json', 'a+') as f:
            pass

        with open('points_table/pointsData.json', 'r') as f:
            fileContent: str = f.read()
            
        if fileContent == "":
            self.pointMap = {}
            
        else:
            self.pointMap = json.loads(fileContent)

    # updates file (idk im just calling it everytime there's a change just in case the bot crashes)
    def update(self):
        with open('points_table/pointsData.json', 'w') as f:
            f.write(json.dumps(self.pointMap, indent=2))

    # adds points
    def addPoints(self, userID: int , points=1):
        userID = str(userID)
        if self.pointMap.get(userID) == None:
            self.pointMap[userID] = 0
        self.pointMap[userID] += points
        self.update()

    # clears scores
    def clear(self):
        self.pointMap = {}
        self.update()

    # get top scores
    def getTop(self, amount=20) -> list[int]:
        return nlargest(amount, self.pointMap, key=self.pointMap.get)

    # get points of an individual user
    def getPoints(self, userID: int ):
        userID = str(userID)
        if self.pointMap.get(userID) == None:
            self.pointMap[userID] = 0
        return self.pointMap[userID]
