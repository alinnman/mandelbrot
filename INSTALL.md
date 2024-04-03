Requirements

* Windows 10/11 or Linux. 
* Installation of C compiler
* Python 3 environment
* Git for cloning or forking the code

You must start by cloning my repository cplot2. It is a fork of the official PyPi cplot library. 

    git clone https://github.com/alinnman/cplot2.git
    pip uninstall cplot # If you already had cplot installed
    cd <directory of the clone you just made>
    pip install . 

Then just clone or fork this repository to a suitable location. Install dependent libraries. 

    git clone https://github.com/alinnman/mandelbrot.git
	pip install -r requirements.txt

The program uses a Cython module for computation speed. 
Execute one of the attached scripts ``build.sh`` (Linux) or ``build.cmd`` (Windows) which builds the C-code and executable. 

Now you can run the program. Specifying no arguments will just generate a test suite. All generated images will be written to the ``pictures`` subdirectory. 

    python mandelbrot.py

Parameters are shown using help switch

    python mandelbrot.py -h

For examples see the <a href="README.md">README file</a>


