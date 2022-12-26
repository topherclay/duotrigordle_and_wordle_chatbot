import parsing_stuff
import datetime


async def make_class(full_string):
    single_game = SingleGame(full_string)
    return single_game


class SingleGame:
    def __init__(self, full_string):
        self.user = None
        self.board_number = None
        self.guesses_til_win = None
        self.is_a_won_game = None
        self.time = None
        self.time_as_seconds = None
        self.parse_full_string(full_string)
        self.turn_events = None
        self.get_raw_scores(full_string)
        self.turn_time_to_seconds()


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


        self.board_number = board_number
        self.guesses_til_win = guesses_til_win
        self.is_a_won_game = is_a_won_game
        self.time = time





        return "unknown user", full_string.split("\n")[0]


    def get_raw_scores(self, full_string):
        raw_scores = parsing_stuff.get_scores_only(full_string)
        self.turn_events = parsing_stuff.turn_scores_into_turns(raw_scores)


    def turn_time_to_seconds(self):
        time = self.time

        if not time:
            return

        try:
            minutes, seconds_and_milli = time.split(":")
            minutes = int(minutes)

            seconds, milli = seconds_and_milli.split(".")
            seconds = int(seconds)
            milli = int(milli)*10

            as_delta = datetime.timedelta(minutes=minutes, seconds=seconds, milliseconds=milli)
            self.time_as_seconds = as_delta.total_seconds()
        except ValueError:
            self.time = None
            return







    def __repr__(self):
        representation = "```"

        ignorables = "turn_events"
        for key, value in self.__dict__.items():
            if key not in ignorables:
                new_line = f"{key: >16} : {str(value): <20}\n"
                representation += new_line
        representation += "```"
        return representation


class SingleWordle:
    def __init__(self, full_string):
        self.user = None
        self.board_number = None
        self.guesses_til_win = None
        self.is_a_won_game = None
        self.shape = None
        self.parse_the_string(full_string)

    def parse_the_string(self, message):
        header, content = message.split("\n\n")

        # eg: 'Wordle 555 X/6'
        _, day, score = header.split(" ")
        score = score.split("/")[0]


        if score == "X":
            score = "0"
            self.is_a_won_game = False
        else:
            self.is_a_won_game = True


        score = int(score)
        day = int(day)





        # letters are easier to parse than emojis.
        # replace *both* light mode and dark mode emojis with B for blank.
        content = content.replace("⬛", "B")
        content = content.replace("⬜", "B")
        # yellow and green emojis are the same regardless of dark mode settings.
        content = content.replace("🟩", "G")
        content = content.replace("🟨", "Y")
        content = content.replace("\n", "")


        content = [char for char in content if char in ["B", "G", "Y"]]

        self.shape = content
        self.board_number = day
        self.guesses_til_win = score


        if self.is_a_won_game:
            if self.shape[-5:] != "GGGGG":
                print("last five are:")
                print(self.shape[-5:])
                print("------------")
                raise ValueError("How did you win without five greens as your last line?")



