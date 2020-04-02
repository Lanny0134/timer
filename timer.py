import schedule
import time
import RPi.GPIO as GPIO

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(11, GPIO.OUT, initial=GPIO.LOW)             #GPIO pin 11 is relay
GPIO.setup(13, GPIO.OUT, initial=GPIO.LOW)             #GPIO pin 13 is LED
GPIO.setup(15, GPIO.IN, pull_up_down=GPIO.PUD_UP)      #GPIO pin 15 is button

pos = False         #position of relay
lock = False        #locks to off
delay = False       #toggles delay
ontime = "09:00"    #sets on time
offtime = "21:00"   #sets off time
delaytime = "11:00" #sets delayed on time

def switch(cmd):
    global pos
    global lock
    global delay
    if cmd == 1 and lock == False:      #switches relay on and delay off
        delay = False
        schedule.clear('on')
        schedule.every().day.at(ontime).tag('on').do(switch, 1)
        GPIO.output(11, GPIO.HIGH)
    elif  cmd == 0:                       #switches relay off
        GPIO.output(11, GPIO.LOW)
        pos = False
    elif cmd == 3:                      #switches relay to opposite position and turns lock off
        if pos == True:
            GPIO.output(11, GPIO.LOW)
            pos = False
        elif pos == False:
            GPIO.output(11, GPIO.HIGH)
            pos = True
            lock = False


def flash(num):
    speed = 0.5 #change speed of flashing
    while num > 0:
        GPIO.output(13, GPIO.HIGH)
        time.sleep(speed)
        GPIO.output(13, GPIO.LOW)
        num = num - 1
        if num == 0:
            break
        time.sleep(speed)

def tdelay():
    global delay
    if delay == False:
        delay = True
        flash(2)
        schedule.clear('on')
        schedule.every().day.at(delaytime).tag('on').do(switch, 1)
    elif delay == True:
        delay = False
        flash(1)
        schedule.clear('on')
        schedule.every().day.at(ontime).tag('on').do(switch, 1)


def bpush(self):
    GPIO.remove_event_detect(15)
    global lock
    global delay
    loopcount = 0
    while GPIO.input(15) == GPIO.LOW:      #loop to time button press
        time.sleep(0.05)
        loopcount = loopcount + 0.05
    if loopcount >= 0.05 and loopcount < 1: #switches relay
        switch(3)
    if loopcount >= 1 and loopcount < 3:    #toggles delay
        tdelay()
    if loopcount >= 3:                      #turns on lock
        lock = True
        flash(4)
    GPIO.add_event_detect(15, GPIO.FALLING, callback=bpush)



GPIO.add_event_detect(15, GPIO.FALLING, callback=bpush)     #detects button and starts callback

schedule.every().day.at(ontime).tag('on').do(switch, 1)
schedule.every().day.at(offtime).do(switch, 0)

try:
    while True:
        schedule.run_pending()
        time.sleep(5)

finally:
    GPIO.cleanup()