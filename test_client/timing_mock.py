import time

# not needed on linux machine
LINUX_EPOCH_OFFSET = 0

# synchronize local time with NTP server
# this function should be executed once in a couple of minutes
#   returns:    0 if completed, 1 otherwise
_is_time_synchronized = False
def ntp_synchronize():
    global _is_time_synchronized
    _is_time_synchronized = True
    return 0

# returns True when at least one NTP synchronization has been completed
def is_synchronized():
    return _is_time_synchronized


# checks if current time is within specified range
#   day_start:  string, start time in format "HH:MM:SS"
#   day_end:    string, end time in format "HH:MM:SS"
#   returns:    True/False
def check_day_mode(day_start, day_end):
    try:
        start = [int(i) for i in day_start.split(':')]
        start = 3600*start[0] + 60*start[1] + start[2]

        end = [int(i) for i in day_end.split(':')]
        end = 3600*end[0] + 60*end[1] + end[2]

        current = get_time()
        current = 3600*current[0] + 60*current[1] + current[2]

        if start <= end:
            return (current >= start) and (current < end)
        else:
            return (current >= start) or (current < end)
    except Exception as e:
        print('[ERR] Day mode checking failed:',e)
        return False


# get current time
#   returns:    a tuple of (hour, minute, second)
def get_time():
    return time.localtime()[3:6]


# get current date
#   returns:    a tuple of (year, month, day)
def get_date():
    return time.localtime()[:3]


# get current date and time
#   returns:    a tuple of (year, month, day, hour, minute, second)
def get_datetime():
    return time.localtime()[:6]


# get current timestamp since linux epoch
def get_timestamp():
    return int(time.time() + LINUX_EPOCH_OFFSET)



# -------------------------------------------------------------------
# aux functions
# -------------------------------------------------------------------

# check if given date should be in summertime or regular time
#   t:          current time in seconds
#   returns:    True if summertime, False if regular time
def check_summertime(t):
    # not entirely correct implementation, but it should be enough for everyday's use - one week accuracy
    month = time.localtime(t)[1]
    if month >= 4 and month <= 10:
        return True
    else:
        return False