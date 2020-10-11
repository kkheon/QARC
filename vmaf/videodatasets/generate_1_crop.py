import os
import sys
import json
import commands
import re
import cv2

import pandas as pd
import numpy as np

# bitrate
#testrange = [300, 500, 800, 1100, 1400]
##testrange = [1400]
##testrange = [500, 800, 1100, 1400, 1700]
##testrange = [800, 1100, 1400, 1700, 2000, 2300, 2600, 2900, 3200, 3500, 3800, 4100, ]
##testrange = [1000, 1500, 2000, 2500, 3000, 3500, 4000, 4500, 5000, ]

# QP 
testrange = [22, 27, 32, 37, 42]

#WIDTH, HEIGHT = 800, 480
WIDTH, HEIGHT = 1280, 720

#=== input size of CNN
IMG_WIDTH, IMG_HEIGHT = 64, 36
#IMG_WIDTH, IMG_HEIGHT = 256, 144
#IMG_WIDTH, IMG_HEIGHT = 1280, 720

FPS = 25
#FPS_SAMPLING = 25
FPS_SAMPLING = 5

N_PARTITION = (WIDTH / IMG_WIDTH) * (HEIGHT / IMG_HEIGHT)

def variance_check(sub_input):
    wsqrmean = np.mean(sub_input*sub_input)
    wmean = np.mean(sub_input)
    pixel_variance = wsqrmean - wmean*wmean

    if pixel_variance >= 0.0035:
        return True
    else:
        return False

def load_image(filename):
    img = cv2.imread(filename)
    return img

def eventloop(mode, test_file_full):
    INPUT_PATH = './mov_' + mode
    IMG_PATH = 'img_' + mode
    os.system('mkdir %s' % (IMG_PATH))

    #=== gen label
    #os.system('ffmpeg -threads 4 -y -i %s/%s -vf fps=%d -s 1280x720 %s/%%d.png' %
    #          (INPUT_PATH, test_file, FPS, TMP_PATH))

    for each_y in range(0, HEIGHT, IMG_HEIGHT):
        for each_x in range(0, WIDTH, IMG_WIDTH):
    #for each_y in range(IMG_HEIGHT*5, IMG_HEIGHT*6, IMG_HEIGHT):
    #    for each_x in range(IMG_WIDTH*5, IMG_WIDTH*6, IMG_WIDTH):

            test_file = test_file_full  + '_' + str(each_x) + '_' + str(each_y)

            #=== gen label
            TMP_PATH = 'tmp_' + test_file
            os.system('mkdir %s' % (TMP_PATH))
            ## from mov -> tmp && crop
            #os.system('ffmpeg -threads 4 -y -i %s/%s -vf fps=%d -vf "crop=w=%d:h=%d:x=%d:y=%d" %s/%%d.png' %
            #  (INPUT_PATH, test_file_full, FPS, IMG_WIDTH, IMG_HEIGHT, each_x, each_y, TMP_PATH))

            # load images from tmp_path 
            _files = os.listdir(TMP_PATH)
            list_img = []
            for each_file in _files:
                #print each_file
                _img = load_image(TMP_PATH + '/' + each_file)
                print _img.shape
                list_img.append(_img)
            img_set = np.stack(list_img)    
            print img_set.shape

            # variance test
            var_test_passed = variance_check(img_set)
            if var_test_passed == False:
                continue


    #os.system('ffmpeg -threads 4 -y -i tmp_%s/%%d.png -vf fps=5 -s 64x36 img/%s_%%d.png' %

            ##=== why this should be done? png to png???
            ## ORG : down-scale && sampling 
            ## Here : sampling 25 fps to 5fps
            ## from tmp -> img
            #EACH_IMG_PATH = IMG_PATH + '/' + test_file
            #os.system('mkdir %s' % (EACH_IMG_PATH))
            #os.system('ffmpeg -threads 4 -y -i %s/%%d.png -vf fps=%d -s %dx%d %s/%s_%%d.png' %
            ##os.system('ffmpeg -threads 4 -y -i tmp_%s/%%d.png -vf fps=5 -s 1280x720 img/%s_%%d.png' %
            #          (TMP_PATH, FPS_SAMPLING, IMG_WIDTH, IMG_HEIGHT, EACH_IMG_PATH, test_file))

            #
            img_files = os.listdir('%s/' % TMP_PATH)
            img_files.sort()
            _count = len(img_files)
            #_file = open(test_file + '_vmaf.log', 'w')
            #_filelen = open(test_file + '_len.log', 'w')

            df_video = pd.DataFrame()
            #_file = open(test_file + '_frm_' + str(_frame) + '_vmaf.log', 'w')
            TMP2_PATH = 'tmp2_' + test_file
            os.system('mkdir %s' % (TMP2_PATH))

            for _frame in xrange(1, _count + 1, FPS):
                df = pd.DataFrame()

                # generate period images : copy from tmp to tmp2 
                for _p in xrange(FPS):
                    os.system('cp -f tmp_%s/%d.png tmp2_%s/%d.png' % (test_file, _frame + _p, test_file, _p))

                ## gen label yuv for VMAF : from tmp2 image => yuv
                #os.system('ffmpeg -threads 4 -y -i %s/%%d.png -pix_fmt yuv420p tmp_%s.yuv' % (TMP2_PATH, test_file))

                for each_range in testrange:
                    ##=== bitrate mode
                    #_range = each_range // N_PARTITION 
                    #print '%f, %fk' % (_range, _range)

                    ##out_filename = 'tmp_%s_%dk.flv' % (test_file, _range)
                    ## encoding for each bitrate : from tmp2 image -> x264 video ".flv"
                    #os.system(
                    #    'ffmpeg -threads 4 -y -i %s/%%d.png -vcodec libx264 -s %dx%d -b:v %dk -f flv tmp_%s.flv' % 
                    #    (TMP2_PATH, IMG_WIDTH, IMG_HEIGHT, _range, test_file))

                    #=== fixed QP mode
                    os.system(
                        'ffmpeg -threads 4 -y -i %s/%%d.png -vcodec libx264 -s %dx%d -qp %d -f flv tmp_%s.flv' % 
                        (TMP2_PATH, IMG_WIDTH, IMG_HEIGHT, each_range, test_file))

                    # save tmp2 as image
                    TMP2_PATH_QP = TMP2_PATH + '_qp' + str(each_range) + '_frm_' + str(_frame)
                    os.system('mkdir %s' % (TMP2_PATH_QP))
                    os.system('cp tmp_%s.flv %s/' % (test_file, TMP2_PATH_QP))
                    os.system('ffmpeg -threads 4 -y -i tmp_%s.flv -vf fps=%d -s %dx%d %s/%%d.png' %
                              (test_file, FPS, IMG_WIDTH, IMG_HEIGHT, TMP2_PATH_QP))


            #        # gen vmaf yuv and x264 video
            #        os.system(
            #            '../ffmpeg2vmaf %d %d tmp_%s.yuv tmp_%s.flv --ref-fmt yuv420p --ref-width %d --ref-height %d --out-fmt json 1>tmp_%s_%d.json' % 
            #            #(IMG_WIDTH, IMG_HEIGHT, test_file, test_file, IMG_WIDTH, IMG_HEIGHT, test_file, _range))
            #            (IMG_WIDTH, IMG_HEIGHT, test_file, test_file, IMG_WIDTH, IMG_HEIGHT, test_file, each_range))
            #        _size = os.path.getsize('tmp_%s.flv' % (test_file, ))
            #        _filelen.write(str(_size))
            #        _filelen.write(',')
            #        #with open('tmp_' + test_file + '_' + str(_range) + '.json') as json_file:
            #        with open('tmp_' + test_file + '_' + str(each_range) + '.json') as json_file:
            #            data = json.load(json_file)

            #            ##=== FPS-frame avg VMAF
            #            score = float(data['aggregate']['VMAF_score']) / 100.0
            #            df[str(each_range)] = pd.Series(score)    

            #            ##=== frame-level VMAF
            #            #list_score = []
            #            #for each_frame in xrange(0, _count):
            #            #    score = float(data['frames'][each_frame]['VMAF_score']) / 100.0
            #            #    list_score.append(score)
            #            ##df[str(_range)] = pd.Series(list_score)    
            #            #df[str(each_range)] = pd.Series(list_score)    

            #    #=== end of each_range
            #    df_video = df_video.append(df)

            #_filelen.write('\n')
            ##_file.close()
            ##df.to_csv(test_file + '_frm_' + str(_frame) + '_vmaf.log', index=False, header=None, sep=',')
            ##df_video = df_video.append(df)
            ##_file.close()
            #_filelen.close()
            ##df.to_csv(test_file + '_vmaf.log', index=False, header=None, sep=',')
            #df_video.to_csv(test_file + '_vmaf.log', index=False, header=None, sep=',')
            ##os.system('rm -rf tmp_%s' % (test_file))
            ##os.system('rm -rf tmp2_%s' % (test_file))
            ##os.system('rm -rf tmp_%s.flv' % (test_file))
            ##os.system('rm -rf tmp_%s.yuv' % (test_file))
    print 'done'


import sys
mode = sys.argv[1]
each_file = sys.argv[2]
if __name__ == '__main__':
    os.system('export PYTHONPATH=\"$(pwd)/../python/src:$PYTHONPATH\"')
    #for _file in os.listdir('mov/'):
    #    eventloop(_file)
    eventloop(mode, each_file)
