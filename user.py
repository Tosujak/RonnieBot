from interactions import Member

class User():
    def __init__(self, uid: int, handle: str, voter_uid: int, curr_duration: int, curr_online: int, instance: Member):
        self.uid = uid
        self.handle = handle
        self.voters = {voter_uid: curr_duration}
        self.curr_online = curr_online
        self.instance = instance
        self.vote_count = 1
        self.end_date = None

    def update_stats(self, new_handle: str, new_voter_uid: int, new_duration: int, new_online_count: int) -> None:
        self.handle = new_handle
        self.voters[new_voter_uid] = new_duration
        self.curr_online = new_online_count
        self.vote_count += 1

    def decrease_vote(self) -> None:
        self.vote_count -= 1

    def voter_is_present(self, voter_uid: int) -> bool:
        return voter_uid in self.voters

    def is_bannable(self) -> bool:
        if self.curr_online < 3:
            return False
        return self.vote_count > self.curr_online // 2
    
    def get_duration(self) -> int:
        return round(sum(self.voters.values())/len(self.voters))

def get_user(uid: int, user_list: []) -> User | None:
    for user in user_list:
        if user.uid == uid:
            return user    
    return None

def print_stats(user_list: []) -> str:
    ret_str = "Ban candidates:\n"
    for user in user_list:
        ret_str += f'\t{user.handle}: {user.vote_count}/{user.curr_online}, avg duration: {user.get_duration()}h\n'
    return ret_str
