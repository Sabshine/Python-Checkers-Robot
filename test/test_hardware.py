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
    if button_move.when_pressed:
      print("move")

    if button_reset.when_pressed:
      print("reset")

main()