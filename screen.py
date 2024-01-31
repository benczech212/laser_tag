import board
import busio
import adafruit_ssd1306
from PIL import Image, ImageDraw

# Create the I2C interface.
i2c = busio.I2C(board.SCL, board.SDA)

# Create the SSD1306 OLED class.
oled = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c)

# Clear the display.
oled.fill(0)
oled.show()

# Create an image buffer.
image = Image.new("1", (oled.width, oled.height))

# Create a drawing object.
draw = ImageDraw.Draw(image)

# Draw text on the image.
draw.text((10, 10), "Hello, OLED!", fill=1)

# Display the image.
oled.image(image)
oled.show()
