import time
import sys
from lifxlan import LifxLAN
import os
import logging
import time, vlc
import socket
import tkinter
from PIL import Image, ImageTk
import msvcrt
import win32api

RASPBERRY_PI_IP = "192.168.1.23"
LAPTOP_IP = "192.168.1.8"

TCP_IP = LAPTOP_IP # this IP of my pc. When I want raspberry pi 2`s as a server, I replace it with its IP '169.254.54.195'
TCP_PORT = 5005
BUFFER_SIZE = 20 # Normally 1024, but I want fast response

lights = []
conn = None
gabry_tag = False

def setup():
    # instantiate LifxLAN client, num_lights may be None (unknown).
    # In fact, you don't need to provide LifxLAN with the number of bulbs at all.
    # lifx = LifxLAN() works just as well. Knowing the number of bulbs in advance
    # simply makes initial bulb discovery faster.
    global lights
    global conn
    lifx = LifxLAN(1)
    lights = lifx.get_lights()  # get devices
    lights_names = map(lambda x: x.get_label(), lights)
    print("Found %s lights: %s" % (len(lights), lights_names))

    RASPBERRY_PI_IP = "192.168.1.23"
    LAPTOP_IP = "192.168.1.8"

    TCP_IP = LAPTOP_IP  # this IP of my pc. When I want raspberry pi 2`s as a server, I replace it with its IP '169.254.54.195'
    TCP_PORT = 5005
    BUFFER_SIZE = 20  # Normally 1024, but I want fast response

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((TCP_IP, TCP_PORT))
    s.listen(1)

    conn, addr = s.accept()
    print('Connection address:', addr)
    turnLightsOff()

    # freq = 44100    # audio CD quality
    # bitsize = -16   # unsigned 16 bit
    # channels = 2    # 1 is mono, 2 is stereo
    # buffer = 2048   # number of samples (experiment to get right
    # # mixer.init(frequency=44100, size=-16, channels=2, buffer=512, devicename="LE-Gabry's Bose QC35 II")
    # mixer.init(devicename="LE-Gabry's Bose QC35 II")
    # print os.path.exists("What are you doing in my swamp.mp3")
    # mixer.music.load('What are you doing in my swamp.mp3')
    # mixer.music.play()
    # while mixer.music.get_busy() == True:
    # 		continue

    return lights


def Play(sound, fullscreen=False):
    vlc_instance = vlc.Instance()
    player = vlc_instance.media_player_new()
    media = vlc_instance.media_new(sound)
    player.set_media(media)
    player.play()
    if fullscreen:
        player.toggle_fullscreen()
    player.audio_set_volume(100)
    time.sleep(1.5)
    duration = player.get_length() / 1000
    started_time = time.time()
    while time.time() - started_time <= duration:
        print("%s / %s" % (time.time() - started_time, duration))
        state = win32api.GetAsyncKeyState(27)
        print(state)
        if state:
            # print("KB HIT!")
            break
    time.sleep(1)

def turnLightsOff():
    for d in lights:
        d.set_power(False)

def TurnGreenLightOn():
    global lights
    for d in lights:
        # print 'Turning led on to green'
        power = True
        color = [20000, 65535, 65535, 9000]
        d.set_power(power)
        # 	color is a HSBK list of values: [hue (0-65535), saturation (0-65535), brightness (0-65535), Kelvin (2500-9000)]
        d.set_color(color)
    # print("{} ({}) HSBK: {}".format(d.get_label(), d.mac_addr, d.get_color()))


def turn_red_LED():
    global lights
    for d in lights:
        # print 'Turning led on to green'
        power = False
        color = [0, 65535, 65535, 9000]
        d.set_power(power)
        # 	color is a HSBK list of values: [hue (0-65535), saturation (0-65535), brightness (0-65535), Kelvin (2500-9000)]
        d.set_color(color)
    # print("{} ({}) HSBK: {}".format(d.get_label(), d.mac_addr, d.get_color()))

def showPIL(pilImage):
    root = tkinter.Tk()
    w, h = root.winfo_screenwidth(), root.winfo_screenheight()
    root.overrideredirect(1)
    root.geometry("%dx%d+0+0" % (w, h))
    root.focus_set()
    root.bind("<Escape>", lambda e: (e.widget.withdraw(), e.widget.quit()))
    canvas = tkinter.Canvas(root,width=w,height=h)
    canvas.pack()
    canvas.configure(background='black')
    imgWidth, imgHeight = pilImage.size
    if imgWidth > w or imgHeight > h:
        ratio = min(w/imgWidth, h/imgHeight)
        imgWidth = int(imgWidth*ratio)
        imgHeight = int(imgHeight*ratio)
        pilImage = pilImage.resize((imgWidth,imgHeight), Image.ANTIALIAS)
    image = ImageTk.PhotoImage(pilImage)
    imagesprite = canvas.create_image(w/2,h/2,image=image)
    root.mainloop()

def shreck_fullscreen():
    showPIL(Image.open('shrek.png'))


def loop():
    global player
    while 1:
        msg = conn.recv(BUFFER_SIZE)
        intruder_detected = bool(int(msg))
        if intruder_detected and not gabry_tag:
            print("INTRUDER")
            TurnGreenLightOn()
            # Play("What are you doing in my swamp.mp3")
            Play("What are you doing in my swamp.mp4", True)
            Play("All Star - Smash Mouth.mp3")
            return
        # conn.send(data)  # echo











if __name__ == "__main__":
    setup()
    loop()
    conn.close()
