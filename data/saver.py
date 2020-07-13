class Sql():
    sqlite = __import__('sqlite3')
    def __init__(self,rate=False):
        super(Sql, self).__init__()
        self.rate=rate
        self.dbname='txs.sqlite'
        if(self.rate):
            self.dbname='rates.sqlite'
        self.connection = self.sqlite.connect(self.dbname)
        self.create_tables()

    def __call__(self,x):
        cursor=self.connection.cursor()
        if(not self.rate):
            query="""INSERT INTO txs VALUES ('{}', '{}', '{}')""".format(x[0],x[1],x[2])
        else:
            query="""INSERT INTO rates VALUES ('{}', '{}')""".format(x[0],x[1])
        cursor.execute(query)
        self.connection.commit()
        
    def create_tables(self):
        cursor=self.connection.cursor()
        if(not self.rate):
            cursor.execute("""CREATE TABLE IF NOT EXISTS txs (hash, total, time)""")
        else:
            cursor.execute("""CREATE TABLE IF NOT EXISTS rates (rate, time)""")
        
