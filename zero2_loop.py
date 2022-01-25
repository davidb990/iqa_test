import uart_comms as uart
import time

uart = uart.UART()
uart.zero_on_tx()
while True:
    uart.rx_check()
    time.sleep(0.1)

