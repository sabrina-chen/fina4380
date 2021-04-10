import pandas as pd
import numpy as np

class Performance:
    def __init__(self, NAV):
        self.nav = np.array(NAV).reshape(-1)
    
    def analyze(self, rf):
        self.cr = self.nav[-1] / self.nav[0] - 1
        self.ar = (self.nav[-1] / self.nav[0]) ^ (250/len(self.nav)) - 1
        self.ann_vol = self.nav.std() * 16
        self.asr = (self.ar - rf) / self.ann_vol
        
        