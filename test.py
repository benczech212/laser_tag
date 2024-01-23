import board
import digitalio
import time

# Define the pin for the IR beam sensor
sensor_pin = board.D5

# Initialize the digital input for the sensor
sensor = digitalio.DigitalInOut(sensor_pin)
sensor.direction = digitalio.Direction.INPUT
sensor.pull = digitalio.Pull.UP

# Set a threshold value for beam detection
threshold = 500  # Adjust this value based on calibration

def detect_beam():
    return sensor.value < threshold  # Sensor is active low

while True:
    sensor_value = sensor.value
    
    print(f"Sensor Value: {sensor_value}")
    
    # if detect_beam():
    #     print("Beam detected!")
    # else:
    #     print("No beam detected.")
    
    time.sleep(0.1)  # Adjust the sleep duration as needed
