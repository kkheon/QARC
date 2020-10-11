import os
import numpy as np
#from PIL import Image
import cv2
import h5py
# implmenation of vmaf neural network
# in 640x360
# out vmaf future score
# 5 + 4 + 3 + 2 + 1
#INPUT_W = 1280 // 8
#INPUT_H = 720 // 8
INPUT_W = 64
INPUT_H = 36
#INPUT_W = 256
#INPUT_H = 144
INPUT_D = 3
INPUT_SEQ = 25
#INPUT_SEQ = 1

import time

# 300,45.6419748364
# 500,60.3927594181
# 800,72.948687536
# 1100,81.1788565049
# 1400,86.2749310139


def load_y(filename):
    #_index = index + 1
    #_file += '_' + str(index) + '.yuv-480.log'
    #try:
    print filename + '_vmaf.log'
    _reader = open(filename + '_vmaf.log', 'r')
    _array = []
    for _line in _reader:
        _sp = _line.split(',') 
        _tmp = []
        for t in _sp:
            if len(t) > 1:
            	_tmp.append(float(t))
        _array.append(np.array(_tmp))
    _array = np.array(_array)
    #print _array
    return _array
    #except:
    #    #print 'error'
    #   return None


def load_image(filename):
    img = cv2.imread(filename)
    return img


# 5+4+3+2+1


def saveh5f(filename, x, y):
    #print y
    h5f = h5py.File(filename, 'w')
    h5f.create_dataset('X', data=x)
    h5f.create_dataset('Y', data=y)
    h5f.close()
    print 'save done'


def event_loop(MODE, N_SUBSET):
    IMG_PATH = 'img_' + MODE + '/'
    _dirs = os.listdir(IMG_PATH)
    _x_array, _y_array = [], []
    length_dir = len(_dirs)
    length_dir_subset = int(length_dir / N_SUBSET)

    #for _dir in _dirs:
    for idx, _dir in enumerate(_dirs):
        print _dir
        _files = os.listdir(IMG_PATH + _dir + '/')
        y = load_y(_dir)
        #_files.sort()
        _p = [int(l.split('_')[-1].split('.')[0]) for l in _files]
	_p.sort()
	x = np.zeros([INPUT_SEQ, INPUT_H, INPUT_W, INPUT_D])
        _index = 0
        for _file in _p:
            #x = np.roll(x, -1, axis=0)  # 5=>4=>3=>2=>1=>0=>-1 rotation. 

            _img = load_image(IMG_PATH + _dir + '/' + str(_file) + '.png')
            #x[-1] = _img    # add to last 

            x[0] = _img    # only one frame in x

            _index += 1     # image file count : frame count
            # why division by 5 ??? A : 5 means the number of target bitrates. 
            # every 5 frame, dataset is generated. 
            # but why?? it makes sense if they make a vmaf every 5-frame period. Did they??
            # fps 5 option is there. 
            #if _index % (INPUT_SEQ / 5) == 0:       # _index    = 0, 5, 10, 15
            #    _y_index = _index / (INPUT_SEQ / 5) # y_index   = 0, 1,  2,  3, ...
            #    #print _y_index
            #    if len(y) > _y_index:
            #        _x_array.append(x)              # 25 frame of video
            #        _y_array.append(y[_y_index])    # 5 bitrate's vmaf

            if len(y) > _index:
                _x_array.append(x)            # 25 frame of video
                _y_array.append(y[_index])    # 5 bitrate's vmaf

        # save partial 
        if N_SUBSET > 1:
            sub_idx = idx // length_dir_subset
            if (idx % length_dir_subset) == (length_dir_subset -1):
                print 'idx : %d, idx_subset : %d, length_subset : %d' % (idx, idx % length_dir_subset, length_dir_subset)
                saveh5f(MODE + '_720p_vmaf_' + str(sub_idx) + '.h5', _x_array, _y_array)
                _x_array, _y_array = [], []
                print len(_x_array)
                print len(_y_array)

    # save h5
    if N_SUBSET > 1:
        # save leftover
        sub_idx = idx // length_dir_subset
        saveh5f(MODE + '_720p_vmaf_' + str(sub_idx) + '.h5', _x_array, _y_array)
    else:
        saveh5f(MODE + '_720p_vmaf.h5', _x_array, _y_array)

    return np.array(_x_array), np.array(_y_array)
    #y_ = np.array([OUTPUT_DIM])


def main():
    MODE = 'train'
    N_SUBSET = 40
    x, y = event_loop(MODE, N_SUBSET)

    MODE = 'test'
    N_SUBSET = 10
    x, y = event_loop(MODE, N_SUBSET)

    #saveh5f('train_hd.h5', x, y)
    #saveh5f('train_720p_vmaf.h5', x, y)
    
    #saveh5f(MODE + '_720p_vmaf.h5', x, y)


if __name__ == '__main__':
    main()
