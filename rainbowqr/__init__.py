#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import cv2
import sys
import json
import base64
import qrcode
import numpy as np

from PIL import Image


class RainbowQR:

    def __init__(self, alpha_bit : bool = False, verbose : bool = False, qr_version : int = 4):
        
        self.SUCCESS = 'success'
        self.ERROR = 'error'
        self.INFO = 'info'

        self.MAX_QR_DATA_SIZE       = 464
        self.COLOR_THRESHOLD        = 100
        self.VERBOSE                = verbose
        self.qr_version              = qr_version

        if alpha_bit:
            self.COLORS         = {'red': (255,0,0,0), 'green': (0,255,0,0), 'blue': (0,0,255,0), 'alpha': (0,0,0,255)}
            self.WHITE_L        = [255,255,255,255]
            self.BLACK_L        = [0,0,0,0]
            self.EMPTY_ARRAY    = [0,0,0,0]
            self.COLOR_INDEX    = {'red':0,'green':1,'blue':2, 'alpha':3}
            self.USING_ALPHA    = True
        
        else:
            self.COLORS         = {'red': (255,0,0), 'green': (0,255,0), 'blue': (0,0,255)}
            self.WHITE_L        = [255,255,255]
            self.BLACK_L        = [0,0,0]
            self.EMPTY_ARRAY    = [0,0,0]
            self.COLOR_INDEX    = {'red':0,'green':1,'blue':2}
            self.USING_ALPHA    = False

        self.WHITE_T            = tuple(self.WHITE_L)
        self.BLACK_T            = tuple(self.BLACK_L)
        self.COLOR_PLEX         = len(self.COLOR_INDEX.keys())
        self.MAX_PACKET_SIZE    = self.MAX_QR_DATA_SIZE * self.COLOR_PLEX

        if self.USING_ALPHA:
            sys.stderr.write("I currently still don't support using the transparency bit.\n")
            sys.stderr.write("You can still push a commit to fix this...\n")
            sys.exit(1)

    def _print(self, message, level='info') -> None:
        message = message.strip()
        if level == self.INFO:
            # print with blue [-] prefix:
            sys.stdout.write(f'\033[94m[-]\033[0m {message}\n')
        elif level == self.ERROR:
            # print with red [!] prefix:
            sys.stdout.write(f'\033[91m[!]\033[0m {message}\n')
        elif level == self.SUCCESS:
            # print with green [+] prefix:
            sys.stdout.write(f'\033[92m[+]\033[0m {message}\n')
        else:
            raise ValueError('level must be one of info, error, success')

    def _split_to_chunks_by_packet_count(self, data: bytes, chunks:int) -> list:
        chnk_len = len(data) // chunks
        if len(data) % chunks != 0:
            chnk_len += 1
        return [data[i:i+chnk_len] for i in range(0, len(data), chnk_len)]
    
    def _split_to_chunks_by_max_length(self, data: bytes, max_length: int) -> list:
        return [data[x:x+max_length] for x in range(0,len(data),max_length)]

    def _chunk_to_qr(self, data: bytes, color: str) -> list:
        if color not in self.COLORS.keys():
            raise ValueError('color must be one of red, green, blue')

        qr = qrcode.QRCode(
            version=self.qr_version,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=4,
            border=2,
        )
        qr.add_data(data)
        qr.make(fit=True)
        qr.make_image()
        return qr.make_image()

    def _read_image_into_rgb_array(self, image_path: str) -> list:
        '''
        Reads an image into an RGB array
        args:
            image_path: path to image
        returns:
            list of RGB values
        '''
        if self.VERBOSE:
            self._print(f'Reading {image_path}...\n')
        img = cv2.imread(image_path)
        return img.reshape((img.shape[0] * img.shape[1], 3))

    def Encode(self, data) -> list:

        # Split data into packets
        packets = self._split_to_chunks_by_max_length(data, self.MAX_PACKET_SIZE)
        if self.VERBOSE:
            self._print(f"Total data of {len(data)} split into {len(packets)} packets.")

        # Split each packet into THREE chunks
        '''
        qrs = {
            packet_number = { 'red': chunk, 'green': chunk, 'blue': chunk }
        }
        '''
        qrs = {}
        for i, packet in enumerate(packets):
            r,g,b = self._split_to_chunks_by_packet_count(packet, 3)
            qrs[i] = {'red': r, 'green': g, 'blue': b}
            if self.VERBOSE:
                self._print(f"Packet of {len(packet)} split into {len(qrs)} chunks.")
        if self.VERBOSE:
            self._print(f"Each packet split into {len(packets)} chunks with a total of {len(qrs)*3} chunks.")

        # Encode each packet into a QR code
        for packet_number, body in qrs.items():
            for color, data in body.items():
                fname = f'P{packet_number}_{color}.png' 
                qr = self._chunk_to_qr(data, color)
                qr.save(fname)

        # Merge all QR codes into one image
        if self.VERBOSE:
            self._print('Merging QR codes...\n')
        for packet_number, body in qrs.items():
            for color, data in body.items():
                fname = f'P{packet_number}_{color}.png' 
                img = cv2.imread(fname)
                qrs[packet_number][color] = {}
                qrs[packet_number][color]['img'] = img
                qrs[packet_number][color]['fname'] = fname
                qrs[packet_number][color]['h'] = img.shape[0]
                qrs[packet_number][color]['w'] = img.shape[1]
                qrs[packet_number][color]['pixels'] = self._read_image_into_rgb_array(fname)

        self._print(f"Each packet encoded into a QR code.", self.SUCCESS)

        packets_paths = []
       
        # Create new image

        for packet_number in range(len(qrs)):

            final_packet_pixels = []
            for i in range(qrs[0]['red']['h']*qrs[0]['red']['w']): final_packet_pixels.append([0,0,0])
            #np.zeros((qrs[0]['red']['h'] * len(qrs), qrs[0]['red']['w'], 3), dtype=np.uint8)
            for idx, item in enumerate(final_packet_pixels):
                for color in self.COLORS.keys():
                    if qrs[packet_number][color]['pixels'][idx][0] > self.COLOR_THRESHOLD:
                        turn_on = True
                    else:
                        turn_on = False
                    
                    if turn_on:
                        final_packet_pixels[idx][self.COLOR_INDEX[color]] = 255
                    else:
                        final_packet_pixels[idx][self.COLOR_INDEX[color]] = 0

            # Save final packet to file
            final_packet_pixels = np.array(final_packet_pixels, dtype=np.uint8)
            final_packet_pixels = final_packet_pixels.reshape((body['red']['h'], body['red']['w'], self.COLOR_PLEX))
            cv2.imwrite(f'P{packet_number}.png', final_packet_pixels)
            packets_paths.append(f'P{packet_number}.png')
        
        self._print(f"Each QR code combined into a single image.", self.SUCCESS)

        for color in self.COLORS.keys():
            for packet_number, body in qrs.items():
                os.remove(body[color]['fname'])

        return packets_paths

    def Decode(self, image_path: str) -> str:
        pixels      = self._read_image_into_rgb_array(image_path)
        img         = cv2.imread(image_path)
        h           = img.shape[0]
        w           = img.shape[1]

        qr_pxls = {}

        for color in self.COLORS.keys():
            qr_pxls[color] = []

        for idx, pixel in enumerate(pixels):
            for i in range(0,3):
                if i == 0: # RED
                    if pixel[i] > self.COLOR_THRESHOLD:
                        qr_pxls['red'].append(self.WHITE_L,)
                    else:
                        qr_pxls['red'].append(self.BLACK_L,)
                elif i == 1: # GREEN
                    if pixel[i] > self.COLOR_THRESHOLD:
                        qr_pxls['green'].append(self.WHITE_L,)
                    else:
                        qr_pxls['green'].append(self.BLACK_L,)
                elif i == 2: # BLUE
                    if pixel[i] > self.COLOR_THRESHOLD:
                        qr_pxls['blue'].append(self.WHITE_L,)
                    else:
                        qr_pxls['blue'].append(self.BLACK_L,)

        # Save each QR into image file
        for color in self.COLORS.keys():
            # Initialize empty array
            this_color = np.array(qr_pxls[color], dtype=np.uint8)
            this_color = this_color.reshape((h, w, self.COLOR_PLEX))
            cv2.imwrite(f'{color}.png', this_color)
        
        output_data = ""
        # Decode QR Data
        for color in self.COLORS.keys():
            # Decode QR data in file:
            ih = cv2.imread(f'{color}.png')
            detector = cv2.QRCodeDetector()
            data, bbox, rect = detector.detectAndDecode(ih)
            if data is not None:
                output_data += data
            if self.VERBOSE:
                print(f"Decoded {color} QR code: {data}")

        # Clean up the files
        for color in self.COLORS.keys():
            os.remove(f'{color}.png')

        if self.VERBOSE:
            self._print(f"Decoded QR code: {output_data}", self.SUCCESS)
        return output_data




