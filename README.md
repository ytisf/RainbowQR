# RainbowQR

[![RainbowQR](https://raw.githubusercontent.com/ytisf/RainbowQR/main/QRSample.png)](https://raw.githubusercontent.com/ytisf/RainbowQR/main/QRSample.png)

## Abstract
QR codes are such versatile tool in relaying information. This project is intended to examine some 'unorthodox' notions of evaluating various types of usage. The first attempt created here is combining a data set of THREE distinct QR codes into one QR code based on the significance of a color bit. 
In this example, a data set is split into THREE distinct chunks. These chunks are then encoded into a QR code seperately, and then merged on the color bits. For example, chunk 0 will be correlating to the red bit, chunk 1 to the green bit and chunk 2 to the blue bit. The combination should enable transmitting 3x the amount of information over the same image. 


In a one liner - it combines three QR codes into one by correlating the color bits.


## Installation
```bash
git clone https://www.github.com/ytisf/RainbowQR
cd RainbowQR
pip3 install -r requirements3.txt
```
## Usage
Encoding:
```python
#!/usr/bin/env python3

import base64

from rainbowqr import RainbowQR

data = b"This is a test of the QR code decoder.\n"
data = base64.b64encode(data)

mQR = RainbowQR(qr_version=4)
qred_files = mQR.Encode(data)

```
Decoding:
```python
#!/usr/bin/env python3

from rainbowqr import RainbowQR

for file in qred_files:
    data = mQR.Decode(file)
    print(data)
```