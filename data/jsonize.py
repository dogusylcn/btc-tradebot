class Json():
    _json = __import__('json')
    def __init__(self):
        super(Json, self).__init__()
        self.jsonize=self._json.loads
        
    def __call__(self,x):
        return self.jsonize(x)
