'''RP2040 Prop-Maker BD-1 animation'''

import time
import board
import audiobusio
import audiomixer
import displayio
import terminalio
from adafruit_display_text import label
import adafruit_displayio_ssd1306
from i2cdisplaybus import I2CDisplayBus
import terminalio
from digitalio import DigitalInOut, Direction, Pull
import neopixel
from adafruit_led_animation.animation.rainbow import Rainbow
from adafruit_led_animation.animation.rainbowchase import RainbowChase
from adafruit_led_animation.animation.rainbowcomet import RainbowComet
from adafruit_led_animation.animation.rainbowsparkle import RainbowSparkle
from adafruit_led_animation.sequence import AnimationSequence
from adafruit_led_animation.animation.comet import Comet
from adafruit_led_animation.animation.blink import Blink
from adafruit_led_animation.animation.pulse import Pulse
from adafruit_led_animation.animation.sparklepulse import SparklePulse
from adafruit_led_animation import helper
from adafruit_led_animation.helper import PixelSubset
from adafruit_led_animation.color import PURPLE, JADE, AMBER, BLUE, RED, GREEN, WHITE, TEAL
import adafruit_lis3dh
from audiomp3 import MP3Decoder
import random
import analogio

# Get Battery Voltage
vbat_voltage = analogio.AnalogIn(board.A1)

def get_voltage(pin):
    return pin.value / 65535 * 3.3 * 2


# enable external power pin
# provides power to the external components
external_power = DigitalInOut(board.EXTERNAL_POWER)
external_power.direction = Direction.OUTPUT
external_power.value = True

# i2s playback
# The listed mp3files will be played randomly
mp3files = ["bd-1-sound-1-22050-mono.mp3", "bd-1-woo-hoo-22050-mono.mp3", "bd-1-rebels-fanfare-22050-mono.mp3"]

# You have to specify some mp3 file when creating the decoder
mp3 = open(mp3files[0], "rb")
decoder = MP3Decoder(mp3)
audio = audiobusio.I2SOut(board.I2S_BIT_CLOCK, board.I2S_WORD_SELECT, board.I2S_DATA)
mixer = audiomixer.Mixer(voice_count=1, sample_rate=22050, channel_count=1 ,
                         bits_per_sample=16, samples_signed=True, buffer_size=8192)

mixer.voice[0].level = 0.5

# Side Head LEDs
red_leds = DigitalInOut(board.D12)
red_leds.direction = Direction.OUTPUT

# OLED I2C display
displayio.release_displays()

i2c = board.I2C()  # uses board.SCL and board.SDA
display_bus = I2CDisplayBus(i2c, device_address=0x3C)
WIDTH = 128
HEIGHT = 32
BORDER = 1

display = adafruit_displayio_ssd1306.SSD1306(display_bus, width=WIDTH, height=HEIGHT)

# Make the display context
splash = displayio.Group()
display.root_group = splash

color_bitmap = displayio.Bitmap(WIDTH, HEIGHT, 1)
color_palette = displayio.Palette(1)
color_palette[0] = 0xFFFFFF  # White

# Draw a label
text = "BD-3 System: Nominal" + "\nVBat: "
text_area = label.Label(terminalio.FONT, text=text, color=0xFFFFFF, x=1, y=4)
splash.append(text_area)
vbat_text = "online"
vbat_text_area = label.Label(terminalio.FONT, text=vbat_text, color=0xFFFFFF, x=35, y=18)
splash.append(vbat_text_area)
# external neopixels
num_pixels = 38
pixels = neopixel.NeoPixel(board.EXTERNAL_NEOPIXELS, num_pixels)

rear_head_pixels = PixelSubset(pixels, 0, 36)
left_eye_pixel=PixelSubset(pixels, 36, 37)
right_eye_pixel=PixelSubset(pixels, 37, 38)
pixels.brightness = 0.3

#Rear Neopixel array
pixel_wing_horizontal = helper.PixelMap.horizontal_lines(
    rear_head_pixels, 18, 2, helper.horizontal_strip_gridmap(18, alternating=True)
)
pixel_wing_vertical = helper.PixelMap.vertical_lines(
    rear_head_pixels, 18, 2, helper.horizontal_strip_gridmap(18, alternating=True)
)

rear_comet_h = Comet(
    pixel_wing_horizontal, speed=0.1, color=GREEN, tail_length=3, bounce=True
)
rear_comet_v = Comet(pixel_wing_vertical, speed=0.1, color=BLUE, tail_length=5, bounce=True)


rear_rainbow = Rainbow(rear_head_pixels, speed=0.1, period=2)
rear_rainbow_chase = RainbowChase(rear_head_pixels, speed=0.1, size=5, spacing=3)
rear_rainbow_comet = RainbowComet(rear_head_pixels, speed=0.1, tail_length=7, bounce=True)
rear_rainbow_sparkle = RainbowSparkle(rear_head_pixels, speed=0.1, num_sparkles=15)
rear_sparkle_pulse = SparklePulse(rear_head_pixels, speed=0.02, color=AMBER, period=5)

rear_animations = AnimationSequence(
    rear_rainbow,
    rear_rainbow_chase,
    rear_rainbow_comet,
    rear_rainbow_sparkle,
    rear_sparkle_pulse,
    rear_comet_v,
    advance_interval=5,
    auto_clear=True,
)



# Animate Eyes
right_eye_rainbow = Rainbow(right_eye_pixel, speed=0.05, period=6)
left_eye_blink = Blink(left_eye_pixel, speed=3, color=TEAL)
left_eye_pulse = Pulse(left_eye_pixel, speed=0.1, color=AMBER, period=3)


left_eye_animations = AnimationSequence(
    left_eye_blink,
    left_eye_pulse,
    advance_interval=5,
    auto_clear=True,
)

# onboard LIS3DH
i2c = board.I2C()
int1 = DigitalInOut(board.ACCELEROMETER_INTERRUPT)
lis3dh = adafruit_lis3dh.LIS3DH_I2C(i2c, int1=int1)
lis3dh.range = adafruit_lis3dh.RANGE_2_G
lis3dh.set_tap(2, 60)
tap_counter = 0

time_played = 0
p = 0

while True:
    # left eye animation
    left_eye_animations.animate()
    # right eye animation
    right_eye_rainbow.animate()
    
    # Rear head animation
    rear_animations.animate()


   
    battery_voltage = get_voltage(vbat_voltage)
    readout = ("{:.2f}".format(battery_voltage))
    splash.pop()
    vbat_text_area = label.Label(terminalio.FONT, text=readout, color=0xFFFFFF, x=35, y=18)
    splash.append(vbat_text_area)


    # # Play random BD-3 sounds after a random amount of time
    now = time.monotonic()
    time_since_played = (now) - time_played
    # Play Sounds when tapped
    if lis3dh.tapped and tap_counter < 6:
        filename = mp3files[1]
        decoder.file = open(filename, "rb")
        time_played = time.monotonic()
        audio.play(mixer)
        tap_counter += 1
        mixer.voice[0].play(decoder, loop=False)
    elif lis3dh.tapped:
        filename = mp3files[2]
        decoder.file = open(filename, "rb")
        time_played = time.monotonic()
        audio.play(mixer)
        mixer.voice[0].play(decoder, loop=False)
        tap_counter = 0
    else:
        if time_since_played > p:
            filename = mp3files[0]
            decoder.file = open(filename, "rb")
            time_played = time.monotonic()
            p = random.randint(30, 180) 
            audio.play(mixer)
            mixer.voice[0].play(decoder, loop=False)

    # # # This allows you to do other things while the audio plays!
    while mixer.playing:
        pass

    time.sleep(2)
