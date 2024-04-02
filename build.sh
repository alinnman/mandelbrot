#!/bin/bash

# Cython build script for the mandelbrot code module

cython -a mandeliter.pyx
gcc -shared -pthread -fPIC -fwrapv -O2 -Wall -fno-strict-aliasing -I/home/august/anaconda3/include/python3.11 -o mandeliter.so mandeliter.c
