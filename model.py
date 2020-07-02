import tensorflow as tf

class Fuhuscoin():
    def __init__(self,ins,outs,hl):
        self.insize=ins
        self.outsize=outs
        self.hiddenlayers=hl
        placeholders()
        
    def placeholders(self):
        self.last_24_hour_txs=tf.compat.v1.placeholder(tf.float32,shape=(?,self.insize), name="last_24_hour_txs")
        self.last_24_hour_buydiff=tf.compat.v1.placeholder(tf.float32,shape=(?,self.insize), name="last_24_hour_buydiff")
        self.last_24_hour_selldiff=tf.compat.v1.placeholder(tf.float32,shape=(?,self.insize), name="last_24_hour_selldiff")
        self.labels=tf.compat.v1.placeholder(tf.float32,shape=(?,self.outsize), name="labels")
        
    def variables(self):
        self.variables={}
        self.hls=[int((self.insize+self.outsize)/(hl+1))*x for x in range(1,self.hiddenlayers+1)]
        for j in ["t","b","s"]:
            self.variables{"{}w-{}".format(j,"start")}= tf.Variable(tf.random_normal_initializer(shape=[hls[i], hls[i+1]], dtype=tf.float32) name="{}w-{}".format(j,"start"))
            self.variables{"{}b-{}".format(j,"start")}= tf.Variable(tf.random_normal_initializer(shape=[hls[i+1]], dtype=tf.float32) name="{}b-{}".format(j,"start"))
        for i in range(self.hiddenlayers-1):
            for j in ["t","b","s"]:
                self.variables{"h{}w-{}".format(j,i)}= tf.Variable(tf.random_normal_initializer(shape=[hls[i], hls[i+1]], dtype=tf.float32) name="h{}w-{}".format(j,i))
                self.variables{"h{}b-{}".format(j,i)}= tf.Variable(tf.random_normal_initializer(shape=[hls[i+1]], dtype=tf.float32) name="h{}b-{}".format(j,i))

