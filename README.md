# Python-Checkers-Robot
A robot arm using the minimax algorithm for the checkers AI.
This branch does **not** contains espeak or an Arduino connections. This project only needs a compputer.

Click on the gif below to watch a demo of this project
[![Watch the video](https://github.com/Sabshine/Python-Checkers-Robot/blob/master/img/Demo_damrobot.gif)](https://youtu.be/LuqGzSuD3s0)

## Hardware
You need the following devices for this project: 
- uArm Swift Pro 

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