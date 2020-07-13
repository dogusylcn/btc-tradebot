class Ws():
    websocket=__import__('websocket')
    def __init__(self):
        super(Ws, self).__init__()
        self.connect(
            "wss://ws.blockchain.info/inv","""{"op":"unconfirmed_sub"}""")

    def __call__(self):
        return self.listen()
        
    def connect(self,uri,msg):
        self.connection=self.websocket.create_connection(uri)
        self.connection.send(msg)
        
    def listen(self):
        return self.connection.recv()

##gate=ws()
##gate.connect("wss://ws.blockchain.info/inv","""{"op":"unconfirmed_sub"}""")
##while 1:
##    gate.listen()
