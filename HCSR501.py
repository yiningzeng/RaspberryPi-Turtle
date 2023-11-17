#!/user/bin/env python 
import smbus
import time
import sys
import RPi.GPIO as GPIO
HC_SR501 = 12 

GPIO.setmode(GPIO.BCM)
GPIO.setup(HC_SR501, GPIO.OUT)
GPIO.output(HC_SR501, GPIO.LOW)
if __name__ == '__main__':  
    while True:
        print("nonething")
        time.sleep(1)
        GPIO.output(HC_SR501, GPIO.LOW)
