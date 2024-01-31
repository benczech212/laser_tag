import time
import digitalio as dio
import board
import threading
import os
import subprocess
import math
from adafruit_seesaw import seesaw, rotaryio, digitalio, neopixel
from adafruit_neokey.neokey1x4 import NeoKey1x4



i2c_bus = board.I2C()
seesaw = seesaw.Seesaw(i2c_bus)
seesaw_product = (seesaw.get_version() >> 16) & 0xFFFF
print("Found product {}".format(seesaw_product))
if seesaw_product != 4991:
    print("Wrong firmware loaded?  Expected 4991")

# Configure seesaw pin used to read knob button presses
# The internal pull up is enabled to prevent floating input
seesaw.pin_mode(24, seesaw.INPUT_PULLUP)
button = digitalio.DigitalIO(seesaw, 24)



sensor_pin = board.D5
ir_blaster_pin = board.D6
trigger_bin = board.D13



# Initialize the digital input for the sensor


# trigger = dio.DigitalInOut(trigger_bin)
# trigger.direction = dio.Direction.INPUT
# trigger.pull = dio.Pull.UP


# # Initialize the digital output for the IR blaster
# ir_blaster = dio.DigitalInOut(ir_blaster_pin)
# ir_blaster.direction = dio.Direction.OUTPUT

# Shared variable for the encoded message with preamble



bit_delay = 0.001

# Event to signal when to start pulsing the IR blaster


firing_message_format = "{type}{player_id}{damage_id}{special_id}{duration_id}{target_id}"

type_bit_dict = {
        0:'shot',
        1:'none',
    }
player_id_dict = {
        0:{'name':'Environment'},
        1:{'name':'Team 1'},
        2:{'name':'Team 2'},
        3:{'name':'Team 3'},
        4:{'name':'Player 1'},
        5:{'name':'Player 2'},
        6:{'name':'Player 3'},
        7:{'name':'Player 4'},
        8:{'name':'Player 5'},
        9:{'name':'Player 6'},
        10:{'name':'Player 7'},
        11:{'name':'Player 8'},
        12:{'name':'Player 9'},
        13:{'name':'Player 10'},
        14:{'name':'Player 11'},
        15:{'name':'Player 12'},
    }
damage_bit_dict = {
        0:{'damage':1,'name':'Smallest Damage'},
        1:{'damage':2,'name':'Very Small Damage'},
        2:{'damage':4,'name':'Small Damage'},
        3:{'damage':8,'name':'Average Damage'},
        4:{'damage':16,'name':'Moderate Damage'},
        5:{'damage':32,'name':'High Damage'},
        6:{'damage':64,'name':'Very High Damage'},
        7:{'damage':-128,'name':'Full Recovery'},
        8:{'damage':-64,'name':'Partial Recovery'},
        9:{'damage':-32,'name':'Quarter Recovery'},
        10:{'damage':-16,'name':'Eight Recovery'},
        11:{'damage':-8,'name':'Sixteenth Recovery'},
        12:{'damage':-4,'name':'Small Recovery'},
        13:{'damage':-2,'name':'Very Small Recovery'},
        14:{'damage':-1,'name':'Smallest Recovery'},
        15:{'damage':0,'name':'No Damage'},
    }
special_bit_dict = {
    0:{'name':'None','function':None},
    1:{'name':'Get Hit x2','function':None},
    2:{'name':'Get Hit x4','function':None},
    3:{'name':'Get Hit x8','function':None},
    5:{'name':'Rapid Fire','function':None},
    6:{'name':'Unlimited Mana','function':None},
    7:{'name':'Weapon Disabled','function':None},
    8:{'name':'Weapon Jam','function':None},
    9:{'name':'Weapon Noisy','function':None},
    10:{'name':'Weapon Overheated','function':None},
    11:{'name':'Weapon Slow','function':None},
    12:{'name':'Weapon Weak','function':None},
    13:{'name':'Weapon Strong','function':None},
}
duration_bit_dict = {
    0:{'name':'None','function':None},
    1:{'name':'5 Seconds','function':None},
    2:{'name':'10 Seconds','function':None},
    3:{'name':'15 Seconds','function':None},
}
target_bit_dict = {
    0:{'name':'Enemy','function':None},
    1:{'name':'Friendly','function':None},
    2:{'name':'Neutral','function':None},
    3:{'name':'None','function':None},
}


class MessageEncoder:


    def __init__(self,ir_blaster):
        self.ir_blaster = ir_blaster
    def blast_ir_message(self,message):
        print(f"Blasting IR Message")
        full_message = self.package_message(message)
        print(f"full message: {full_message}")
        for bit in full_message:
            self.ir_blaster.value = int(bit)
            time.sleep(bit_delay)
        
        self.ir_blaster.value = True
    def package_message(self,message):
        preamble = '1' * (len(message)-1) + "0"
        full_message = preamble + message
        return full_message




class Weapon:
    def __init__(self,trigger_pin,blaster_bin,player):
        self.player = player
        self.player_id = player.player_id
        self.player_name = player_id_dict[player.player_id]
        
        self.trigger = dio.DigitalInOut(trigger_pin)
        self.trigger.direction = dio.Direction.INPUT
        self.trigger.pull = dio.Pull.UP

        self.blaster = dio.DigitalInOut(blaster_bin)
        self.blaster.direction = dio.Direction.OUTPUT
        self.message_encoder = MessageEncoder(self.blaster)

        self.firing = False
        self.blaster.value = True
        self.fully_automatic = False
        self.firing_delay = 1
        self.fire_ready = True
        self.special_id = 0
        self.duration_id = 0
        self.target_selection_id = 0
        self.damage_id = 6
        

    def get_firing_message(self):
        type = '0'
        # player_id = bin(self.player_id)[2:].zfill(4)
        # damage_id = bin(self.damage_id)[2:].zfill(4)
        # special_id = bin(self.special_id)[2:].zfill(4)
        # duration_id = bin(self.duration_id)[2:].zfill(4)
        # target_id = bin(self.target_selection_id)[2:].zfill(4)
        # firing_message = f'{type}{player_id}{damage_id}{special_id}{duration_id}{target_id}'
        firing_message = '01' * 4
        print(firing_message)
        return firing_message

    def check_trigger_press(self):
        if self.trigger.value == 0: return True
        else: return False

 

    def fire(self):
        print("Firing")
        # threading.Thread(target=play_sound).start()
        selected_button = self.player.hotbar.buttons[self.player.hotbar.selected_button]
        threading.Thread(selected_button.start_cooldown()).start()
        firing_message = self.get_firing_message()
        self.message_encoder.blast_ir_message(firing_message)
    
    def check_triggers(self):
        if self.check_trigger_press() and self.fire_ready:
            self.fire()
        else: pass

class SoundManager:
    def __init__(self):
        self.sound_path = "Sounds"
        self.sound_files = os.listdir(self.sound_path)
        self.sound_files.sort()
    def play_sound(self,sound_name):
        file = f"{self.sound_path}/{sound_name}"
        subprocess.call(['aplay', file])

class RotoryEncoder:
    def __init__(self,i2c_bus,seesaw,addr=0x3F):
        self.seesaw = seesaw
        self.encoder = rotaryio.IncrementalEncoder(seesaw)
        self.button = digitalio.DigitalIO(seesaw, 24)
        self.pixel = neopixel.NeoPixel(seesaw, 6, 1)
        self.pixel.brightness = 0.5
        self.pixel.fill((255,0,0))

        self.last_position = None
        self.button_down = False
    def update_loop(self):
        position = -self.encoder.position
        if position != self.last_position:
            print(position)
            self.last_position = position
            self.pixel.fill(hsv_to_rgb((position % 360,1,1)))
        if not self.button.value and not self.button_down:
            print("Button Pressed")
            self.button_down = True
        if self.button.value and self.button_down:
            print("Button Released")
            self.button_down = False


class HotbarButton:
    def __init__(self, key, color, neokey, hotbar,sound_name='Default'):
        self.neokey = neokey
        self.hotbar = hotbar
        self.key = key
        self.on_color = color
        self.current_color = color
        self.off_color = (0,0,0)
        self.pressed = False
        self.sound_name = sound_name
        self.fire_ready = True
        self.available_animation() if self.fire_ready else self.recharging_animation()
        self.cooldown_duration = 10
        
    
    def start_cooldown(self):
        self.fire_ready = False
        steps = 24
        for i in range(steps):
            t = i / steps
            delay = self.cooldown_duration / steps
            time.sleep(delay)
            self.recharging_animation(t**2)
            
        

    def set_on_color(self,color):
        self.on_color = color
    
    def available_animation(self):
        self.neokey.pixels[self.key] = self.on_color
    def recharging_animation(self,t):
        self.neokey.pixels[self.key] = lerpn(self.off_color,self.on_color,t,make_int=True)
    def selected_animation(self):
        brightness = math.sin(time.monotonic() * 10) * 0.5 + 0.5
        self.current_color = [int(c * brightness) for c in self.on_color]
        self.neokey.pixels[self.key] = self.current_color

    def update_loop(self):
        if self.hotbar.selected_button == self.key:
            self.selected_animation()
                
        if self.neokey[self.key]:
            if not self.pressed:
                print(f"Button {self.key} pressed")
                self.pressed = True
                self.available_animation()
        else:
            if self.pressed:
                print(f"Button {self.key} released")
                self.hotbar.selected_button = self.key
            self.pressed = False


class PlayerInputs:
    def __init__(self,i2c_bus,seesaw,player,key_addr = 0x30,encoder_addr = 0x3F,button_count = 4):
        self.player = player
        self.seesaw = seesaw
        self.neokey = NeoKey1x4(i2c_bus, addr=key_addr)
        self.encoder = RotoryEncoder(i2c_bus,seesaw,addr=encoder_addr)
        self.button_colors = [(0,0,255), (0,255,0), (255,0,255), (255,255,255)]
        self.buttons = [HotbarButton(i, self.button_colors[i],self.neokey,self) for i in range(button_count)]
        self.selected_button = 0
        
    def get_player_inputs(self):
        for button in self.buttons:
            button.update_loop()
        self.encoder.update_loop()

def lerp(v1,v2,t):
    return v1 + (v2 - v1) * t
def lerpn(c1,c2,t,make_int=False):
    return tuple([int(lerp(v1,v2,t)) for v1,v2 in zip(c1,c2)]) if make_int else tuple([lerp(v1,v2,t) for v1,v2 in zip(c1,c2)])

def rgb_to_hsv(rgb):
    r,g,b = rgb
    r,g,b = r/255,g/255,b/255
    cmax = max(r,g,b)
    cmin = min(r,g,b)
    delta = cmax - cmin
    if delta == 0: h = 0
    elif cmax == r: h = ((g-b)/delta) % 6
    elif cmax == g: h = ((b-r)/delta) + 2
    elif cmax == b: h = ((r-g)/delta) + 4
    h *= 60
    if h < 0: h += 360
    if cmax == 0: s = 0
    else: s = delta / cmax
    v = cmax
    return (h,s,v)
def hsv_to_rgb(hsv):
    h,s,v = hsv
    c = v * s
    x = c * (1 - abs((h/60)%2 - 1))
    m = v - c
    if h < 60: r,g,b = c,x,0
    elif h < 120: r,g,b = x,c,0
    elif h < 180: r,g,b = 0,c,x
    elif h < 240: r,g,b = 0,x,c
    elif h < 300: r,g,b = x,0,c
    elif h < 360: r,g,b = c,0,x
    r,g,b = (r+m)*255,(g+m)*255,(b+m)*255
    return (int(r),int(g),int(b))


class IrSensor:
    def __init__(self,pin):
        self.pin = pin
        self.sensor = dio.DigitalInOut(pin)
        self.sensor.direction = dio.Direction.INPUT
        self.sensor.pull = dio.Pull.UP

class IrBlaster:
    def __init__(self,pin):
        self.pin = pin
        self.blaster = dio.DigitalInOut(pin)
        self.blaster.direction = dio.Direction.OUTPUT
class Hitbox:
    def __init__(self,ir_sensor_pins,player):
        self.player = player
        self.ir_sensor_pins = ir_sensor_pins
        self.ir_sensors = [IrSensor(pin) for pin in ir_sensor_pins]
    def check_for_hit(self):
        for sensor in self.ir_sensors:
            if sensor.sensor.value == 0:
                print(f"Hit on sensor {sensor.pin}")
            else: pass
            


class Player:
    def __init__(self,player_id=0,team_id=0):
        self.player_id = player_id
        self.set_team(team_id)
        self.health = 128
        self.mana = 128
        self.name = player_id_dict[player_id]['name']
        self.gun = Weapon(trigger_bin,ir_blaster_pin,self)
        self.hotbar = PlayerInputs(i2c_bus,seesaw,self)
        self.hitbox = Hitbox([sensor_pin],self)
        print(f"Created Player {self.name} on team {self.team_id}")
    def set_team(self,team_id):
        self.team_id = team_id
        

    def game_loop(self):
        self.gun.check_triggers()
        self.hotbar.get_player_inputs()
        self.hitbox.check_for_hit()



player = Player(4,0)
# team_count = 3
# teams = [Team() for i in range(team_count)]
# teams[0].add_player(player)
# game  = Game(teams=teams)

tick_count = 0


print("Starting...")
if __name__ == "__main__":
    while True:
        player.game_loop()
        tick_count += 1