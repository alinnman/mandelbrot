# mandelbrot

For installation instructions see <a href="INSTALL.md">INSTALL.md</a>
 
This project is just an exercise in fractal geometry using the well-known Mandelbrot fractal (see https://en.m.wikipedia.org/wiki/Mandelbrot_set) in combination with a refresh of my Python programming skills. 

To plot the data I use the excellent cplot Python package by Nico Schlömer (https://github.com/nschloe/cplot.git). This package is also available in PyPi. 
I have made some very minor changes to this package and made a fork. You need my fork (https://github.com/alinnman/cplot2.git) to visualize the data quickly since there are some optimizations (using the original cplot will take a very long time). 

<hr/>

This command will produce a picture of the (entire) fractal

    python mandelbrot.py -cd picdata.py -dp 1000 -dpi 400 -cs 4 -sel 0

This will result in a picture like this:     
<img alt="alt_text" width="1000px" src="demo_pictures/mandelbrot.png" />

<hr/>

This command will produce a beautiful rendering of a spiral structure

    python mandelbrot.py -cd picdata.spiral.py -dp 1000 -dpi 400 -cs 4

This will result in a picture like this:     
<img alt="alt_text" width="1000px" src="demo_pictures/mandelbrot_spiral.png" />

<hr/>

This command will produce a structure with irregular branches

    python mandelbrot.py -cd picdata.branches.py -dp 1000 -dpi 400 -cs 4

This will result in a picture like this:     
<img alt="alt_text" width="1000px" src="demo_pictures/mandelbrot_branches.png" />

<hr/>

This command will produce a structure with a tree structure and a "minibrot" blog

    python mandelbrot.py -cd picdata.py -dp 1000 -dpi 400 -cs 4 -sel 5

This will result in a picture like this:     
<img alt="alt_text" width="1000px" src="demo_pictures/mandelbrot_tree.png" />

<hr/>

This command will produce a structure with a "seahorse" pattern

    python mandelbrot.py -cd picdata.py -dp 1000 -dpi 600 -cs 4 -sel 6

This will result in a picture like this:     
<img alt="alt_text" width="1000px" src="demo_pictures/mandelbrot_seahorse.png" />

Note the little black pattern in the middle which is a "minibrot" and technically part of the Mandelbrot Set. If the Mandelbrot Local Connectivity conjecture (<a href="https://mathoverflow.net/questions/95701/the-deep-significance-of-the-question-of-the-mandelbrot-sets-local-connectednes">MLC</a>) holds then it is connected to the main area through an infinitely thin, extremely long, and complex "black communication line" hidden in the web of "seahorse" patterns. Hard to believe when looking at it. 


