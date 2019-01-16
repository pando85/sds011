import serial
import struct


SLEEP_BYTES = ['\xaa', #head
    '\xb4', #command 1
    '\x06', #data byte 1
    '\x01', #data byte 2 (set mode)
    '\x00', #data byte 3 (sleep)
    '\x00', #data byte 4
    '\x00', #data byte 5
    '\x00', #data byte 6
    '\x00', #data byte 7
    '\x00', #data byte 8
    '\x00', #data byte 9
    '\x00', #data byte 10
    '\x00', #data byte 11
    '\x00', #data byte 12
    '\x00', #data byte 13
    '\xff', #data byte 14 (device id byte 1)
    '\xff', #data byte 15 (device id byte 2)
    '\x05', #checksum
    '\xab'] #tail

WAKE_BYTES = ['\xaa', #head
    '\xb4', #command 1
    '\x06', #data byte 1
    '\x01', #data byte 2 (set mode)
    '\x01', #data byte 3 (sleep)
    '\x00', #data byte 4
    '\x00', #data byte 5
    '\x00', #data byte 6
    '\x00', #data byte 7
    '\x00', #data byte 8
    '\x00', #data byte 9
    '\x00', #data byte 10
    '\x00', #data byte 11
    '\x00', #data byte 12
    '\x00', #data byte 13
    '\xff', #data byte 14 (device id byte 1)
    '\xff', #data byte 15 (device id byte 2)
    '\x05', #checksum
    '\xab'] #tail


def open_serial(path):
    print('Open serial port')
    ser = serial.Serial()
    #ser.port = sys.argv[1]
    ser.port = path
    ser.baudrate = 9600

    ser.open()
    ser.flushInput()
    print('Connected to device')
    return ser


def wake_up(ser):
    print('Waking up')
    for b in WAKE_BYTES:
        ser.write(b.encode())
    print('Waked up')


def sleep(ser):
    for b in SLEEP_BYTES:
        ser.write(b.encode())


def sensor_read(ser):
    print('Reading values')
    byte = 0
    while byte != "\xaa":
        print('Continue reading')
        byte = ser.read(size=1)
        d = byte + ser.read(size=10)
        if d[1].to_bytes(1, byteorder='big') == b'\xc0':
            r = struct.unpack('<HHxxBBB', d[2:])
            pm25 = r[0]/10.0
            pm10 = r[1]/10.0
            checksum = sum(d[2:8])%256

            if not (checksum == r[2] and r[3].to_bytes(1, byteorder='big') == b'\xab'):
                print('Check sum not match')
                return
            return {'pm25': pm25, 'pm10': pm10}


def main():
    ser = open_serial("/dev/ttyUSB0")
    wake_up(ser)

    while True:
        data = sensor_read(ser)
        print(data)

if __name__ == '__main__':
    main()
