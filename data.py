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

    def get_txs(self):
        cursor=self.connection.cursor()
        cursor.execute("SELECT * FROM txs")
        return cursor.fetchall()

    def get_rates(self):
        cursor=self.connection.cursor()
        cursor.execute("SELECT * FROM rates")
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

class Creator():
    time = __import__('time')
    np = __import__('numpy')
    def __init__(self):
        super(Creator, self).__init__()
        self.saver=Sql()
        self.get_data()
        self.init_dates()
        self.init_rates()
        self.clip_data()

    def __call__(self, s=None):
        if(not s):
            s=self.time.strftime('%Y-%m-%d-%H-%M', self.time.localtime(self.time.time()))
        self.store(s)

    def get_data(self):
        self.txs=self.saver.get_txs()
        self.rates=self.saver.get_rates()

    def init_dates(self):
        cur_date=self.time.strftime('%Y-%m-%d %H:%M', self.time.localtime(int(float(self.txs[0][2]))))
        data_txs=[[.0,cur_date]]
        for i in range(len(self.txs)):
            n_date=self.time.strftime('%Y-%m-%d %H:%M', self.time.localtime(int(float(self.txs[i][2]))))
            if(cur_date!=n_date):
                cur_date=n_date
                data_txs.append([.0,.0])
                data_txs[-1][0]=float(self.txs[i][1].split()[0])
                data_txs[-1][1]=n_date
            else:
                data_txs[-1][0]+=float(self.txs[i][1].split()[0])

        self.txs=data_txs

        cur_date=self.time.strftime('%Y-%m-%d %H:%M', self.time.localtime(int(float(self.rates[0][2]))))
        data_rates=[]
        mb_rates=[]
        ms_rates=[]
        for i in range(len(self.rates)):
            n_date=self.time.strftime('%Y-%m-%d %H:%M', self.time.localtime(int(float(self.rates[i][2]))))
            if(cur_date!=n_date):
                cur_date=n_date
                data_rates.append([self.np.mean(mb_rates),self.np.mean(ms_rates),cur_date])
                mb_rates=[float(self.rates[i][0].replace(',',''))]
                ms_rates=[float(self.rates[i][1].replace(',',''))]
            else:
                mb_rates.append(float(self.rates[i][0].replace(',','')))
                ms_rates.append(float(self.rates[i][1].replace(',','')))
        self.rates=data_rates

    def init_rates(self):
        data_rates=self.rates[:-1]
        for i in range(len(self.rates)-1):
            data_rates[i][0]=100*(self.rates[i+1][0]-self.rates[i][0])/self.rates[i][0]
            data_rates[i][1]=100*(self.rates[i+1][1]-self.rates[i][1])/self.rates[i][1]
            data_rates[i][2]=self.rates[i+1][2]
        self.rates=data_rates

    def clip_data(self):
        while(self.rates[0][2]>self.txs[0][1]):
            self.txs=self.txs[1:]
        if(len(self.rates)!=len(self.txs)):
            while(len(self.rates)>len(self.txs)):
                self.rates=self.rates[:-1]
            while(len(self.rates)<len(self.txs)):
                self.txs=self.txs[:-1]

    def store(self,s):
        data=[[t[0],r[0],r[1],r[2]] for r,t in zip(self.rates,self.txs)]
        self.np.save("data-{}.npy".format(s),self.rates)

    def make_labels(self):
        return -1

        
import sys

if __name__ == "__main__":
    if(sys.argv[1]=="collect"):
        collect=Collector()
        collect()
    elif(sys.argv[1]=="create"):
        create=Creator()
        create()
