import gpiozero

# HARDWARE
button_move = gpiozero.Button(17)
button_reset = gpiozero.Button(27)

led_player = gpiozero.LED(23)
led_computer = gpiozero.LED(24)

def main():
  while True:
    if button_move.is_pressed:
      led_player.on()
      print("move")

    if button_reset.is_pressed:
      led_computer.on()
      print("reset")

main()