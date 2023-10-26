import clr
import os
import sys
import serial
import enum
import array

clr.AddReference("System")

# Import the necessary types from the System namespace

# Import the necessary types from the System.IO.Ports namespace





# Get the current directory
current_directory = os.getcwd()

# Get the parent directory
parent_directory = os.path.dirname(current_directory)

# Construct the path to the file or directory in the parent directory
relative_path = os.path.join(parent_directory, "file_or_directory_name")
clr.AddReference(parent_directory + '/lib/flatscan.dll')

from U920 import Flatscan_Protocol

#parity_value = Parity.None  # Replace with the desired parity value
#stop_bits_value = StopBits.ONE  # Replace with the desired stop bits value
from System import Enum
from System.IO.Ports import SerialPort, Parity, StopBits
parity_value = 0  # Assuming 0 represents Parity.None in your case
parity_enum = Enum.ToObject(Parity, parity_value)

obj = Flatscan_Protocol("COM6",921600, parity_enum,  8, StopBits.One)
obj.Open()
while True:
    obj.m_serialPort_DataCheck()
    byte_array = array.array('B',obj.ReceiveBuffer)
    bytearray_value = bytearray(byte_array)
    print(byte_array)




