import uart_comms as uart
import time

max_attempts = 10

uart = uart.UART("COM5")
while True:
    command = input("What would you like to request from the Zero 2?\n\n 1 - FFT\n 2 - Tone\n 3 - Relay Select\n")
    try:
        command = int(command)
    except:
        print("Invalid Input! Please enter either 1,2 or 3.")
        continue
    if command == 1:
        uart.fft_tx_w(0.5)
        for n in range(max_attempts):
            confirmation = uart.conf_tx()
            if confirmation:
                while True:
                    try:
                        fft = uart.fft_tx_r()
                        if isinstance(fft, tuple):
                            print(fft)
                            break
                    except:
                        pass
                break
            else:
                if n == max_attempts-1:
                    print("Zero 2 failed to confirm receipt of command.")
    elif command == 2:
        duration = float(input("Tone duration:\n"))
        mono_stereo = input("Type of tone:\n\n 1 - mono\n 2 - stereo\n")
        try:
            mono_stereo = int(mono_stereo)
        except:
            print("Invalid Input! Please enter either 1,2 or 3.")
            continue
        if mono_stereo == 1:
            tone = input("Frequency:\n")
            uart.tone_tx(int(tone), duration)
        elif mono_stereo == 2:
            l_tone = input("Left frequency:\n")
            r_tone = input("Right frequency:\n")
            tone = [int(l_tone), int(r_tone)]
        else:
            print("Invalid Input! Please enter either 1 or 2.")
            continue
        uart.tone_tx(tone, duration)
        for n in range(max_attempts):
            if uart.conf_tx():
                print("Command received")
                break
            else:
                if n == max_attempts-1:
                    print("Zero 2 failed to confirm receipt of command.")
    elif command == 3:
        relay_list = ["aux_out", "rca", "phones", "xlr", "aux_in",
                      "mic", "all"]
        relay_sel = input("Please choose a relay:\n 1 - Aux Out\n 2 - RCA\n 3 - Headphones\n 4 - XLR\n 5 - Aux In\n"
                          " 6 - Mic\n 7 - All\n")
        try:
            relay_sel = int(relay_sel)
        except:
            print("Invalid Input! Please enter either 1 to 7.")
            continue
        relay_sel = relay_sel-1
        relay = relay_list[relay_sel]
        on_off = input("Enter 1 for on and 2 for off.\n")
        if on_off == 1 or on_off == 2:
            pass
        else:
            print("Invalid input, enter 1 or 2")
            continue
        try:
            uart.relay_tx(relay, on_off)
            print("Relay switched")
        except:
            print("Invalid input!")
    else:
        print("Invalid Input! Please enter either 1,2 or 3.")
        continue
