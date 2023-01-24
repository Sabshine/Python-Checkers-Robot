# Python-Checkers-Robot
A robot arm using the minimax algorithm for the checkers AI.

## Hardware
You need the following devices for this project: 
- Arduino nano
- Raspberry Pi 4b
- uArm Swift Pro 

You need the hardware components:
- 128x64 OLED (attach to arduino)
- Rotary Encoder (attach to arduino)
- 2 LEDS
- Speaker
- 2 6x6x6 push button (6x6x5 can also be used)

## Dependencies
Install the following dependencies:
```Python
$ pip install pygame
$ pip install opencv-python==4.6.0.66
$ sudo apt-get install libsdl2-image-2.0.0
$ pip install pyuarm
$ sudo apt-get install espeak
```
Clone the following repo: https://github.com/uArm-Developer/uArm-Python-SDK/tree/2.0
```Python
$ python setup.py install
```

## Devices