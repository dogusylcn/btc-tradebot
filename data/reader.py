class Sql():
    sqlite = __import__('sqlite3')
    def __init__(self,rate=False):
        super(Sql, self).__init__()
        self.rate=rate
        self.dbname='txs.sqlite'
        if(self.rate):
            self.dbname='rates.sqlite'
        self.connection = self.sqlite.connect(self.dbname)

    def __call__(self):
        cursor=self.connection.cursor()
        if(not self.rate):
            cursor.execute("SELECT * FROM txs")
        else:
            cursor.execute("SELECT * FROM rates")
        return cursor.fetchall()
