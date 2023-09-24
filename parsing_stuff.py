import datetime

# single_symbol = "🟥"
import sql_stuff
import stuff_to_be_saved


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

    if not end_of_scores:
        abridged = "\n".join(original_string.split("\n")[start_of_scores:-1])


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
    message = "```\n" + message + "```"
    return message


async def main_parse(orig_string):
    # adding this extra nonsense line at the end makes it easier to find the true last line.
    orig_string = orig_string + "\nx"

    raw_scores = get_scores_only(orig_string)

    turn_events = turn_scores_into_turns(raw_scores)

    grid = make_list_be_grid(turn_events)
    grid = emojify_a_string(grid)
    grid = add_turn_labels(grid)
    grid = add_ticks(grid)


    return grid


def convert_seconds_to_formatted_string(seconds):

    delta = datetime.timedelta(seconds=seconds)
    minutes, seconds = divmod(delta.seconds, 60)

    formatted_time = f"{minutes:02d}:{seconds:02d}.{str(delta.microseconds)[:2]}"
    return formatted_time



async def digest_a_wordle_result(message, user):
    try:
        wordle = stuff_to_be_saved.SingleWordle(message)
        wordle.user = user
        response = wordle
    except Exception as e:
        response = e
        raise e

    print("digested a wordle")

    return response



async def turn_wordle_stats_into_percentages(wordle_stats):
    total_games = sum(wordle_stats)
    percentages = []
    for index, score in enumerate(wordle_stats):
        percentage = round(score / total_games * 100, 2)
        percentage = str(percentage)
        left_half, right_half = percentage.split(".")
        if len(left_half) == 1:
            left_half = left_half.zfill(2)
        if len(right_half) == 1:
            right_half += "0"
        percentage = left_half + "." + right_half




        percentages.append(percentage)

    full_string = f"Out of {total_games} games \n" \
                  f"1/6 {percentages[0]:>5}% {wordle_stats[0]:<3}\n" \
                  f"2/6 {percentages[1]:>5}% {wordle_stats[1]:<3}\n" \
                  f"3/6 {percentages[2]:>5}% {wordle_stats[2]:<3}\n" \
                  f"4/6 {percentages[3]:>5}% {wordle_stats[3]:<3}\n" \
                  f"5/6 {percentages[4]:>5}% {wordle_stats[4]:<3}\n" \
                  f"6/6 {percentages[5]:>5}% {wordle_stats[5]:<3}\n" \
                  f"0/6 {percentages[6]:>5}% {wordle_stats[6]:<3}"
    return full_string



if __name__ == "__main__":
    # 05:05.37
    # 305.37
    formatted = convert_seconds_to_formatted_string(305.37)
    print(formatted)