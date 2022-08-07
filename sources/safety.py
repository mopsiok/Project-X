# Safety features - hardware watchdog pin and safe reboot

import machine

# -------------------------------------------------------------------
# configuration and magic numbers
# -------------------------------------------------------------------

WATCHDOG_TIMER_PERIOD = 10                      # virtual timer period in ms
WATCHDOG_TIMER_PERIODS_PER_ACTIVE_STATE = 10    # virtual timer periods that corresponds to active state duration
DEFAULT_WATCHDOG_TIMER_PERIODS_PER_CLEAR = 130  # virtual timer periods that corresponds to single clear sequence duration (in main program)
BOOT_WATCHDOG_TIMER_PERIODS_PER_CLEAR = 50     # virtual timer periods that corresponds to single clear sequence duration (in boot, faster because of delay while loading scripts)
# 1.3s in normal mode, should be 1.95s (150%) when malfunction occurs
# after testing => 1.9s always generates reset, so it should be more than ok

# GPIO definitions
WATCHDOG_PIN = 14               # hardware watchdog reset pin
GPIO0_PIN = 0                   # reboot-related pin
GPIO2_PIN = 2                   # reboot-related pin
GPIO15_PIN = 15                 # reboot-related pin

# Pin object to clear external watchdog
watchdog = None

# Timer object to trigger clearing external watchdog
watchdog_timer = None


# -------------------------------------------------------------------
# watchdog
# -------------------------------------------------------------------

# callback executed by watchdog timer
period_counter = 0
period_counter_max = DEFAULT_WATCHDOG_TIMER_PERIODS_PER_CLEAR
def watchdog_timer_callback(tim):
    global watchdog, period_counter
    period_counter += 1
    if period_counter == WATCHDOG_TIMER_PERIODS_PER_ACTIVE_STATE:
        watchdog.on()
    elif period_counter >= period_counter_max:
        period_counter = 0
        watchdog.off()


# initialize watchdog pin and start a timer
# clear_periods - watchdog clear period [as multiples of WATCHDOG_TIMER_PERIOD], must be greater than 1
def init_watchdog(clear_periods = DEFAULT_WATCHDOG_TIMER_PERIODS_PER_CLEAR):
    global watchdog, watchdog_timer, period_counter, period_counter_max
    watchdog = machine.Pin(WATCHDOG_PIN, machine.Pin.OUT, value=False)
    period_counter = 0
    period_counter_max = clear_periods

    if watchdog_timer:
        watchdog_timer.deinit()
    watchdog_timer = machine.Timer(-1)
    watchdog_timer.init(period=WATCHDOG_TIMER_PERIOD, mode=machine.Timer.PERIODIC, callback=watchdog_timer_callback)

# -------------------------------------------------------------------
# safe reboot
# -------------------------------------------------------------------

pre_reboot_func = None

# Initialize pre-reboot function called before system reboot.
def init_reboot_pre_func(func = None):
    global pre_reboot_func 
    pre_reboot_func = func

# after setting important pins to default states, peform optional pre-reboot 
# function, then reboot the system.
def reboot():
    global pre_reboot_func
    if pre_reboot_func != None:
        pre_reboot_func()
    print('Performing safe reboot...')
    machine.Pin(GPIO0_PIN, machine.Pin.OUT, value=1)
    machine.Pin(GPIO2_PIN, machine.Pin.OUT, value=1)
    machine.Pin(GPIO15_PIN, machine.Pin.OUT, value=0)
    machine.reset()