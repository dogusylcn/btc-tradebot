#blockcypher yattı uyku tutmadı seleniumla yazdım
#blockchain.comdan çekiyoz

class Browser():
    selenium = __import__('selenium.webdriver').webdriver
    def __init__(self):
        super(Browser, self).__init__()
        self.browser=self.selenium.Chrome()

    def __call__(self,x):
        self.browser.get(x)
        return self.browser

class Json():
    _json = __import__('json')
    def __init__(self):
        super(Json, self).__init__()
        self.jsonize=self._json.loads
        
    def __call__(self,x):
        return self.jsonize(x)

class Sql():
    sqlite = __import__('sqlite3')
    def __init__(self):
        super(Sql, self).__init__()
        self.connection = self.sqlite.connect('db.sqlite')
        self.create_tables()

    def __call__(self,x):
        cursor=self.connection.cursor()
        if(len(x)==3):
            query="""INSERT INTO txs VALUES ('{}', '{}', '{}')""".format(x[0],x[1],x[2])
        else:
            query="""INSERT INTO rates VALUES ('{}', '{}')""".format(x[0],x[1])
        cursor.execute(query)
        self.connection.commit()

    def get_by_txs(self,x):
        cursor=self.connection.cursor()
        cursor.execute("""SELECT * FROM txs WHERE hash='{}'""".format(x))
        return cursor.fetchall()
        
    def create_tables(self):
        cursor=self.connection.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS txs (hash, total, time)""")
        cursor.execute("""CREATE TABLE IF NOT EXISTS rates (rate,time)""")

class Collector():
    time = __import__('time')
    def __init__(self):
        super(Collector, self).__init__()
        self.jsonize=Json()
        self.get=Browser()
        self.get2=Browser()
        self.saver=Sql()
        self.timer=self.time.time
        self.transactions_u="https://www.blockchain.com/btc/unconfirmed-transactions"
        self.transactions_xpath="/html/body/div[1]/div[3]/div/div[3]/div"
        self.rate_u="https://blockchain.info/ticker?base=BTC"
        self.transactions_page=self.get(self.transactions_u)
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
            self.saver([self.rate(),self.timer()])
        
    def is_processed(self,x):
        return self.saver.get_by_txs(x)

    def transactions(self):
        return self.transactions_page.find_element_by_xpath(self.transactions_xpath).text.split("\n")

    def rate(self):
        return self.jsonize(self.get2(self.rate_u).find_element_by_tag_name("body").text)["USD"]["15m"]

if __name__ == "__main__":
    collect=Collector()
    collect()
