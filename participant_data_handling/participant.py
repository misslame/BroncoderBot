
class Participant:
    def __init__(self) -> None:
        self.total_points = 0
        self.problems_solved = 0 #also days committed
        self.easy = 0
        self.medium = 0
        self.hard = 0
        self.won = 0
        self.first = 0

    def to_string(self):
        result = "\ntotal_points: " + str(self.total_points)
        result += "\nproblems solved: " + str(self.problems_solved)
        result += "\nEasy problems solved: " + str(self.easy)
        result += "\nMedium problems solved: "  + str(self.medium)
        result += "\nhard problems solved: " + str(self.hard)
        result += "\nCompetitions won: " + str(self.won)
        result += "\nfirst submissions: " + str(self.first)
        return result

    def update_win(self):
        self.won += 1

    def update_stats(self, difficulty: str, points_recieved: int, was_first: bool):
        if(difficulty == 'hard'):
            self.hard += 1
        elif(difficulty == 'med'):
            self.medium += 1
        elif(difficulty == 'easy'):
            self.easy += 1

        self.problems_solved += 1
        self.total_points += points_recieved
        self.first += 1 if was_first else 0