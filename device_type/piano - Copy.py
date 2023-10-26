from time import sleep

import piano_device

piano = piano_device.FlatScanPiano(6)
while (True):
    sleep(1)
    piano.print_mdi()
