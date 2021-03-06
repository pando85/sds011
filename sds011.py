#!/usr/bin/env python3
""" sds011.py. basic python script to read values from nova pm sensor sds011.

Usage:
    sds011.py [-h | --help] [-d | --debug]

Options:
    -h --help       Show this screen.
    -d --debug      Show debug information.
"""

import datetime
import docopt
import logging
import serial
import struct
import sys

logger = logging.getLogger(__name__)
logger_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(logger_handler)
logger.setLevel('INFO')


SLEEP_BYTES = [b'\xaa', #head
    b'\xb4', #command 1
    b'\x06', #data byte 1
    b'\x01', #data byte 2 (set mode)
    b'\x00', #data byte 3 (sleep)
    b'\x00', #data byte 4
    b'\x00', #data byte 5
    b'\x00', #data byte 6
    b'\x00', #data byte 7
    b'\x00', #data byte 8
    b'\x00', #data byte 9
    b'\x00', #data byte 10
    b'\x00', #data byte 11
    b'\x00', #data byte 12
    b'\x00', #data byte 13
    b'\xff', #data byte 14 (device id byte 1)
    b'\xff', #data byte 15 (device id byte 2)
    b'\x05', #checksum
    b'\xab'] #tail

WAKE_BYTES = [b'\xaa', #head
    b'\xb4', #command 1
    b'\x06', #data byte 1
    b'\x01', #data byte 2 (set mode)
    b'\x01', #data byte 3 (sleep)
    b'\x00', #data byte 4
    b'\x00', #data byte 5
    b'\x00', #data byte 6
    b'\x00', #data byte 7
    b'\x00', #data byte 8
    b'\x00', #data byte 9
    b'\x00', #data byte 10
    b'\x00', #data byte 11
    b'\x00', #data byte 12
    b'\x00', #data byte 13
    b'\xff', #data byte 14 (device id byte 1)
    b'\xff', #data byte 15 (device id byte 2)
    b'\x05', #checksum
    b'\xab'] #tail


def open_serial(path):
    logger.debug('Open serial port')
    ser = serial.Serial()
    #ser.port = sys.argv[1]
    ser.port = path
    ser.baudrate = 9600

    ser.open()
    ser.flushInput()
    logger.debug('Connected to device')
    return ser


def wake_up(ser):
    logger.debug('Waking up')
    for b in WAKE_BYTES:
        ser.write(b)
    logger.debug('Waked up')


def sleep(ser):
    for b in SLEEP_BYTES:
        ser.write(b)


def sensor_read(ser):
    logger.debug('Reading values')
    byte = 0
    while byte != "\xaa":
        logger.debug('Continue reading')
        byte = ser.read(size=1)
        d = byte + ser.read(size=10)
        if d[1].to_bytes(1, byteorder='big') == b'\xc0':
            r = struct.unpack('<HHxxBBB', d[2:])
            pm25 = r[0]/10.0
            pm10 = r[1]/10.0
            checksum = sum(d[2:8])%256

            if not (checksum == r[2] and r[3].to_bytes(1, byteorder='big') == b'\xab'):
                logger.error('Checksum does not match')
                return
            return {'pm25': pm25, 'pm10': pm10, 'timestamp': str(datetime.datetime.now())}


def main():
    arguments = docopt.docopt(__doc__)
    if arguments['--debug']:
        logger.setLevel('DEBUG')

    ser = open_serial("/dev/ttyUSB0")
    wake_up(ser)

    while True:
        data = sensor_read(ser)
        logger.info(data)

if __name__ == '__main__':
    main()
