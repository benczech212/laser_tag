# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT
"""NeoKey simpletest."""
import board
from adafruit_neokey.neokey1x4 import NeoKey1x4

# use default I2C bus
i2c_bus = board.I2C()

# Create a NeoKey object
neokey = NeoKey1x4(i2c_bus, addr=0x30)

print("Adafruit NeoKey simple test")

# Check each button, if pressed, light up the matching neopixel!
colors = [0xFF0000, 0xFFFF00, 0x00FF00, 0x00FFFF]

class Button:
    def __init__(self, key, color):
        self.key = key
        self.color = color
        self.pressed = False
        self.state = False

    def update(self):
        if neokey[self.key]:
            if not self.pressed:
                print(f"Button {self.key}")
                neokey.pixels[self.key] = self.color
                self.pressed = True
        else:
            neokey.pixels[self.key] = 0x0
            self.pressed = False

buttons = [Button(i, colors[i]) for i in range(4)]



while True:
    for button in buttons:
        button.update()