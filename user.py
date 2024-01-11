from interactions import Member
from datetime import datetime
from itertools import groupby

class User():
    def __init__(self, uid: int, handle: str, voter_uid: int, curr_duration: int, user_count: int, instance: Member):
        self.uid = uid
        self.handle = handle
        self.voters = {voter_uid: curr_duration}
        self.user_count = user_count
        self.instance = instance
        self.vote_count = 1
        self.end_date = None

    def update_stats(self, new_handle: str, new_voter_uid: int, new_duration: int) -> None:
        self.handle = new_handle
        self.voters[new_voter_uid] = new_duration
        self.vote_count += 1

    def decrease_vote(self) -> None:
        self.vote_count -= 1

    def voter_is_present(self, voter_uid: int) -> bool:
        return voter_uid in self.voters

    def is_bannable(self) -> bool:
        return self.vote_count > self.user_count // 2
    
    def get_duration(self) -> int:
        return round(sum(self.voters.values())/len(self.voters))
    
    def set_duration(self, new_date: datetime) -> None:
        self.end_date = new_date

def get_user(uid: int, user_list: []) -> User | None:
    for user in user_list:
        if user.uid == uid:
            return user    
    return None

def print_stats(user_list: []) -> str:
    ret_str = "**Ban candidates:**\n"
    for user in user_list:
        ret_str += f'\t{user.handle}: {user.vote_count}/{user.user_count}, avg duration: {user.get_duration()}h\n'
    return ret_str

def print_gasparko_tierlist(user_list: []) -> str:
    # a solid block of cancer, I know... it was late
    # also for some reason discord treats **a** **b** as:
    # **a**
    # 
    # **b**
    # hence a lot of this bloat is for formatting the resulting message

    user_list.sort(key=lambda x: x.get_duration(), reverse=True)
    # aggregate User objects with same values into a sublist
    user_list = [list(group) for _, group in groupby(user_list, key=lambda x: x.get_duration())]
    end = ""
    ret_str = f'# !!! {datetime.now().date().strftime("%d.%m.%Y")} Gašparko Tier List !!!\n'

    if not user_list:
        return ret_str + "No entries yet!"

    for i, user_sublist in zip(range(len(user_list)), user_list):
        if i == 0:
            ret_str += "# :first_place: "
        elif i == 1:
            ret_str += "## :second_place: "
        elif i == 2:
            ret_str += "### :third_place: "
        elif i == 3:
            ret_str += f'**{i + 1}. '
        else:
            ret_str += f'{i + 1}. '
        if user_sublist == user_list[-1] and len(user_list) > 3:
            end = "**"

        # sublist found, sort User objects by name
        if isinstance(user_sublist, list):
            user_sublist.sort(key=lambda x: x.handle)

        for user in user_sublist:
            ret_str += f'{user.handle} with {user.get_duration()}cm, '
        ret_str = ret_str[:-2]
        ret_str += f'{end}\n'
    return ret_str