class FileException(Exception):
    def __init__(self, name):
        super(FileException, self).__init__()
        self.name = name
    def __str__(self):
        return "The file %s can't be found!\n" % self.name
        
class AppNotFound(Exception):
    def __init__(self, name):
        super(AppNotFound, self).__init__()
        self.name = name
    def __str__(self):
        return "The app %s can't be found!\n" % self.name
        
class ParaNotProvide(Exception):
    def __init__(self, name):
        super(ParaNotProvide, self).__init__()
        self.name = name
    def __str__(self):
        return "The class/function %s need more parameters!\n" % self.name
