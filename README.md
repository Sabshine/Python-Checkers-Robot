# Python-Checkers-Robot
A robot arm using the minimax algorithm for the checkers AI.
This branch also contains espeak and Arduino connections, which the [ver-raspberry](https://github.com/Sabshine/Python-Checkers-Robot/tree/ver-raspberry) branch doesn't.
This branch is the most up-to-date.

Click on the gif below to watch a full demo of this project
[![Watch the video](https://github.com/Sabshine/Python-Checkers-Robot/blob/master/img/Demo_damrobot_1.gif)](https://youtu.be/F-rw_T0ELHk)

Click on the gif below to watch a demo regarding invalid moves
[![Watch the video](https://github.com/Sabshine/Python-Checkers-Robot/blob/master/img/Demo_damrobot_2.gif)]( https://youtu.be/5TMRmjDuwSk)

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

For more details about harware go to the following branch: [Arduino](https://github.com/Sabshine/Python-Checkers-Robot/tree/arduino)

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