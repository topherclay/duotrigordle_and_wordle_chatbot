import itertools



niels_score = """Daily Duotrigordle #187
Guesses: 36/37
3️⃣0️⃣ 0️⃣9️⃣ 2️⃣1️⃣ 3️⃣1️⃣
2️⃣9️⃣ 2️⃣2️⃣ 2️⃣3️⃣ 3️⃣2️⃣
0️⃣7️⃣ 2️⃣4️⃣ 2️⃣5️⃣ 2️⃣6️⃣
0️⃣5️⃣ 0️⃣3️⃣ 2️⃣8️⃣ 1️⃣0️⃣
1️⃣1️⃣ 2️⃣7️⃣ 1️⃣9️⃣ 1️⃣8️⃣
3️⃣6️⃣ 3️⃣3️⃣ 0️⃣4️⃣ 1️⃣7️⃣
1️⃣6️⃣ 1️⃣2️⃣ 1️⃣3️⃣ 2️⃣0️⃣
1️⃣4️⃣ 3️⃣5️⃣ 3️⃣4️⃣ 1️⃣5️⃣
https://duotrigordle.com/"""


davids_Score = """Daily Duotrigordle #187
Guesses: X/37
1️⃣4️⃣ 0️⃣8️⃣ 🟥🟥 2️⃣4️⃣
3️⃣7️⃣ 2️⃣3️⃣ 3️⃣5️⃣ 3️⃣6️⃣
2️⃣7️⃣ 1️⃣2️⃣ 2️⃣5️⃣ 2️⃣8️⃣
1️⃣1️⃣ 0️⃣5️⃣ 1️⃣5️⃣ 2️⃣9️⃣
2️⃣2️⃣ 3️⃣4️⃣ 3️⃣0️⃣ 0️⃣6️⃣
1️⃣0️⃣ 3️⃣3️⃣ 2️⃣1️⃣ 1️⃣3️⃣
3️⃣1️⃣ 2️⃣0️⃣ 0️⃣7️⃣ 3️⃣2️⃣
1️⃣6️⃣ 1️⃣7️⃣ 1️⃣8️⃣ 1️⃣9️⃣
https://duotrigordle.com/"""









# single_symbol = "🟥"




def get_scores_only(original_string):
    abridged = None
    start_of_scores = None
    end_of_scores = None
    for index, line in enumerate(original_string.split("\n")):
        for char in line:
            if char.encode("utf8") in [b"\xef\xb8\x8f", b'\xef\xb8\x8f', b'\xf0\x9f\x9f\xa5'] and (not start_of_scores):
                start_of_scores = index
                break

        if "https://duotrigordle.com/" in line:
            end_of_scores = index


        if start_of_scores and " " not in line:
            end_of_scores = index


        if start_of_scores and end_of_scores:
            abridged = "\n".join(original_string.split("\n")[start_of_scores:end_of_scores])
            break

    return convert_scores_to_ints(abridged)



def convert_scores_to_ints(emoji_string):
    emoji_string = emoji_string.replace("\n", " ")
    single_word_scores = emoji_string.split(" ")


    integer_scores = []
    for single_word_score in single_word_scores:
        # turn red box emoji to zeros
        remove = single_word_score.encode("utf8").replace(b"\xf0\x9f\x9f\xa5", b"0").decode()
        # remove color emoji
        remove = remove.encode("utf8").replace(b'\xef\xb8\x8f', b"").decode()
        # remove box emoji
        removed_non_scores = remove.encode("utf8").replace(b'\xe2\x83\xa3', b"").decode()
        integer_scores.append(int(removed_non_scores))
    return integer_scores


def display_non_scoring_turns(scores):
    full_turns = ""
    scoring_turns = 0
    for turn in range(1, 38):
        if scoring_turns >= 32:
            full_turns += "🏆"
            continue


        if turn in scores:
            scoring_turns += 1
            full_turns += "😊"
        else:
            full_turns += "😡"
    return full_turns


def make_list_be_grid(scores):
    grid = ""
    for index, score in enumerate(scores[0:]):
        grid += f"{score} "
        if not (index + 1) % 4:
            grid += "\n"
    return grid




def turn_scores_into_turns(scores: list):
    """This adds solved words, the XX, and the GG in to the list of turns."""
    turns = range(1, 38)

    event_per_turn = []
    amount_of_scoring_turns = 0
    for turn in turns:
        if turn in scores:
            event_per_turn.append(f"{scores.index(turn) + 1:02d}")
            amount_of_scoring_turns += 1
            # print(f"\t{scores.index(turn) + 1:02d}")
        else:
            if amount_of_scoring_turns >= 32:
                event_per_turn.append("GG")
            else:
                event_per_turn.append("XX")
                # print("\tXX")
        # print(f"{amount_of_scoring_turns} are scored on turn {turn}")
    return event_per_turn


def emojify_a_string(the_string):


    errors = ["🟩", "🟩", "🟩", "🟩", "🟨", "🟥", "🟥", "🟥", "🟥", "🟥", "🟥", "🟥", "🟥", "🟥", "🟥", "🟥", "🟥"]
    error_count = 0
    finished_string = ""
    for char in the_string:
        if char == "X":

            finished_string += errors[error_count//2]
            error_count += 1
            continue
        if char == "G":
            finished_string += "🏆"
            break

        if char in [" ", "\n"]:
            finished_string += char
            continue

        finished_string += char
        finished_string += b'\xef\xb8\x8f'.decode()
        # finished_string += b'\x9f\x9f\xa9'.decode()

        finished_string += b'\xe2\x83\xa3'.decode()


    return finished_string


def add_turn_labels(non_labelled: str):

    turn = 1
    with_turns = f"Turn {turn:02d} "
    for char in non_labelled:
        if char == "\n":
            turn = turn + 4
            with_turns += f"\nTurn {turn:02d} "
        else:
            with_turns += char
    return with_turns


def add_ticks(message):
    message = "```" + message + "```"
    return message





async def main_parse(orig_string):


    raw_scores = get_scores_only(orig_string)

    turn_events = turn_scores_into_turns(raw_scores)

    grid = make_list_be_grid(turn_events)
    grid = emojify_a_string(grid)
    grid = add_turn_labels(grid)
    grid = add_ticks(grid)


    return grid















if __name__ == "__main__":
    alia = """3️⃣1️⃣ 3️⃣2️⃣ 1️⃣4️⃣ 1️⃣5️⃣
    1️⃣6️⃣ 0️⃣4️⃣ 1️⃣1️⃣ 1️⃣7️⃣
    0️⃣9️⃣ 3️⃣3️⃣ 1️⃣8️⃣ 0️⃣8️⃣
    3️⃣4️⃣ 0️⃣7️⃣ 1️⃣3️⃣ 1️⃣9️⃣
    3️⃣5️⃣ 3️⃣7️⃣ 2️⃣0️⃣ 1️⃣2️⃣
    2️⃣1️⃣ 2️⃣2️⃣ 2️⃣3️⃣ 2️⃣5️⃣
    2️⃣7️⃣ 2️⃣8️⃣ 2️⃣6️⃣ 0️⃣6️⃣
    0️⃣5️⃣ 3️⃣6️⃣ 2️⃣9️⃣ 3️⃣0️⃣"""

    one_fail = """1️⃣6️⃣ 3️⃣5️⃣ 2️⃣4️⃣ 1️⃣5️⃣
    1️⃣3️⃣ 0️⃣5️⃣ 1️⃣4️⃣ 1️⃣2️⃣
    1️⃣7️⃣ 2️⃣3️⃣ 1️⃣1️⃣ 0️⃣6️⃣
    2️⃣5️⃣ 2️⃣6️⃣ 1️⃣8️⃣ 2️⃣7️⃣
    3️⃣6️⃣ 🟥🟥 1️⃣9️⃣ 3️⃣7️⃣
    2️⃣0️⃣ 1️⃣0️⃣ 2️⃣8️⃣ 2️⃣9️⃣
    3️⃣0️⃣ 3️⃣1️⃣ 2️⃣1️⃣ 0️⃣8️⃣
    0️⃣9️⃣ 3️⃣3️⃣ 2️⃣2️⃣ 3️⃣2️⃣"""




    main_parse(alia)
    main_parse(one_fail)
