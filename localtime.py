import time

def get_unixtime():
    return time.time()

def now():
    return time.strftime('%d.%m.%Y %X', time.localtime(get_unixtime()))

def time_formatted(unixtime = get_unixtime()):
    return time.strftime('%d.%m.%Y %X', time.localtime(unixtime))

if __name__ == "__main__":
    pass