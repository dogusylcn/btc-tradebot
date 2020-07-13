class RatesCollector():
    req=__import__('requests')
    sql=__import__("saver").Sql
    dejson=__import__("jsonize").Json
    time = __import__('timer').Time
    
    def __init__(self):
        super(RatesCollector, self).__init__()
        self.saver=self.sql(rate=True)
        self.timer=self.time()
        self.json=self.dejson()

    def __call__(self):
        while True:
            try:
                self.save_curr()
            except:
                print("collect_rates.py hata verdi!")
                print("yeniden deneniyor!")

    def get_rate(self):
        return self.json(self.req.get(
            "https://api.coinbase.com/v2/prices/spot?currency=USD").text)["data"]["amount"]
        
    def save_curr(self):
        self.saver([self.get_rate(),self.timer()])


if __name__ == "__main__":
    c=RatesCollector()
    c()
