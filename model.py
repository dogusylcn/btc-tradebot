import tensorflow as tf

class Fuhuscoin():
    def __init__(self,ins,outs,hl):
        self.insize=ins
        self.outsize=outs
        self.hiddenlayers=hl
        self.placeholders()
        self.variables()
        
    def placeholders(self):
        self.last_24_hour_txs=tf.compat.v1.placeholder(tf.float32,shape=(None,self.insize), name="last_24_hour_txs")
        self.last_24_hour_buydiff=tf.compat.v1.placeholder(tf.float32,shape=(None,self.insize), name="last_24_hour_buydiff")
        self.last_24_hour_selldiff=tf.compat.v1.placeholder(tf.float32,shape=(None,self.insize), name="last_24_hour_selldiff")
        self.labels=tf.compat.v1.placeholder(tf.float32,shape=(None,self.outsize), name="labels")
        
    def variables(self):
        self.variables={}
        self.hls=[int((self.insize*3+self.outsize)/(self.hiddenlayers+1))*x for x in range(1,self.hiddenlayers+1)]
        self.variables["w-{}".format("start")]= tf.Variable(tf.random_normal_initializer()(shape=[self.insize*3, self.hls[0]], dtype=tf.float32), name="w-{}".format("start"))
        self.variables["b-{}".format("start")]= tf.Variable(tf.random_normal_initializer()(shape=[self.hls[0]], dtype=tf.float32), name="b-{}".format("start"))
        for i in range(self.hiddenlayers-1):
            self.variables["h-w-{}".format(i)]= tf.Variable(tf.random_normal_initializer()(shape=[self.hls[i], self.hls[i+1]], dtype=tf.float32), name="h-w-{}".format(i))
            self.variables["h-b-{}".format(i)]= tf.Variable(tf.random_normal_initializer()(shape=[self.hls[i+1]], dtype=tf.float32), name="h-w-{}".format(i))
        self.variables["w-{}".format("end")]= tf.Variable(tf.random_normal_initializer()(shape=[self.hls[-1],self.outsize], dtype=tf.float32), name="w-{}".format("end"))
        self.variables["b-{}".format("end")]= tf.Variable(tf.random_normal_initializer()(shape=[self.outsize], dtype=tf.float32), name="w-{}".format("end"))
    
    def evaluate(self):
        x=tf.concat([self.last_24_hour_txs,self.last_24_hour_buydiff,self.last_24_hour_selldiff],1)
        x=tf.matmul(x,self.variables["w-{}".format("start")])+self.variables["b-{}".format("start")]
        for i in range(self.hiddenlayers-1):
            x=tf.matmul(x,self.variables["h-w-{}".format(i)])+self.variables["h-b-{}".format(i)]
        return tf.nn.softmax(tf.matmul(x,self.variables["w-{}".format("end")])+self.variables["b-{}".format("end")])
        
        
        
model=Fuhuscoin(1440,3,3)
print(model.evaluate().shape)