import wave, struct, os, math, contextlib, warnings
from itertools import chain
import matplotlib.pyplot as plt
from math import log, atan2, sqrt, pi

MAC_OSTYPE = 0
WIN_OSTYPE = 1
OSTYPE = None
from .ostype import OSTYPE
if OSTYPE != MAC_OSTYPE and OSTYPE != WIN_OSTYPE:
    print 'Operating system not known, is ostype.py present?'

DEFAULT_RATE = 44100

from .beat import Beat
from .track import Track
from .location import Location
from .astf import *
from .sound import *
from .mixer import Mixer
