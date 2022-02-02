# Loops through rx_check so that any UART messages are picked up


import uart_comms as uart

uart = uart.UART()
uart.zero_on_tx()
while True:
    uart.rx_check()
