import bluetooth
import random
import time
from simpleBLE import BLEPeripheral
from machine import deepsleep, Pin, RTC, ADC
from math import sqrt
from time import sleep

# ADC Configuration
pin = Pin(34)
adc = ADC(pin)
adc.atten(ADC.ATTN_11DB)

# BLE configuration
ble = bluetooth.BLE()
service = "70e97b1d-bcb2-4b51-8150-bd6b184a52f5"
characteristic = "ab0d02a9-7943-44b7-9c2c-7dfd7dc9e9f9"
temp = BLEPeripheral(ble, "dre", service, characteristic)

# Measurement functions
n = 3585
s = 0.185

def VpromMed(n):
    val1 = 0
    for _ in range(n):
        val2 = adc.read()
        val1 += 3.3 * val2 / 4095
    val3 = val1 / n
    return val3

def IrmsMed(n,s):
    sumatoria = 0
    Vprom = VpromMed(n)
    for _ in range(n - 1):
        val2 = adc.read()
        vn = 3.3 * val2 / 4095
        sumatoria += ((vn - Vprom) ** 2)
    val3 = (1 / s) * sqrt(sumatoria / n)
    return val3

# Variable control
Papp = 0           
i = 0
PA = 0

while True:
        i = (i + 1) % 10
        Vprom = VpromMed(n)
        Irms = IrmsMed(n, s)
        Papp = 120 * Irms
        PA += Papp
        temp.set_values([int(PA)], notify=i == 0, indicate=False)
        print('Potencia', PA)
        time.sleep_ms(1000)
            
# Checks if the button has been pressed to enter deep sleep mode
if button_pin.value() == 1:
    deepsleep(1000)



