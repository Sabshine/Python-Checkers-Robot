# Python-Checkers-AI

## General information

This branch contains the code for the Arduino and its hardware. The hardware that is connected to the Arduino are as followed:
- 1.3" OLED display - SH1106 (I2C, 128*64 pixels, White), this specific screen uses the following initialization (this is different for your OLED):

```bash
U8G2_SH1106_128X64_NONAME_1_HW_I2C display(U8G2_R0, /* reset=*/ U8X8_PIN_NONE);
```
- Rotary encoder - EC11 (20mm)

There are two code files, [Screen - No Playing Page](https://github.com/Sabshine/Python-Checkers-Robot/tree/arduino/Screen%20-%20No%20Playing%20Page) is a version that has no status screen after starting the game. There is the possibility to add your own screen.

The other options [Screen - Playing Page](https://github.com/Sabshine/Python-Checkers-Robot/tree/arduino/Screen%20-%20Playing%20Page) has a screen after starting the game, that shows how many pieces and kings the player and computer have. It also states the difficulty of the game, which was selected in the difficulty selection screen.

If you want to replicate the complete project, you have to download the 3D-model for the complete case. This files can be found in the folder:
[Checkers Computer - Case](https://github.com/Sabshine/Python-Checkers-Robot/tree/3d-models/Checkers%20Computer%20-%20Case).


## Libraries

The libraries needed for the Arduino code to work are as followed:
- [Arduino Multi Button - Poelstra](https://github.com/poelstra/arduino-multi-button), used for easy button usage
- [U8g2 - Olikraus](https://github.com/olikraus/u8g2), used for controlling the OLED and printing text on the OLED

To install these libraries, click `Sketch` > `Include Library` > `Manage Libraries...`. Here you have to search for the name of the library and press `Install`.