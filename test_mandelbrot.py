import pytest
import mandelbrot

def test_generation (): 
    mandelbrot.main (["-cd", "picdata/picdata.py", "-dp", "1000", "-dpi", "400", "-cs", "0"])

