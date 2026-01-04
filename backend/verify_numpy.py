
import sys
try:
    import numpy as np
    print("Numpy is installed. Version:", np.__version__)
except ImportError as e:
    print("Numpy is NOT installed.", e)
    sys.exit(1)
