# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)
#import webrepl
#webrepl.start()
# This example finds and connects to a BLE temperature sensor (e.g. the one in ble_temperature.py).
def do_connect():
    import network
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print('connecting to network...')
        sta_if.active(True)
        sta_if.connect('MONTOYA', '12345678')
        while not sta_if.isconnected():
            pass
    print('network config:', sta_if.ifconfig())

do_connect()

import bluetooth
import random
import struct
import time
import sys
from machine import deepsleep
from machine import Pin
from machine import reset
from simpleBLE import BLECentral
from os import statvfs
from time import sleep_ms
import network
from mqtt import MQTTClient 
import machine 
import json
from micropython import const
USERNAME = const('CxkVDhIIBSoZABgoHTcsJx8')
CLIENTID = const('CxkVDhIIBSoZABgoHTcsJx8')
PASS = const('LJOgyMo61KfuhaZFXOUbpvbQ')
SERVER=const('mqtt3.thingspeak.com')
CHANNEL=const('2300909')

def free_flash():
  s = statvfs('//')
  return ('{0} MB'.format((s[0]*s[3])/1048576))

# https://api.thingspeak.com/update?api_key=JGM08DVSS7Z3IX1U&field2=0
def sub_cb(topic, msg):
    print(msg[0])   
    if msg[0]==48:
       led.value(0)
    elif msg[0]==49:
        led.value(1)

print('Available flash memory: '+free_flash())


led=machine.Pin(2,machine.Pin.OUT)


client = MQTTClient(client_id=CLIENTID, server=SERVER,user=CLIENTID,password=PASS )
 

client.set_callback(sub_cb) 
client.connect()
# client.subscribe(topic='channels/'+CHANNEL+'/subscribe/fields/field2')


def showData(data):
    global done_flag
    print(data)
    done_flag=True
    client.publish(topic="channels/"+CHANNEL+"/publish", msg="field1="+ str(data)) 
    sleep_ms(500)
    if button_pin.value()==1:
        deepsleep(15000)

done_flag=False
BUTTON=0
button_pin = Pin(BUTTON, Pin.IN)


# Bluetooth object
ble = bluetooth.BLE()


# Environmental service
service = "70e97b1d-bcb2-4b51-8150-bd6b184a52f5"
characteristic = "ab0d02a9-7943-44b7-9c2c-7dfd7dc9e9f9"
# BLE Central object
central = BLECentral(ble,service,characteristic)

def on_scan(addr_type, addr, name):
    global not_found
    if addr_type is not None:
        print("Found sensor:", addr_type, addr, name)
        central.connect()
    else:
        print("No sensor found.")

central.scan(callback=on_scan)

# Wait for connection...
attempts=0
while True:
    time.sleep_ms(100)
    if central.is_connected():
        break;
    else:
        attempts=attempts+1
        if attempts==100:
            reset()
            
    
print("Connected")

central.on_notify(callback= lambda data :print('Notified') )

# Explicitly issue reads, using "print" as the callback.


central.read(callback=lambda data: showData(data[0]/3600000))
while not done_flag:
    pass
# Alternative to the above, just show the most recently notified value.
# while central.is_connected():
#     print(central.value())
#     time.sleep_ms(2000)