class Maker():
    sleep = __import__('time').sleep
    np = __import__('numpy')
    reader=__import__("reader").Sql
    ig=__import__("operator").itemgetter
    def __init__(self):
        super(Maker, self).__init__()
        self.data=[]
        self.limit=15
        self.treshold=0.0001

    def __call__(self):
        while True:
            try:
                self.sleep(15*60*2)
                self.make()
            except:
                print("make_data.py hata verdi!")

    def make(self):
        self.rates=self.reader(rate=True)()
        self.txs=self.reader(rate=False)()
        self.init_rates()
        self.init_txs()
        self.clip_data()
        self.calc_labels()
        self.store()

    def store(self):
        data=[[t[0],r[0],l,r[1]] for r,t,l in zip(self.rates,self.txs,self.labels)]
        self.np.save("data.npy",data)

    def calc_labels(self):
        self.labels=[]
        rates,_=self.np.split(self.np.asarray(self.rates),2,1)
        rates.shape=(len(rates))
        rates=rates.astype(self.np.float)
        for i in range(len(rates)-self.limit):
            max_percent=self.calc_percent(rates[i],self.np.amax(rates[i:i+self.limit]))
            min_percent=self.calc_percent(rates[i],self.np.amin(rates[i:i+self.limit]))
            win=max_percent>self.treshold
            loss=abs(min_percent)>self.treshold
            if(win and loss):
                win_t=self.np.argmax(rates[i:i+self.limit])
                loss_t=self.np.argmin(rates[i:i+self.limit])
                if(win_t>loss_t):
                    self.labels.append(1)
                else:
                    self.labels.append(2)
            elif(win):
                self.labels.append(1)
            elif(loss):
                self.labels.append(2)
            else:
                self.labels.append(0)
        self.rates=self.rates[:-5]
        self.txs=self.txs[:-5]

    def calc_percent(self,t1,t2):
        return (t2-t1)/t1

    def init_rates(self):
        self.rates=sorted(self.rates, key=self.ig(1))
        data=[]
        stime="0"
        for i in self.rates:
            if i[-1]!=stime:
                data.append([float(i[0]),i[-1]])
                stime=i[-1]
            else:
                data[-1]=[float(i[0]),i[-1]]
        self.rates=data

    def init_txs(self):
        self.txs=sorted(self.txs, key=self.ig(2))
        data=[]
        stime="0"
        for i in self.txs:
            if i[-1]!=stime:
                data.append([float(i[1]),i[-1]])
                stime=i[-1]
            else:
                data[-1][0]+=float(i[1])
        self.txs=data
        
    def clip_data(self):
        while(self.rates[0][1]>self.txs[0][1]):
            self.txs=self.txs[1:]
        while(self.rates[0][1]<self.txs[0][1]):
            self.rates=self.rates[1:]
        if(len(self.rates)!=len(self.txs)):
            while(len(self.rates)>len(self.txs)):
                self.rates=self.rates[:-1]
            while(len(self.rates)<len(self.txs)):
                self.txs=self.txs[:-1]


if __name__ == "__main__":
    m=Maker()
    m()
