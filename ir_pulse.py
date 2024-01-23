import board
import digitalio
import multiprocessing
import time
from datetime import datetime

# Define the pin for the IR beam sensor
sensor_pin = board.D5

# Define the pin for the IR blaster (assuming it's connected to this pin)
ir_blaster_pin = board.D6

# Initialize the digital input for the sensor
sensor = digitalio.DigitalInOut(sensor_pin)
sensor.direction = digitalio.Direction.INPUT
sensor.pull = digitalio.Pull.UP

# Initialize the digital output for the IR blaster
ir_blaster = digitalio.DigitalInOut(ir_blaster_pin)
ir_blaster.direction = digitalio.Direction.OUTPUT


ir_blaster.value = False



def beam_detect():
    if sensor.value == 1:
        print("Beam detected!")
    else:
        print("no beam")

def pulse_ir_blaster(message):
    ir_blaster.value = True
    time.sleep(1)
    ir_blaster.value = False
    time.sleep(0.1)
    ir_blaster.value = True
    time.sleep(0.1)
    for bit in message:
        ir_blaster.value = True if bit == '1' else False
        time.sleep(0.1)


while True:
    beam_detect()
    pulse_ir_blaster("11111011011110000")

