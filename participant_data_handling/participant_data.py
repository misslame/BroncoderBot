from asyncio.windows_events import NULL
import json
import sqlite3
from participant_data_handling.participant import Participant
from heapq import nlargest

'''to do: try to fix the json file. we are having trouble writing
        : if json works, we can try to implement a database'''
'''************************************************************
    CLASS: ParticipantData:
    Handle Particpant information during & after competition. 
************************************************************'''
class ParticipantData:
    conn = sqlite3.connect(':memory:')
    c = conn.cursor()

    # Static Member: participants - holds participant stats
    #participants_stats: dict
    #participants_stats = {} # Participants

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
        print("checking table...")
        #create table if not exists TableName (col1 typ1, ..., colN typN)
        self.c.execute("""CREATE table if not exists PARTICIPANTS(
            ID INTEGER PRIMARY KEY,
            SCORE INTEGER DEFAULT 0,
            TOTALPOINTS INTEGER DEFAULT 0,
            SOLVED INTEGER DEFAULT 0,
            EASY INTEGER DEFAULT 0,
            MEDIUM INTEGER DEFAULT 0,
            HARD INTEGER DEFAULT 0,
            WIN INTEGER DEFAULT 0,
            WASFIRST INTEGER DEFAULT 0)""")
        
        '''
        # create file if doesnt exist
        with open('participant_data_handling/participantStats.json', 'a+') as f:
            pass

        with open('participant_data_handling/participantStats.json', 'r') as f:
            fileContent: str = f.read()
            

        self.participants_stats= {}
            
        if fileContent:
            raw_stats: dict = json.loads(fileContent).get("participant_stats", {})

            for k, v in raw_stats.items():
                self.participants_stats[k] = Participant(**v)
        '''

    '''
    """NOT FOR PUBLIC USE: internal method only. """
    def __add_points(self, userID: int , points=1):
        userID = str(userID)
        if self.pointMap.get(userID) == None:
            self.pointMap[userID] = 0
        self.pointMap[userID] += points
        self.update()

        #updates personal stats for participant
        #self.updatePoints(userID, points, True)
    '''

    def add_participant(self, userID: int): #add participant upon getting role / leave stats if role removed?
        #userID = str(userID)
        with self.conn:
            self.c.execute("INSERT OR IGNORE INTO PARTICIPANTS(ID) VALUES(:ID)",{'ID':userID})
        self.c.execute("SELECT * FROM PARTICIPANTS")
        print(self.c.fetchone())
        
        '''
        if self.participants_stats.get(userID) == None:
            self.participants_stats[userID] = Participant()
        '''

    def get_participant_printed_stats(self, userID: int):
        userID = str(userID)
        self.c.execute("SELECT * FROM PARTICIPANTS WHERE (:ID)", {'ID':userID })
        userData = self.c.fetchone()
        return self.toString(userData)
        
        #return self.participants_stats[userID].to_string()


    def toString(self, userData):
        #userData[0] is the user's id
        results = "\nPoints: " + str(userData[1])
        results += "\nTotalPoints: " + str(userData[2])
        results += "\nProblems solved: " + str(userData[3])
        results += "\nEasy's solved: " + str(userData[4])
        results += "\nMedium's solved " + str(userData[5])
        results += "\nHard's solved: " + str(userData[6])
        results += "\nNumber of wins: " + str(userData[7])
        results += "\nWas First: " + str(userData[8])
        return results

    # get top scores
    def get_top(self, amount=20) -> list[int]:
        with self.conn:
            self.c.execute("SELECT ID FROM PARTICIPANTS ORDER BY SCORE")

        #print(str(self.c.fetchall())
        print("\n\n")
        result = []
        for row in self.c:
            result.append( str(row[0]) )
        return result
        #return nlargest(amount, self.participants_stats, key=lambda x: self.participants_stats[x].points)

    # get points of an individual user
    def get_points(self, userID: int ):
        #userID = str(userID)
        self.add_participant(userID)
        self.c.execute("SELECT SCORE FROM PARTICIPANTS WHERE (:ID)",{'ID': userID})
        return self.c.fetchone()[0]
        
        '''
        if self.participants_stats.get(userID) == None:
            self.add_participant(userID)
        return self.participants_stats[userID].get_points()
        '''

    def update_win_stats(self, userID: int):
        with self.conn:
            self.c.execute("""UPDATE PARTICIPANTS SET WIN = WIN + 1 WHERE ID = :ID""", {'ID': userID})
        #self.participants_stats[userID].update_win()

    def update_stats(self, userID: int, difficulty: str, points_recieved: int, was_first: bool):
        self.add_participant(userID)

        bonus = 0
        if was_first:
            bonus = 1
        #'Difficulty': difficulty,
        with self.conn:
            self.c.execute("""UPDATE PARTICIPANTS 
            SET SCORE = SCORE + :Points, 
            TOTALPOINTS = TOTALPOINTS + :Points, 
            HARD = HARD + 1, 
            WASFIRST = WASFIRST + :Bonus               
            WHERE ID = :ID""", {'Points': points_recieved, 'Bonus': bonus,'ID': userID})
        self.c.execute("SELECT * FROM PARTICIPANTS")
        print(self.c.fetchall())
        '''
        userID = str(userID)
        if self.participants_stats.get(userID) == None:
            self.add_participant(userID)
        self.participants_stats[userID].update_stats(difficulty, points_recieved, was_first)
        self.update_files()
        '''
    '''
    #TODO: Add functionality for participant data
    #https://stackoverflow.com/questions/21453117/json-dumps-not-working
    # updates file (idk im just calling it everytime there's a change just in case the bot crashes)
    def update_files(self):
        with open('participant_data_handling/participantStats.json', 'w') as f:
            #f.write(json.dumps(self.participants_stats, indent=2))
            json.dump({'participant_stats':self.participants_stats}, f, indent = 2, default=lambda o: o.__dict__)
    '''
    # clears current scores
    def clear(self):
        with self.conn:
            self.c.execute("UPDATE PARTICIPANTS SET SCORE = 0")
        
        #self.participants_stats = {k.clear_points() for k, v in self.participants_stats.items()}
        #self.update_files()

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