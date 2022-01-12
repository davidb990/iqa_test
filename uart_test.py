import uart_comms

uart = uart_comms.UART()
while True:
    uart.rx_check()
