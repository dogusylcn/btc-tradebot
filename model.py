## Fuhuscoin v0.1
## model=Fuhuscoin(ins,outs,hl,path="C:/btc/fuhus-model/model.ckpt")
##  - ins = input shape[1] (note that there is 3 same shaped input)
##  - out = output shape[1] (one hot array)
##  - hl = hidden layers
##  - path = model save path
## model.train(data, labels, batch, epochs, lr)
##  - data = input data ( list that contains 3 same shaped array )
##  - labels = output data ( one hot array )
##  - batch = batch size ( data will be separated by batch size )
##  - epochs = number of train process
##  - lr = learning rate for optimizer
## model(data) //returns model output
##  - data = input data ( list that contains 3 same shaped array )

import tensorflow as tf

class Fuhuscoin():
    np = __import__('numpy')
    def __init__(self,ins,outs,hl,path="C:/btc/fuhus-model/model.ckpt"):
        self.insize=ins
        self.outsize=outs
        self.hiddenlayers=hl
        self.optimizer=tf.train.AdamOptimizer
        self.placeholders()
        self.variables={}
        self.init_variables()
        self.sess=tf.Session()
        self.path=path
        self.saver = tf.train.Saver()

    def __call__(self,data):
        self.saver.restore(self.sess,self.path)
        ret=self.sess.run(tf.argmax(tf.nn.softmax(self.evaluate()),1),
                          feed_dict={
                                self.last_24_hour_txs:data[0],
                                self.last_24_hour_buydiff:data[1],
                                self.last_24_hour_selldiff:data[2]})
        print(ret)
        
        
    def placeholders(self):
        self.last_24_hour_txs=tf.placeholder(tf.float32,shape=(None,self.insize), name="last_24_hour_txs")
        self.last_24_hour_rates=tf.placeholder(tf.float32,shape=(None,self.insize), name="last_24_hour_rates")
        self.labels=tf.placeholder(tf.float32,shape=(None,self.outsize), name="labels")
        
    def init_variables(self):
        self.hls=[int((self.insize*2+self.outsize)/(self.hiddenlayers+1))*x for x in range(1,self.hiddenlayers+1)]
        self.variables["w-{}".format("start")]= tf.Variable(tf.zeros_initializer()(shape=[self.insize*2, self.hls[0]], dtype=tf.float32), name="w-{}".format("start"))
        self.variables["b-{}".format("start")]= tf.Variable(tf.zeros_initializer()(shape=[self.hls[0]], dtype=tf.float32), name="b-{}".format("start"))
        for i in range(self.hiddenlayers-1):
            self.variables["h-w-{}".format(i)]= tf.Variable(tf.zeros_initializer()(shape=[self.hls[i], self.hls[i+1]], dtype=tf.float32), name="h-w-{}".format(i))
            self.variables["h-b-{}".format(i)]= tf.Variable(tf.zeros_initializer()(shape=[self.hls[i+1]], dtype=tf.float32), name="h-b-{}".format(i))
        self.variables["w-{}".format("end")]= tf.Variable(tf.zeros_initializer()(shape=[self.hls[-1],self.outsize], dtype=tf.float32), name="w-{}".format("end"))
        self.variables["b-{}".format("end")]= tf.Variable(tf.zeros_initializer()(shape=[self.outsize], dtype=tf.float32), name="b-{}".format("end"))
        
    def evaluate(self):
        x=tf.concat([self.last_24_hour_txs,self.last_24_hour_rates],1)
        x=tf.matmul(x,self.variables["w-{}".format("start")])+self.variables["b-{}".format("start")]
        for i in range(self.hiddenlayers-1):
            x=tf.matmul(x,self.variables["h-w-{}".format(i)])+self.variables["h-b-{}".format(i)]
##            x=tf.nn.relu(x)
        return tf.matmul(x,self.variables["w-{}".format("end")])+self.variables["b-{}".format("end")]
        
    def loss(self):
        return tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits_v2(labels=self.labels, logits=self.evaluate()))
    
    def getvariables(self):
        return list(self.variables.values())
    
    def train(self, data, labels, batch, epochs, lr, load_model=False):
        opt=self.optimizer(lr).minimize(self.loss(),var_list=self.getvariables())
        if(load_model):
            self.sess.run(tf.global_variables_initializer())
            self.sess.run(tf.local_variables_initializer())
            self.saver.restore(self.sess,self.path)
        else:
            self.sess.run(tf.global_variables_initializer())
            self.sess.run(tf.local_variables_initializer())
        for epoch in range(epochs):
            for i in range(int(len(data[0])/batch)):
                logits=self.evaluate()
                correct_pred=tf.equal(tf.argmax(tf.nn.softmax(logits),1),tf.argmax(self.labels,1))
                accuracy=tf.reduce_mean(tf.cast(correct_pred,tf.float32))
                self.sess.run(opt,
                                feed_dict={
                                   self.last_24_hour_txs:data[0][i*batch:(i+1)*batch],
                                   self.last_24_hour_rates:data[1][i*batch:(i+1)*batch],
                                   self.labels:labels[i*batch:(i+1)*batch]
                                })
            if epoch%10==0:
                loss,acc=self.sess.run([self.loss(),accuracy],
                                feed_dict={
                                   self.last_24_hour_txs:data[0],
                                   self.last_24_hour_rates:data[1],
                                   self.labels:labels
                                }
                              )
                print("Epoch: {} - Loss: {} - accuracy: {}".format(epoch,loss,acc))
                self.saver.save(self.sess,self.path)
            if epoch%100==99:
                lr=lr/2
        self.saver.save(self.sess,self.path)

def data_to_input(x="C:/btc/data.npy"):
    data=np.load(x)
    if(len(data)<1440):
        print("data is to small")
        return -1
    x1,x2,lbls=[],[],[]
    in1,in2=[],[]
    for df in data:
        x1.append(float(df[0]))
        x2.append(float(df[1]))
        lbls.append(np.eye(3)[int(df[2])])
    for i in range(len(data)-1440):
        in1.append(x1[i:i+1440])
        in2.append(x2[i:i+1440])
    return in1,in2,lbls[1440:]

import numpy as np
import sys

##########################
x1,x2,lbls=data_to_input()
##########################

if __name__ == "__main__":
    if(sys.argv[1]=="train"):
        model=Fuhuscoin(1440,3,8)
        model.train([x1,x2],lbls,50,400,0.01,load_model=False)
    if(sys.argv[1]=="retrain"):
        model=Fuhuscoin(1440,3,8)
        model.train([x1,x2],lbls,50,400,0.01,load_model=True)

out=model([x1,x2])

for i in range(len(out)):
    print(out[i],lbls[i])
