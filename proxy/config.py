import ConfigParser
import os
from UserDict import IterableUserDict

class CONF(IterableUserDict):
    def __init__(self, ini):
        IterableUserDict.__init__(self)
        abspath = os.path.abspath(ini)
        self['ini_path'] = abspath
        self.config = ConfigParser.ConfigParser()
        self.config.read(abspath)
        default = self.config.items("Default")
        for item in default:
            self[item[0]] = item[1]
