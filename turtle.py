#!/usr/bin/python
import sys
import time
import datetime
import pymysql
import Adafruit_DHT
import RPi.GPIO as GPIO
import logging
import smbus
import LCD1602 as LCD

LCD.init_lcd()
time.sleep(0.5)
LCD.print_lcd(0, 0, 'yining~starting')
logging.getLogger().setLevel(logging.INFO)

GPIO_Alarm = 12
HC_SR501 = 24
GPIO_OUT = 23

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(GPIO_OUT, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(HC_SR501, GPIO.IN)
GPIO.setup(GPIO_Alarm, GPIO.OUT)

logging.info("start")
LCD.print_lcd(0, 0, 'mysql~connecting')

GPIO.output(GPIO_OUT, GPIO.HIGH)# 风扇开
#蜂鸣器开，测试是否坏掉
GPIO.output(GPIO_Alarm, GPIO.HIGH)
time.sleep(0.1)
GPIO.output(GPIO_Alarm, GPIO.LOW)
GPIO.output(GPIO_OUT, GPIO.LOW)# 风扇开
#蜂鸣器开，测试是否坏掉
conn = pymysql.connect(host="localhost", port=13399, user="root",passwd="pass",db="turtle")

sumT = 0;sumH = 0;avgT = -1;avgH = -1;count = 0
minT = 99;minH = 99;maxT = -1;maxH = -1
i = 0 # 用于轮询显示
fanOpen = 0

refreshInterval = 20 #读取温湿度间隔
fanOpenTime = 10 #风扇开启持续时间
tempLimit = 15 #温度阈值，高于这个才开风扇
tempAlarm = 35 #温度高报警

def getSettings():
    global refreshInterval
    global fanOpenTime
    global tempLimit
    global tempAlarm
    cursor = conn.cursor()
    cursor.execute("select refresh_interval, fan_open_time, temp_limit, temp_alarm from settings order by create_time desc")
    setting = cursor.fetchone()
    refreshInterval = setting[0] #读取温湿度间隔
    fanOpenTime = setting[1] #风扇开启持续时间
    tempLimit = setting[2] #温度阈值，高于这个才开风扇
    tempAlarm = setting[3] #温度高报警
    logging.info('采集间隔:{:0.0f}S 风扇开启时间:{:0.0f}S 温度阈值:{:0.0f}C 温度报警:{:0.0f}C'.format(refreshInterval, fanOpenTime, tempLimit, tempAlarm))

#用于检测是否有人经过，经过就打开显示屏
def checkPeople():
    if GPIO.input(HC_SR501) == True:
        logging.info("open light")
        LCD.turn_light(1)
    else:
        logging.info("close light")
        LCD.turn_light(0)

#用于开启风扇后的lcd显示
def fan(n):
    strfan = ' '
    if n == 0:
        strfan = 'X'
    elif n == 1:
        strfan = '+'
    LCD.print_lcd(4, 0, strfan)

#获取lcd的进度显示
def getloing(n):
    if n == 0:
        #tt = datetime.datetime.now().hour
        #if tt > 16 and tt < 24 or tt > 6 and tt < 11:
        #    LCD.turn_light(1)
        return '*--'
    elif n == 1:
        return '**-'
    elif n == 2:
        return '***'
    elif n == 3:
        return '***'
    elif n == 4:
        #LCD.turn_light(0)
        return '***'
    else:
        return '$$$'

if __name__ == '__main__':
    LCD.print_lcd(0, 0, 'Getting Settings')
    getSettings()
    LCD.print_lcd(0, 1, '{:0.0f}S {:0.0f}S {:0.0f}C {:0.0f}C'.format(refreshInterval, fanOpenTime, tempLimit, tempAlarm))
    time.sleep(1)
    while True:
        hour = datetime.datetime.now().hour
        minute = datetime.datetime.now().minute
        if hour == 0 and minute == 0:
            sumT = 0;sumH = 0;avgT = -1;avgH = -1;count = 0
            minT = 99;minH = 99;maxT = -1;maxH = -1
        if i == 0:
            # “11”代表你使用的是DHT11传感器，如果你使用的是DHT22传感器，则把数字改成“22”即可。
            #数字“4”代表你的信号引脚连接的是gpio4，而不是“pin4”
            humidity, temperature = Adafruit_DHT.read_retry(11, 4)
            count = count + 1
            sumT = sumT + temperature
            sumH = sumH + humidity
            avgT = sumT / count
            avgH = sumH / count
            if minT > temperature:
                minT = temperature
            if minH > humidity:
                minH = humidity
            if maxT < temperature:
                maxT = temperature
            if maxH < humidity:
                maxH = humidity
            #空气温度以小数点后一位展示，加上℃单位，空气湿度加上%。注意，如果湿度或温度的值为None，这个语句就会报错
            logging.info('Temp: {:0.1f} C Humidity: {:0.1f} %'.format(temperature, humidity))
            LCD.print_lcd(0, 0, 'NOW  T:{:0.0f}C H:{:0.0f}%            '.format(temperature, humidity))
            LCD.print_lcd(0, 1, '{:0.0f}-{:0.0f}C {:0.0f}-{:0.0f}% {:0.0f}'.format(minT, maxT, minH, maxH, avgT))
            sql = "INSERT INTO info (temperature, humidity, time) VALUES ({0:0.1f},{1:0.1f}, NOW())".format(temperature, humidity)
            conn.query(sql)
            conn.commit()

            getSettings()
            if temperature > tempLimit:
                GPIO.output(GPIO_OUT, GPIO.HIGH)# 风扇开
                fanOpen = 1
                logging.info('开风扇')
            else:
                fanOpen = 0
                GPIO.output(GPIO_OUT, GPIO.LOW) # 风扇关闭
                logging.info('温度不足v{:0.1f} ，风扇不开'.format(tempLimit))
            #time.sleep(5)
        checkPeople()
        if fanOpen == 1:
            fan(i%2)
        else:
            fan(3)
        LCD.print_lcd(0, 0, getloing(i%5))
        i = i + 1
        if i >= refreshInterval:
            i = 0
        if fanOpen == 1:
            fanOpenTime = fanOpenTime - 1
            logging.info('风扇剩余: {:0.0f}S'.format(fanOpenTime))
            if fanOpenTime <= 0:
                fanOpen = 0
                GPIO.output(GPIO_OUT, GPIO.LOW) # 风扇关闭
                logging.info('时间到了，风扇关')
        time.sleep(1)
