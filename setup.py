#!/usr/bin/env python

from distutils.core import setup

packages = []
for item in open('requirements3.txt', 'r').readlines():
    packages.append(item.strip())


setup(name='RainbowQR',
      version='1.0',
      description='A package to manipulate QR codes in Python to contain extra layers.',
      author='ytisf',
      url='https://www.github.com/ytisf/RainbowQR/',
      packages= ['rainbowqr'],
      install_requires=packages,
     )