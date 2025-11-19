
import os
import sys
sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Core.NLUtils import ConfigManager
CM = ConfigManager('~/.config/Nikoru/System.confjs')

data = CM.LoadConfig()
data['system-style'] = {'system':'Daylight','user':''}
data['settings-plugins'] = []
CM.SaveConfig(data)