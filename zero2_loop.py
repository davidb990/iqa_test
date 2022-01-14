import uart_comms as uart
import time

uart = uart.UART()
while True:
    uart.rx_check()
    time.sleep(0.1)

