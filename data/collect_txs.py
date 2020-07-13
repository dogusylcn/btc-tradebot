class TxsCollector():
    ws=__import__('webs').Ws
    sql=__import__("saver").Sql
    dejson=__import__("jsonize").Json
    time = __import__('timer').Time
    
    def __init__(self):
        super(TxsCollector, self).__init__()
        self.gate=self.ws()
        self.saver=self.sql()
        self.timer=self.time()
        self.json=self.dejson()

    def __call__(self):
        while True:
            try:
                self.save_curr()
            except:
                print("collect_txs.py hata verdi!")
                self.gate=self.ws()
                print("web socket yeniden yapılandırıldı!")
        
    def save_curr(self):
        [self.saver(
            [i["prev_out"]["addr"],i["prev_out"]["value"]/pow(10,8),self.timer()])
                for i in self.json(self.gate())["x"]["inputs"]]

if __name__ == "__main__":
    c=TxsCollector()
    c()
