class Collector():
    req = __import__('requests')
    json = __import__('json')
    def __init__(self):
        super(Collector, self).__init__()
        self.jsonize=self.json.loads
        self._get=self.req.get
        self.main_u="https://api.blockcypher.com/v1/btc/main"
        self.block_u="https://api.blockcypher.com/v1/btc/main/blocks/"
        self.txid_u="https://api.blockcypher.com/v1/btc/main/txs/"
        self.txs=[]

    def __call__(self):
        self.refresh()
        return self.txs

    def get(self,x):
        return self.jsonize(self._get(x).text)

    def latest_block(self):
        return self.get(self.main_u)['latest_url']

    def transaction_details(self,x):
        data=self.get(x)
        return data["hash"],data["confirmed"],data["total"]

    def transactions(self):
        ret=[]
        for i in self.get(self.latest_block())["txids"]:
            ret.append(self.transaction_details(self.txid_u+i))
        return ret
        
    def refresh(self):
        self.txs=self.transactions()
