import os
import numpy as np
import tensorflow as tf
import tflearn
import h5py
from PIL import Image
from tflearn.data_utils import shuffle, to_categorical
from tflearn.layers.conv import max_pool_2d
import matplotlib.pyplot as plt
from matplotlib.pyplot import plot, savefig
import sys
# implmenation of vmaf neural network
# in 640x360
# out vmaf future score
#INPUT_W = 64
#INPUT_H = 36
INPUT_W = 64*4
INPUT_H = 36*4
#INPUT_W = 160
#INPUT_H = 90
INPUT_D = 3
# long seq
#INPUT_SEQ = 25
INPUT_SEQ = 1
OUTPUT_DIM = 5

KERNEL = int(sys.argv[1])
DENSE_SIZE = int(sys.argv[2])

#EPOCH = 1500
EPOCH = 10000
BATCH_SIZE = 50
LR_RATE = float(sys.argv[3])
EARLYSTOP = 50
#
# long term 1,5,10
#


def load_h5(filename):
    h5f = h5py.File(filename, 'r')
    X = h5f['X']
    Y = h5f['Y']
    X, Y = shuffle(X, Y)
    return X, Y
    
def CNN_Core(x,reuse=False):
    with tf.variable_scope('cnn_core',reuse=reuse):
        network = tflearn.conv_2d(
            x, KERNEL, 3, activation='relu', regularizer="L2",weight_decay=0.0001)
        network = tflearn.avg_pool_2d(network, 3)
        network = tflearn.conv_2d(
        network, KERNEL, 3, activation='relu', regularizer="L2",weight_decay=0.0001)
        network = tflearn.avg_pool_2d(network, 2)
        network = tflearn.fully_connected(
           network, DENSE_SIZE, activation='relu')
        split_flat = tflearn.flatten(network)
        return split_flat
    
def vqn_model(x):
    with tf.variable_scope('vqn'):
        inputs = tflearn.input_data(placeholder=x)
        _split_array = []

        for i in range(INPUT_SEQ):
            tmp_network = tf.reshape(
                inputs[:, i:i+1, :, :, :], [-1, INPUT_H, INPUT_W, INPUT_D])
            if i == 0:
                _split_array.append(CNN_Core(tmp_network))
            else:
                _split_array.append(CNN_Core(tmp_network,True))
            
        merge_net = tflearn.merge(_split_array, 'concat')
        merge_net = tflearn.flatten(merge_net)
        _count = merge_net.get_shape().as_list()[1]
        
        with tf.variable_scope('full-lstm'):
            net = tf.reshape(merge_net, [-1, _count / DENSE_SIZE, DENSE_SIZE])
            net = tflearn.gru(net, DENSE_SIZE, return_seq=True)
            out_gru = tflearn.gru(net, DENSE_SIZE,dropout=0.8)
            gru_result = tflearn.fully_connected(out_gru, DENSE_SIZE, activation='relu')
            
        out = tflearn.fully_connected(
            gru_result, OUTPUT_DIM, activation='sigmoid')

        return out

def save_plot(y_pred, y, j):
    plt.switch_backend('agg')
    plt.figure()
    fig, ax = plt.subplots(y.shape[1], 1, sharex=True,figsize=(10, 16), dpi=100)
    x = np.linspace(0, y.shape[0] - 1, y.shape[0])
        #ax.set_ylim(0,1)
    for i in range(y.shape[1]):
        ax[i].grid(True)
        ax[i].plot(x, y[:,i])
        ax[i].plot(x, y_pred[:,i])

    savefig('save/' + str(KERNEL) + '_' + str(DENSE_SIZE) + '_' + str(LR_RATE) + '/' + str(j) + '.png')

def load_data(dirs):
    _files = os.listdir(dirs)
    _array = []
    for _file in _files:
        _img = load_image(dirs + _file)
        _array.append(np.array(_img).shape)
    return np.array(_array)


def load_image(filename):
    img = Image.open(filename)
    return img


def event_loop():
    testX, testY = load_h5('../test_720p_vmaf.h5')

    gpu_options = tf.GPUOptions(allow_growth=True)
    with tf.Session(config=tf.ConfigProto(gpu_options=gpu_options)) as sess:
        x = tf.placeholder(shape=[None,  INPUT_SEQ, INPUT_H, INPUT_W, INPUT_D], dtype=tf.float32)
        y_ = tf.placeholder(shape=[None, OUTPUT_DIM], dtype=tf.float32)
        core_net = vqn_model(x)

        vars   = tf.trainable_variables() 
        lossL2 = tf.add_n([ tf.nn.l2_loss(v) for v in vars ]) * 1e-3

        core_net_loss = tflearn.objectives.mean_square(core_net, y_)
        #tf.sqrt(tf.reduce_mean(tf.square(tf.subtract(core_net, y_))))
        #tflearn.objectives.mean_square
        # + lossL2
        core_train_op = tf.train.AdamOptimizer(learning_rate=LR_RATE).minimize(core_net_loss)
        core_net_acc = tf.sqrt(tflearn.objectives.mean_square(core_net, y_))
        core_net_mape = tf.subtract(1.0,tf.reduce_mean(tf.abs(core_net - y_) / tf.abs(y_)))

        core_net_diff = tf.abs(core_net - y_)

        sess.run(tf.global_variables_initializer())
        saver = tf.train.Saver()
        best_saver = tf.train.Saver()

        # load model
        model_path = 'best/' + str(KERNEL) + '_' + str(DENSE_SIZE) + '_' + str(LR_RATE) + '/nn_model_ep_best.ckpt'
        print model_path
        saver.restore(sess, model_path)

        #model_ckpt = tf.train.latest_checkpoint(model_path)
        #saver.restore(sess, model_ckpt)

        _writer = open('log_test/' + str(KERNEL) + '_' + str(DENSE_SIZE) + '_' + str(LR_RATE) + '.csv','w')
        _min_mape, _min_step = 100.0, 0

        #_test_acc = sess.run(core_net_acc, feed_dict={x: testX,y_:testY})
        _test_diff = sess.run(core_net_diff, feed_dict={x: testX,y_:testY})
        print 'X : ', testX, ' diff ',_test_diff

        #_writer.write(str(j) + ',' + str(_test_mape) + '\n')
        _writer.write('Y : ')
        _writer.write('\n')
        for eachSet in testY:
            for eachY in eachSet:
                _writer.write(str(eachY) + ', ' )
            _writer.write('\n')
        _writer.write('\n')

        _writer.write('diff : ')
        for each_diff_set in _test_diff:
            for each_diff in each_diff_set:
                _writer.write(str(each_diff) + ', ')
            _writer.write('\n')
        _writer.write('\n')


def main():
    if os.path.exists('best/' + str(KERNEL) + '_' + str(DENSE_SIZE) + '_' + str(LR_RATE) + '.txt'):
        os.environ['CUDA_VISIBLE_DEVICES'] = '1'
        os.system('mkdir log_test')
        event_loop()


if __name__ == '__main__':
    main()

