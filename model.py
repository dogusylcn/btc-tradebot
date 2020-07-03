#tensorflow==1.5

import tensorflow as tf

class Fuhuscoin():
    def __init__(self,ins,outs,hl):
        self.insize=ins
        self.outsize=outs
        self.hiddenlayers=hl
        self.optimizer=tf.train.AdamOptimizer
        self.placeholders()
        self.variables={}
        self.init_variables()
        self.sess=tf.Session()
        self.saver = tf.train.Saver(self.getvariables())
        
    def placeholders(self):
        self.last_24_hour_txs=tf.placeholder(tf.float32,shape=(None,self.insize), name="last_24_hour_txs")
        self.last_24_hour_buydiff=tf.placeholder(tf.float32,shape=(None,self.insize), name="last_24_hour_buydiff")
        self.last_24_hour_selldiff=tf.placeholder(tf.float32,shape=(None,self.insize), name="last_24_hour_selldiff")
        self.labels=tf.placeholder(tf.float32,shape=(None,self.outsize), name="labels")
        
    def init_variables(self):
        self.hls=[int((self.insize*3+self.outsize)/(self.hiddenlayers+1))*x for x in range(1,self.hiddenlayers+1)]
        self.variables["w-{}".format("start")]= tf.Variable(tf.random_normal_initializer()(shape=[self.insize*3, self.hls[0]], dtype=tf.float32), name="w-{}".format("start"))
        self.variables["b-{}".format("start")]= tf.Variable(tf.random_normal_initializer()(shape=[self.hls[0]], dtype=tf.float32), name="b-{}".format("start"))
        for i in range(self.hiddenlayers-1):
            self.variables["h-w-{}".format(i)]= tf.Variable(tf.random_normal_initializer()(shape=[self.hls[i], self.hls[i+1]], dtype=tf.float32), name="h-w-{}".format(i))
            self.variables["h-b-{}".format(i)]= tf.Variable(tf.random_normal_initializer()(shape=[self.hls[i+1]], dtype=tf.float32), name="h-b-{}".format(i))
        self.variables["w-{}".format("end")]= tf.Variable(tf.random_normal_initializer()(shape=[self.hls[-1],self.outsize], dtype=tf.float32), name="w-{}".format("end"))
        self.variables["b-{}".format("end")]= tf.Variable(tf.random_normal_initializer()(shape=[self.outsize], dtype=tf.float32), name="b-{}".format("end"))
        
    def evaluate(self):
        x=tf.concat([self.last_24_hour_txs,self.last_24_hour_buydiff,self.last_24_hour_selldiff],1)
        x=tf.matmul(x,self.variables["w-{}".format("start")])+self.variables["b-{}".format("start")]
        for i in range(self.hiddenlayers-1):
            x=tf.matmul(x,self.variables["h-w-{}".format(i)])+self.variables["h-b-{}".format(i)]
        return tf.matmul(x,self.variables["w-{}".format("end")])+self.variables["b-{}".format("end")]
        
    def loss(self):
        return tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits_v2(labels=self.labels, logits=self.evaluate()))
    
    def getvariables(self):
        return list(self.variables.values())
    
    def train(self, data, batch, epochs, lr):
        opt=self.optimizer(lr).minimize(self.loss(),var_list=self.getvariables())
        self.sess.run(tf.global_variables_initializer())
        self.sess.run(tf.local_variables_initializer())
        for epoch in range(epochs):
            for i in range(int(len(data[0])/batch)):
                logits=self.evaluate()
                self.sess.run(opt,
                                feed_dict={
                                   self.last_24_hour_txs:data[0][i*batch:(i+1)*batch],
                                   self.last_24_hour_buydiff:data[1][i*batch:(i+1)*batch],
                                   self.last_24_hour_selldiff:data[2][i*batch:(i+1)*batch],
                                   self.labels:data[3][i*batch:(i+1)*batch]
                                })
            if epoch%10==1:
                loss,ret=self.sess.run([self.loss(),tf.nn.softmax(self.evaluate())],
                                feed_dict={
                                   self.last_24_hour_txs:data[0],
                                   self.last_24_hour_buydiff:data[1],
                                   self.last_24_hour_selldiff:data[2],
                                   self.labels:data[3]
                                }
                              )
                print("Epoch: {} - Loss: {}".format(epoch,loss))
                print(ret)
                self.saver.save(self.sess,"C:/btc/fuhus-model/model.ckpt")
        self.saver.save(self.sess,"C:/btc/fuhus-model/model.ckpt")



model=Fuhuscoin(1440,3,3)

import numpy as np
 
x1=np.random.rand(5,1440)
x2=np.random.rand(5,1440)
x3=np.random.rand(5,1440)
x4=np.eye(3)[[0,1,2,2,1]]

model.train([x1,x2,x3,x4],5,41,0.0001)
