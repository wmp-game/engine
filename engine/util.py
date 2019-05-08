__all__ = ['d', 'Logger']


def d(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return ((x2 - x1)**2 + (y2 - y1)**2)**.5


class Logger:
    def __init__(self):
        self.log = ''
        self.has_log = False

    def feed(self, log):
        if (not self.has_log):
            self.log += log
            self.has_log = True
        else:
            self.log += '\n' + log

    def dump(self, log_file_name):
        with open(log_file_name, "w") as log_file:
            print(self.log, file=log_file)
