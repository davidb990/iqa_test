from smbus2 import SMBus
import time


class EepFlash:
    def __init__(self, addr: int = 0x1a, bus: int = 1, offset: int = 0x00, file: str = "Pi-CodecZero.eep",
                 page_size: int = 32):
        self.addr = addr
        self.bus = bus
        self.offset = offset
        self.file = file
        self.page_size = page_size

    def eep_import(self) -> bytes:
        # read the .eep as bytes
        with open(self.file, 'rb') as file:
            eep_bin = file.read()
        return eep_bin

    def bytes_to_page(self, all_bytes: bytes, page_size: int = None) -> list:
        # convert the bytes to pages of bytes

        # checks to see if local page_size arg given
        if isinstance(page_size, int):
            self.page_size = page_size
        page_list = []
        for n in range(len(all_bytes)):
            # appends a moving bracket of bytes to the page_list
            page_list.append(all_bytes[self.page_size * n:self.page_size * (n + 1)])
        return page_list

    def pages(self) -> list:
        # takes the imported bytes, runs the bytes to pages func on them
        all_bytes = self.eep_import()
        return self.bytes_to_page(all_bytes)

    def eep_write(self):
        page_list = self.pages()
        eeprom_byte_addr = self.offset
        # open the i2c bus
        with SMBus(self.bus) as bus:
            for page in page_list:
                t_start = time.perf_counter()
                # some of the trailing pages are empty (at least with the EEPROM I am using to test), this if statement
                # omits them to speed up the write
                if page != b'':
                    # writes to EEPROM at a specific address within the eeprom, which is incremented at the end of
                    # the loop
                    bus.write_i2c_block_data(self.addr, eeprom_byte_addr, page)
                    # write time for a page on a CAT24C32 EEPROM is 5ms, hence the next while loop ensure that the code
                    # takes more that 5ms to run, thus the EEPROM has enough time to write
                    while time.perf_counter() - t_start < 0.005:
                        pass
                # increment the EEPROM address where the page is written by a page length
                eeprom_byte_addr += len(page)
