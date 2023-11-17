#!/user/bin/env python 
import smbus
import time
import sys
import RPi.GPIO as GPIO
from threading import Thread

HC_SR501 = 12 

GPIO.setmode(GPIO.BCM)
GPIO.setup(HC_SR501, GPIO.OUT)
GPIO.output(HC_SR501, GPIO.LOW)

def alarm():
    while True:
        time.sleep(0.5)
        GPIO.output(HC_SR501, GPIO.HIGH)
        print("HIGH")
        time.sleep(0.5)
        GPIO.output(HC_SR501, GPIO.LOW)
        print("LOW")

if __name__ == '__main__':
    #t = Thread(target=alarm)
    #t.start()
    while True:
        print("nonething")
        time.sleep(1)
