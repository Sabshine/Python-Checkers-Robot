# Python-Checkers-Robot
A robot arm using the minimax algorithm for the checkers AI.

Click on the image below to watch a preview of this project
[![Watch the video](https://img.youtube.com/vi/LuqGzSuD3s0/maxresdefault.jpg)](https://youtu.be/LuqGzSuD3s0)

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

## 3d models
All the 3d models can be found in the [3d-models](https://github.com/Sabshine/Python-Checkers-Robot/tree/3d-models) branch

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