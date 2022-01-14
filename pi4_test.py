import uart_comms as uart
import time

max_attempts = 10

uart = uart.UART("COM5")
while True:
    command = input("What would you like to request from the Zero 2?\n\n 1 - FFT\n 2 - Tone\n")
    try:
        command = int(command)
    except:
        print("Invalid Input! Please enter either 1 or 2.")
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
            print("Invalid Input! Please enter either 1 or 2.")
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
    else:
        print("Invalid Input! Please enter either 1 or 2.")
        continue
