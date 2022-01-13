import uart_comms as uart
import time

while True:
    try:
        uart = uart.UART()
        time.sleep(0.5)
        while True:
            uart.rx_check()
            time.sleep(0.1)
    except:
        pass
