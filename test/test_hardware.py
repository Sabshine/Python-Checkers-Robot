import gpiozero

# HARDWARE
button_move = gpiozero.Button(17)
button_reset = gpiozero.Button(22)

led_player = gpiozero.LED(23)
led_computer = gpiozero.LED(24)

def main():
  while True:
    if not button_move.is_pressed:
      print("move")

    # if button_reset.is_pressed:
    #   print("reset")

main()