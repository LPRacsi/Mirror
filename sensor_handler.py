import subprocess
import time

import RPi.GPIO as GPIO

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(7, GPIO.IN)  # Read output from PIR motion sensor
count = 0
screenOn = True

while True:
    i = GPIO.input(7)
    time.sleep(0.1)
    if i == 0:  # When output from motion sensor is LOW
        # print("No intruders", i)
        print('Count ', count)
        if count >= 600 and screenOn:
            print('Screen off')
            subprocess.run('fbset -accel false', shell=True)
            subprocess.run('tvservice -o', shell=True)
            screenOn = False
            # os.system("sh screen_off.sh")
        else:
            count += 1
    elif i == 1:  # When output from motion sensor is HIGH
        print("Intruder detected", time.time())
        count = 0
        # subprocess.call('./screen_on.sh')
        # os.system("sh screen_on.sh")
        if not screenOn:
            print('Screen on')
            subprocess.run('tvservice -p', shell=True)
            subprocess.run('fbset -accel true', shell=True)
            screenOn = True
