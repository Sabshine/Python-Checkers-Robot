import gpiozero

# HARDWARE
button_move = gpiozero.Button(17)
button_reset = gpiozero.Button(27)

led_player = gpiozero.LED(23)
led_computer = gpiozero.LED(24)

def main():
  led_player.blink()
  led_computer.blink()

  while True:
    if not button_move.is_pressed:
      print("move")

    if not button_reset.is_pressed:
      print("reset")

main()