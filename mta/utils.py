__author__ = 'sam.royston'
import os
import sys
import pandas as pd
import time


def default_data_dir():
    return os.path.dirname(os.path.abspath(__file__)) + "/mta_data"


def print_all(x):
    pd.set_option('display.max_rows', len(x))
    print(x.to_string(index=False))
    pd.reset_option('display.max_rows')


def debug(f, msg=None):
    def wrapper(*args, **kwargs):
        self = args[0]
        if self.verbose is True:
            start_time = time.time()
            if msg is not None:
                sys.stdout.write(msg + ", ")
            sys.stdout.write("running " + f.__name__)
            out = f(*args, **kwargs)
            sys.stdout.write("   " + str(time.time() - start_time) + "\n")
            sys.stdout.flush()
            return out
        else:
            return f(*args, **kwargs)
    return wrapper
