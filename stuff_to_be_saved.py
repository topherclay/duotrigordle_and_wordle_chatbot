import parsing_stuff



async def make_class(full_string):
    single_game = SingleGame(full_string)
    return single_game


class SingleGame:
    def __init__(self, full_string):
        self.user = None
        self.board_numer = None
        self.guesses_til_win = None
        self.is_a_won_game = None
        self.time_til_win = None
        self.parse_full_string(full_string)
        self.turn_events = None
        self.get_raw_scores(full_string)



    def parse_full_string(self, full_string):
        board_number = None
        guesses_til_win = None
        is_a_won_game = False
        time = None

        for line in full_string.split("\n"):
            if "Daily Duotrigordle #" in line:
                board_number = line.split("#")[1]

            if "Guesses:" in line:
                right_half = line.split("Guesses: ")[1]
                number = right_half.split("/37")[0]
                if number == "X":
                    continue
                else:
                    guesses_til_win = int(number)
                    is_a_won_game = True

            if "Time: " in line:
                time = line.split("Time: ")[1]


        self.board_numer = board_number
        self.guesses_til_win = guesses_til_win
        self.is_a_won_game = is_a_won_game
        self.time_til_win = time





        return "unknown user", full_string.split("\n")[0]


    def get_raw_scores(self, full_string):
        raw_scores = parsing_stuff.get_scores_only(full_string)
        self.turn_events = parsing_stuff.turn_scores_into_turns(raw_scores)





    def __repr__(self):
        representation = "```"

        ignorables = "turn_events"
        for key, value in self.__dict__.items():
            if key not in ignorables:
                new_line = f"{key: >16} : {value: <20}\n"
                representation += new_line
        representation += "```"
        return representation