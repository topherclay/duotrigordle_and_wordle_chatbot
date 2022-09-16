

async def make_class(full_string):
    single_game = SingleGame(full_string)



    return single_game.user, single_game.date


class SingleGame:
    def __init__(self, full_string):
        self.user, self.date = self.parse_full_string(full_string)
        # self.score = self.parse_score()
        # self.time = self.parse_time()
        pass


    def parse_full_string(self, full_string):
        return "bob", full_string.split("\n")[0]