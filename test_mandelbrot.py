import pytest
import mandelbrot
import shutil 
import os

def test_generation (): 
    # Delete all pictures from pictures area
    shutil.rmtree ("pictures")
    # Execute main test
    mandelbrot.main (["-cd", "picdata/picdata.py", "-dp", "1000", "-dpi", "400", "-cs", "0"])
    # Check existence of pictures
    _, _, files = next(os.walk("pictures"))
    file_count = len(files)
    assert (file_count == 8) 
    

    
    
