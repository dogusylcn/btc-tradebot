class Time():
    time = __import__('time')
    def __init__(self):
        super(Time, self).__init__()
        self.ret_type='%Y-%m-%d-%H-%M'
    def __call__(self):
        return self.time.strftime(self.ret_type, self.time.localtime(self.time.time()))         
