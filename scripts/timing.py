# Handling time (synchronization with NTP, checking day/night mode etc.)

import gc, utime, ntptime, machine
gc.collect()


# -------------------------------------------------------------------
# configuration
# -------------------------------------------------------------------



# -------------------------------------------------------------------
# main features
# -------------------------------------------------------------------

#set local time with predefined values
#this function should be executed on startup if NTP synchronization fails
def set_time(year, month, day, hour, minute, second):
    machine.RTC().datetime((year, month, day, 0, hour, minute, second, 0))


# synchronize local time with NTP server
# this function should be executed once in a couple of minutes
#   returns:    0 if completed, 1 otherwise
def ntp_synchronize():
    try:
        extra_hour = 3600
        t = ntptime.time() + extra_hour #synchronize to Central European Time (UTC+1)
        if check_summertime(t): #optionally synchronize to Central European Summer Time (UTC+2)
            t += extra_hour
        
        year, month, day, hour, minute, second = utime.localtime(t)[:6]
        set_time(year, month, day, hour, minute, second)
        return 0
    except Exception as e:
        print('[ERR] NTP synchronization failed:',e)
        return 1


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
    return utime.localtime()[3:6]


# get current date
#   returns:    a tuple of (year, month, day)
def get_date():
    return utime.localtime()[:3]


# get current date and time
#   returns:    a tuple of (year, month, day, hour, minute, second)
def get_datetime():
    return utime.localtime()[:6]



# -------------------------------------------------------------------
# aux functions
# -------------------------------------------------------------------

# check if given date should be in summertime or regular time
#   t:          current time in seconds
#   returns:    True if summertime, False if regular time
def check_summertime(t):
    # not entirely corrent implementation, but it should be enough for everyday's use - one week accuracy
    month = utime.localtime(t)[1]
    if month >= 4 and month <= 10:
        return True
    else:
        return False