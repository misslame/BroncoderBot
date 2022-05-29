
#stats to be tracked

class user:
    def __init__(self) -> None:
        self.totalPoints = 0
        self.problemsSolved = 0 #also days committed
        self.easy = 0
        self.medium = 0
        self.hard = 0
        self.won = 0
        self.first = 0

    def toString(self):
        pass

#make a dictionary using user name as a key
#write to file? to store if bot crashes
class stats:
    population: dict
    population = {}

    #ripped from points.py
    def __init__(self):
        if stats.__instance == None:
            stats.__instance = self
        else:
            raise Exception("[ERROR]: Cannot create another instance of class: Points. Singlton implemented.")

    @staticmethod
    def get_instance():
        if stats.__instance == None:
            stats.__instance = stats()    
        return stats.__instance

    def addUser(self, userID: int): #add user upon getting role / leave stats if role removed?
        userID = str(userID)
        if self.population.get(userID) == None:
            self.population[userID] = user()

    def getUser(self, userID: int):
        userID = str(userID)
        return self.population[userID]

    def updatePoints(self, userID: int, difficulty: int, first: bool):
        baseValue, multiplier, firstBonus= 1,2,0
        if first:
            firstBonus = 1
        userID = str(userID)
        user = self.population[userID]
        user.problemsSolved += 1
        
        user.totalPoints += baseValue + difficulty*multiplier + firstBonus

        if difficulty == "1":
            user.easy += 1
        elif difficulty == "2":
            user.medium += 1
        elif difficulty == "3":
            user.hard += 1
        
