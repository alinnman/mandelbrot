# mandelbrot
 
This project is just an exercise in fractal geometry using the well-known Mandelbrot fractal (see https://en.m.wikipedia.org/wiki/Mandelbrot_set) in combination with a refresh of my Python programming skills. 

In order to plot the data I use the excellent cplot Python package by Nico Schlömer (https://github.com/nschloe/cplot.git). This package is also available in PyPi. 
I have made some very minor changes to this package and made a fork. You need my fork (https://github.com/alinnman/cplot2.git) in order to visualize the data quickly since there are some optimizations (using the original cplot will take a very long time). 

This command will produce a beautiful rendering of a spiral structure

    python mandelbrot.py -cd picdata.spiral.py -dp 1000 -dpi 400 -cs 4

This will result in a picture like this:     
[<img alt="alt_text" width="1000px" src="mandelbrot_illustration.png" />]
