#!/usr/bin/env python3

import base64

from rainbowqr import RainbowQR


data = b"This is a test of the QR code decoder.\n"
data = base64.b64encode(data)


mQR = RainbowQR(qr_version=4)
qred_files = mQR.Encode(data)
for file in qred_files:
    mQR.Decode(file)

