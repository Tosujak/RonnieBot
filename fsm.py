nword_room_counters = {}  # format: roomID: counter

def nword_fsm(nword_counter, msg):
    # epic FSM moment
    if (nword_counter == 0 and msg.lower() == "n"):
        return False, 1
    elif (nword_counter == 1 and msg.lower() == "i"):
        return False, 2
    elif (nword_counter == 1 and msg.lower() == "e"):
        return False, 6
    elif (nword_counter == 2 and msg.lower() == "g"):
        return False, 3
    elif (nword_counter == 3 and msg.lower() == "g"):
        return False, 4
    elif (nword_counter == 4 and msg.lower() == "a"):
        return True, 0
    elif (nword_counter == 4 and msg.lower() == "e"):
        return False, 5
    elif (nword_counter == 5 and msg.lower() == "r"):
        return True, 0
    elif (nword_counter == 6 and msg.lower() == "g"):
        return False, 4
    else:
        return False, 0
    
    
def should_send_warning(channel_id, msg):
    global nword_room_counters
    # if it doesnt exist, create a new channel entry in the counter dict
    if not channel_id in nword_room_counters.keys():
        nword_room_counters[channel_id] = 0
    nword_counter = nword_room_counters[channel_id]
    
    is_counter_filled, new_state = nword_fsm(nword_counter, msg)
    if is_counter_filled:
        # reset counter for given room and send warning msg
        nword_room_counters[channel_id] = 0  
        return True
    else:
        nword_room_counters[channel_id] = new_state
        return False
    