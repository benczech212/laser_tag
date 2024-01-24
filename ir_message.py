import time
import digitalio
import board
import threading
import os
import subprocess
sensor_pin = board.D5
ir_blaster_pin = board.D6
trigger_bin = board.D13



# Initialize the digital input for the sensor
sensor = digitalio.DigitalInOut(sensor_pin)
sensor.direction = digitalio.Direction.INPUT
sensor.pull = digitalio.Pull.UP


trigger = digitalio.DigitalInOut(trigger_bin)
trigger.direction = digitalio.Direction.INPUT
trigger.pull = digitalio.Pull.UP


# Initialize the digital output for the IR blaster
ir_blaster = digitalio.DigitalInOut(ir_blaster_pin)
ir_blaster.direction = digitalio.Direction.OUTPUT

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




class Gun:
    def __init__(self,trigger_pin,blaster_bin,player_id=0):
        self.player_id = player_id
        self.player_name = player_id_dict[player_id]
        
        self.trigger = digitalio.DigitalInOut(trigger_pin)
        self.trigger.direction = digitalio.Direction.INPUT
        self.trigger.pull = digitalio.Pull.UP

        self.blaster = digitalio.DigitalInOut(blaster_bin)
        self.blaster.direction = digitalio.Direction.OUTPUT
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

    
    def fire_cooldown(self):
        time.sleep(self.firing_delay)
        self.fire_ready = True

    def fire(self):
        print("Firing")
        self.fire_ready = False
        firing_message = self.get_firing_message()
        self.message_encoder.blast_ir_message(firing_message)
        threading.Thread(target=self.fire_cooldown).start()
    
    def main_loop(self):
        while True:
            if self.check_trigger_press() and self.fire_ready:
                self.fire()
            else: pass
            
def play_sound():
    # use command sudo aplay "$file" to play sound
    file = "sounds/shot.wav"
    subprocess.call(['aplay', file])

gun = Gun(trigger_bin,ir_blaster_pin)

print("Starting...")
if __name__ == "__main__":
    while True:
            gun.main_loop()
            # time.sleep(bit_delay * len(encoded_message) )