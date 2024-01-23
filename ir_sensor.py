import RPi.GPIO as GPIO
import time

# Define the IR LED and sensor pins
ir_led_pin = 6  # Replace with the actual pin number where your IR LED is connected
ir_sensor_pin = 5  # Replace with the actual pin number where your IR sensor is connected
# GPIO.setmode(GPIO.BOARD)
# Initialize GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(ir_led_pin, GPIO.OUT)
GPIO.setup(ir_sensor_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Create an IR encoder for the IR LED
data_to_send = [1, 0, 1, 0, 1, 0, 1, 0]

# Transmit the data
try:
    for bit in data_to_send:
        GPIO.output(ir_led_pin, GPIO.HIGH if bit == 1 else GPIO.LOW)
        time.sleep(0.0005)  # Adjust the pulse duration
finally:
    GPIO.cleanup()

# Detect the IR signal
try:
    while True:
        ir_sensor_value = GPIO.input(ir_sensor_pin)
        print(f"IR Sensor Value: {ir_sensor_value}")
        time.sleep(0.1)  # Adjust the detection interval
except KeyboardInterrupt:
    print("Exiting program.")
finally:
    GPIO.cleanup()