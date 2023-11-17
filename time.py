#!/user/bin/env python 
import smbus
import time
import sys
import LCD1602 as LCD
 
if __name__ == '__main__':  
    LCD.init_lcd()
    time.sleep(1)
    LCD.print_lcd(4, 0, 'baymin~~~')
    for x in range(1, 4):
        LCD.turn_light(0)
        LCD.print_lcd(4, 1, 'LIGHT OFF')
        time.sleep(0.5)
        LCD.turn_light(1)
        LCD.print_lcd(4, 1, 'LIGHT ON ')
        time.sleep(0.5)
 
   # LCD.turn_light(0)
    while True:
        now = time.strftime('%Y%m%d %H:%M:%S', time.localtime(time.time()))
        now = now[2:]
        s = now[13:14]
        if int(s) % 2 == 0:
            LCD.turn_light(1)
        else:
            LCD.turn_light(0)
        LCD.print_lcd(2, 0, s)
        LCD.print_lcd(0, 1, now)
        time.sleep(0.5)
