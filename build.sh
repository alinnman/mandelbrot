#!/bin/bash
# Cython build script for the mandelbrot code module

cython3 -a mandeliter.pyx
gcc -shared -pthread -fPIC -fwrapv -O2 -Wall -fno-strict-aliasing -I/usr/include/python3.10 -o mandeliter.so mandeliter.c
