#!/usr/bin/env python3

# Copyright (C) 2020 Marco Lochen

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from PIL import Image
import hashlib
import sys

class datastream_in:
    def __init__(self, path):
        self.f = open(path, mode='rb')
        self.esc = False
        self.finished = False

    def get(self):
        if (self.esc == True):
            self.esc = False
            return self.f.read(1)[0]
        if (self.finished == True):
            return 0
        byte = self.f.peek(1)
        if (len(byte) == 0):
            self.finished = True
            return 0x55
        if (byte[0] == 0x55):
            self.esc = True
            return 0x55
        return self.f.read(1)[0]

    def is_finished(self):
        return self.finished

    def close(self):
        self.f.close()

class datastream_out:
    def __init__(self, path):
        self.f = open(path, mode='wb')
        self.esc = False

    def put(self, char):
        if (self.esc == True):
            if (char == 0x55):
                self.esc = False
                self.f.write((char).to_bytes(1, byteorder="big"))
                return
            else:
                return
        if (char == 0x55):
            self.esc = True
            return
        self.f.write((char).to_bytes(1, byteorder="big"))

    def close(self):
        self.f.close()

class randstream:
    def __init__(self, password):
        self.hash = hashlib.sha256(password.encode())
        self.index = 0

    def get(self):
        byte = self.hash.digest()[self.index]
        self.index = self.index + 1
        if (self.index == len(self.hash.digest())):
            self.hash = hashlib.sha256(self.hash.digest())
            self.index = 0
        return byte

def get_data():
    password = input("Password: ")
    filename = input("Save as: ")
    img = Image.open(sys.argv[1])
    if (img.mode != "RGB"):
        print("Error: Image must be in RGB mode!")
        exit()
    return (password, filename, img)

if (len(sys.argv) == 3):
    print("Encode data")
    password, filename, img_in = get_data()
    ds = datastream_in(sys.argv[2])
    rs = randstream(password)
    b = ds.get() ^ rs.get()
    bs = 6
    img_out = Image.new("RGB", img_in.size)
    for y in range(img_out.height):
        for x in range(img_out.width):
            p = list(img_in.getpixel((x, y)))
            for i in range(len(p)):
                p[i] = (p[i] & 0xFC) | ((b >> bs) & 0x03)
                bs = bs - 2
                if (bs < 0):
                    b = ds.get() ^ rs.get()
                    bs = 6
            img_out.putpixel((x,y), tuple(p))
    if (ds.is_finished() == True):
        img_out.save(filename)
    else:
        print("ERROR: Data does not fit in this image!")
    ds.close()
elif (len(sys.argv) == 2):
    print("Decode data")
    password, filename, img_in = get_data()
    ds = datastream_out(filename)
    rs = randstream(password)
    byte = 0
    sc = 0
    esc = False
    for y in range(img_in.height):
        for x in range(img_in.width):
            for p in img_in.getpixel((x, y)):
                byte = (byte << 2) | (p & 0x03)
                sc = sc + 1
                if (sc == 4):
                    plain = byte ^ rs.get()
                    ds.put(plain)
                    byte = 0
                    sc = 0
    ds.close()
else:
    print("USAGE: Encode data: imgsteg.py path/to/image path/to/data")
    print("       Decode data: imgsteg.py path/to/image")

