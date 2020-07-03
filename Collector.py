class Browser():
    selenium = __import__('selenium.webdriver').webdriver
    def __init__(self):
        super(Browser, self).__init__()
        self.browser=self.selenium.Chrome()

    def __call__(self,x):
        self.browser.get(x)
        return self.browser

##class Json():
##    _json = __import__('json')
##    def __init__(self):
##        super(Json, self).__init__()
##        self.jsonize=self._json.loads
##        
##    def __call__(self,x):
##        return self.jsonize(x)

class Sql():
    sqlite = __import__('sqlite3')
    def __init__(self):
        super(Sql, self).__init__()
        self.connection = self.sqlite.connect('db.sqlite')
        self.create_tables()

    def __call__(self,x,rate=False):
        cursor=self.connection.cursor()
        if(not rate):
            query="""INSERT INTO txs VALUES ('{}', '{}', '{}')""".format(x[0],x[1],x[2])
        else:
            query="""INSERT INTO rates VALUES ('{}', '{}', '{}')""".format(x[0],x[1],x[2])
        cursor.execute(query)
        self.connection.commit()

    def get_by_txs(self,x):
        cursor=self.connection.cursor()
        cursor.execute("""SELECT * FROM txs WHERE hash='{}'""".format(x))
        return cursor.fetchall()
        
    def create_tables(self):
        cursor=self.connection.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS txs (hash, total, time)""")
        cursor.execute("""CREATE TABLE IF NOT EXISTS rates (buy, sell, time)""")

class Collector():
    time = __import__('time')
    def __init__(self):
        super(Collector, self).__init__()
##        self.jsonize=Json()
        self.get=Browser()
        self.get2=Browser()
        self.saver=Sql()
        self.timer=self.time.time
        self.transactions_u="https://www.blockchain.com/btc/unconfirmed-transactions"
        self.transactions_xpath="/html/body/div[1]/div[3]/div/div[3]/div"
        self.rate_u="https://www.binance.com/en/orderbook/BTC_USDT"
        self.buy_xpath="/html/body/div[1]/div[2]/div[2]/div[1]/div[3]/div[1]/div/div/div[1]/div[1]/div[2]"
        self.sell_xpath="/html/body/div[1]/div[2]/div[2]/div[2]/div[3]/div[1]/div/div/div[1]/div[1]/div[2]"
        self.transactions_page=self.get(self.transactions_u)
        self.rates_page=self.get2(self.rate_u)
        self.nodes=[]

    def __call__(self):
        while 1:
            trs=self.transactions()
            for t in range(1,int(len(trs)/4)):
                #t*4 t*4+1 t*4+2 t*4+3
                if(self.is_processed(trs[t*4])):
                    break
                else:
                    self.saver([trs[t*4],trs[t*4+2],self.timer()])
            self.saver([self.buy_rate(),self.sell_rate(),self.timer()],rate=True)
        
    def is_processed(self,x):
        return self.saver.get_by_txs(x)

    def transactions(self):
        return self.transactions_page.find_element_by_xpath(self.transactions_xpath).text.split("\n")

    def buy_rate(self):
        return self.rates_page.find_element_by_xpath(self.buy_xpath).text
    
    def sell_rate(self):
        return self.rates_page.find_element_by_xpath(self.sell_xpath).text

if __name__ == "__main__":
    collect=Collector()
    collect()
