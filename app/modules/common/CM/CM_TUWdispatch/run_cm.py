# -*- coding: utf-8 -*-

import os
import time
import sys
import numpy as np

path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.
                                                       abspath(__file__))))
if path not in sys.path:
    sys.path.append(path)
	
import CM.CM_TUWdispatch.simpel_dispatch as simpel_dispatch
import CM.CM_TUWdispatch.save_sol_to_json as save_sol_to_json
import CM.CM_TUWdispatch.plot_sol_from_json as plot_sol_from_json


def main(data):
    
    values = simpel_dispatch.run(data)
    return values

if __name__ == "__main__":
    print('calculation started')
