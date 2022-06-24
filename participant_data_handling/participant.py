import json


class Participant:
    # custom classes must be converted to dictionary or list to be serializable

    def __init__(
        self,
        points=0,
        total_points=0,
        problems_solved=0,
        easy=0,
        medium=0,
        hard=0,
        won=0,
        first=0,
    ) -> None:
        self.points = points
        self.total_points = total_points
        self.problems_solved = problems_solved  # also days committed
        self.easy = easy
        self.medium = medium
        self.hard = hard
        self.won = won
        self.first = first

    def toJSON(self):
        return json.dumps(self, default=lambda x: x.__dict__, sort_keys=True, indent=2)

    def to_string(self):
        result = "\nTotal Points: " + str(self.total_points)
        result += "\nProblems Solved: " + str(self.problems_solved)
        result += "\nEasy Problems Solved: " + str(self.easy)
        result += "\nMedium Problems Solved: " + str(self.medium)
        result += "\nHard Problems Solved: " + str(self.hard)
        result += "\nCompetitions Won: " + str(self.won)
        result += "\nFirst Submissions: " + str(self.first)
        return result

    def get_points(self):
        return self.points

    def clear_points(self):
        self.points = 0

    def update_win(self):
        self.won += 1

    def update_stats(self, difficulty: str, points_recieved: int, was_first: bool):
        if difficulty == "hard":
            self.hard += 1
        elif difficulty == "med":
            self.medium += 1
        elif difficulty == "easy":
            self.easy += 1

        self.points += points_recieved
        self.problems_solved += 1
        self.total_points += points_recieved
        self.first += 1 if was_first else 0

    """
    def test_stats(self, setting: str, point_amount: int):
        if (setting == "first"):
            self.first += point_amount
        if setting == "hard":
            self.hard += point_amount
        elif setting == "med":
            self.medium += point_amount
        elif setting == "easy":
            self.easy += point_amount
        elif setting == "point":
            self.total_points += point_amount
        elif setting == "prob":
            self.problems_solved += point_amount
        elif setting == "win":
            self.won += point_amount
    """

    def get_badge_title(self):
        PROBLEM_THRESHOLD = 20
        POINT_THRESHOLD = 100
        DIFFICULTY_PERCENTAGE_THRESHOLD = 45
        PERCENT_TOTAL = lambda amount: (amount / self.problems_solved) * 100

        badge_title = "No badge... Do some problems to earn a badge!"

        if self.problems_solved < PROBLEM_THRESHOLD:
            return badge_title

        easy_percentage = PERCENT_TOTAL(self.easy)
        medium_percentage = PERCENT_TOTAL(self.medium)
        hard_percentage = PERCENT_TOTAL(self.hard)

        if self.won >= PROBLEM_THRESHOLD:
            badge_title = "🥇 *Standing on the shoulder of giants. And your hard work.*"
        elif self.first >= PROBLEM_THRESHOLD:
            badge_title = (
                "💨 *Well, would you look at the time. Lack there of obviously.*"
            )
        elif hard_percentage >= DIFFICULTY_PERCENTAGE_THRESHOLD:
            badge_title = "🏆 *The highest honor. Not using Stack Overflow.*"
        elif medium_percentage >= DIFFICULTY_PERCENTAGE_THRESHOLD:
            badge_title = "🍪 *Here's a cookie for all your efforts.*"
        elif easy_percentage >= DIFFICULTY_PERCENTAGE_THRESHOLD:
            badge_title = "🐒 *If rock and monke, then create fire.*"
        elif self.total_points >= POINT_THRESHOLD:
            badge_title = "🦾 *Point King*"
        elif self.problems_solved >= PROBLEM_THRESHOLD:
            badge_title = (
                "👨‍🌾 *Living the simple life. Eat. Solve a programming problem. Sleep.*"
            )

        return badge_title
