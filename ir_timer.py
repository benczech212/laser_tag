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

# Event to signal when to pulse the IR blaster
pulse_event = multiprocessing.Event()
beam_event = multiprocessing.Event()

# Flag to indicate whether the IR blaster should be pulsing
pulse_flag = multiprocessing.Value('b', True)
beam_flag = multiprocessing.Value('b', True)

# Variables to track beam detection intervals
beam_last_detected = None
beam_last_lost = None
shortest_interval = float('inf')

delay_min = 0
delay_max = 0.5
tick_count = 0

tick_max = 24
def lerp(v1, v2, t):
    return v1 + (v2 - v1) * t

def toggle_ir_blaster(pulse_flag, pulse_event):
    global tick_count
    while pulse_flag.value:
        tick_count = tick_count % tick_max
        t = (tick_count/tick_max) * 10
        a = 0.01
        delay = a**t
        pulse_event.wait()  # Wait for the event to be set (beam detected)
        ir_blaster.value = not ir_blaster.value
        time.sleep(delay)     
        tick_count += 1
beam_last_detected = datetime.now()
beam_last_lost = datetime.now()
shortest_interval = float('inf')
duration = float('inf')

def beam_detect(beam_flag, beam_event):
    global beam_last_detected, beam_last_lost, shortest_interval,duration
    while beam_flag.value:
        beam_event.wait()
        now = datetime.now()
        
        if sensor.value:
            if beam_last_lost is not None:
                duration = (now - beam_last_lost).total_seconds()
            beam_last_detected = now
            
            state_text = 'Beam detected!'
            print(f"{now} - {state_text.ljust(15)} | last_changed: {interval:.4f}s | shortest Interval: {duration:.4f}s")
        else:
            beam_last_lost = now
            interval = (now - beam_last_detected).total_seconds()
            state_text = 'Beam lost!'
            print(f"{now} - {state_text.ljust(15)} | last_changed: {interval:.4f}s | shortest Interval: {duration:.4f}s")

# Create processes for pulsing the IR blaster and detecting the beam
pulse_process = multiprocessing.Process(target=toggle_ir_blaster, args=(pulse_flag, pulse_event))
detect_process = multiprocessing.Process(target=beam_detect, args=(beam_flag, beam_event))

try:
    pulse_process.start()  # Start the process
    detect_process.start()

    while True:
        for i in range(10):
            toggle_ir_blaster(pulse_flag, pulse_event)
            

        pulse_event.set()
        beam_event.set()

except KeyboardInterrupt:
    pulse_flag.value = False  # Set the pulse flag to False on KeyboardInterrupt
    pulse_event.set()        # Set the event to exit the pulse process
    pulse_process.join()      # Wait for the pulse process to finish

    
    beam_flag.value = False   # Set the beam flag to False on KeyboardInterrupt
    beam_event.set()          # Set the event to exit the detect process
    detect_process.join()     # Wait for the detect process to finish
    print("Exiting program.")