import board
import digitalio
import pulseio
import time

# Define the pin for the IR beam sensor
sensor_pin = board.D5

# Define the pin for the IR blaster (assuming it's connected to this pin)
ir_blaster_pin = board.D6

# Define the pin for the IR receiver
ir_receiver_pin = board.D18

# Initialize the digital input for the sensor
sensor = digitalio.DigitalInOut(sensor_pin)
sensor.direction = digitalio.Direction.INPUT
sensor.pull = digitalio.Pull.UP

# Initialize the digital output for the IR blaster
ir_blaster = digitalio.DigitalInOut(ir_blaster_pin)
ir_blaster.direction = digitalio.Direction.OUTPUT

# Initialize the pulse input for the IR receiver
pulsein = pulseio.PulseIn(ir_receiver_pin, maxlen=120, idle_state=True)

# Set a threshold value for beam detection
threshold = 500  # Adjust this value based on calibration

def detect_beam():
    return sensor.value < threshold  # Sensor is active low

def send_binary_message(message):
    for bit in message:
        if bit == '1':
            ir_blaster.value = True
        else:
            ir_blaster.value = False
        
        time.sleep(0.01)  # Adjust the duration of the pulse as needed
        ir_blaster.value = False
        time.sleep(0.01)  # Adjust the gap between pulses

def receive_binary_message():
    pulses = pulsein[:]
    binary_message = ''
    
    for pulse in pulses:
        if pulse > 500:  # Adjust this threshold based on your IR receiver characteristics
            binary_message += '1'
        else:
            binary_message += '0'
    
    return binary_message

while True:
    sensor_value = sensor.value
    
    print(f"Sensor Value: {sensor_value}")
    
    if detect_beam():
        print("Beam detected!")
        message_to_send = "10101100"  # Replace with your binary message
        send_binary_message(message_to_send)
        
        received_message = receive_binary_message()
        print(f"Received Message: {received_message}")
    else:
        print("No beam detected.")
    
    time.sleep(0.1)  # Adjust the sleep duration as needed
