# From the python filestructure guide
# link: https://docs.python-guide.org/writing/structure/#test-suite
import os
import sys

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirame(__file__), '..')))

# import the library
import ddns

# in test files add:
# from .context import ddns
