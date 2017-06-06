
import sys
import os
import time

pycrosscall_path = os.path.abspath(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
sys.path.insert(0, pycrosscall_path)
import pycrosscall
pycrosscall_session = pycrosscall.session()

time.sleep(5)
