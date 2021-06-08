# Safety features - hardware watchdog pin and safe reboot

import machine

# -------------------------------------------------------------------
# configuration and magic numbers
# -------------------------------------------------------------------

WATCHDOG_TOGGLE_PERIOD = 100    # watchdog pin toggle period in ms
WATCHDOG_TIMER_PERIOD = 10      # virtual timer period in ms

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
# toggle_flag = False
# toggle_counter = 0
# def watchdog_timer_callback(tim):
#     global watchdog, toggle_flag, toggle_counter
#     toggle_counter += 1
#     if (toggle_counter >= int(WATCHDOG_TOGGLE_PERIOD/WATCHDOG_TIMER_PERIOD)) and (watchdog != None):
#         toggle_counter = 0
#         if toggle_flag:
#             watchdog.on()
#         else:
#             watchdog.off()
#         toggle_flag = not toggle_flag
#     # if watchdog:
#     #     watchdog.value(not watchdog.value())


# initialize watchdog pin and start a timer
def init_watchdog():
    global watchdog, watchdog_timer
    watchdog = machine.PWM(machine.Pin(WATCHDOG_PIN), freq=4)
    watchdog.duty(512)
    # watchdog = machine.Pin(WATCHDOG_PIN, machine.Pin.OUT)
    # watchdog.off()

    # watchdog_timer = machine.Timer(-1)
    # watchdog_timer.init(period=WATCHDOG_TIMER_PERIOD, mode=machine.Timer.PERIODIC, callback=watchdog_timer_callback)


# deinitialize watchdog timer
def deinit_watchdog():
    global watchdog
    if watchdog:
        watchdog.deinit()


# -------------------------------------------------------------------
# safe reboot
# -------------------------------------------------------------------

# reboot the board after setting important pins to default states
def reboot():
    print('Performing safe reboot...')
    machine.Pin(GPIO0_PIN, machine.Pin.IN, machine.Pin.PULL_UP)
    machine.Pin(GPIO2_PIN, machine.Pin.IN, machine.Pin.PULL_UP)
    machine.Pin(GPIO15_PIN, machine.Pin.IN, machine.Pin.PULL_DOWN)
    deinit_watchdog()
    machine.reset()