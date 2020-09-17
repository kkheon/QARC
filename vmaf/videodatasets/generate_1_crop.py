import os
import sys
import json
import commands
import re

import pandas as pd

#testrange = [300, 500, 800, 1100, 1400]
testrange = [500, 800, 1100, 1400, 1700]
#testrange = [800, 1100, 1400, 1700, 2000, 2300, 2600, 2900, 3200, 3500, 3800, 4100, ]
#testrange = [1000, 1500, 2000, 2500, 3000, 3500, 4000, 4500, 5000, ]
#WIDTH, HEIGHT = 800, 480
WIDTH, HEIGHT = 1280, 720
IMG_WIDTH, IMG_HEIGHT = 256, 144
#IMG_WIDTH, IMG_HEIGHT = 1280, 720
FPS = 25

N_PARTITION = (WIDTH / IMG_WIDTH) * (HEIGHT / IMG_HEIGHT)

def eventloop(mode, test_file_full):
    INPUT_PATH = './mov_' + mode
    IMG_PATH = 'img_' + mode

    # test
    # ffmpeg -loop 1 -i mov/videoSRC001_1280x720_30_qp_00.264 -vf "crop=iw/3:ih/4:mod(n,3)*iw/3:trunc(n/3)*ih/4" -vframes 5 out_%d.png
    #ffmpeg -i mov/videoSRC001_1280x720_30_qp_00.264 -vf "crop=w=256:h=144:x=0:y=0" -vframes 5 out_%d.png

    ## ffmpeg -i mov/1.flv -vf fps=25 -s 1280x720 img/1.flv/%5d.png

    #=== gen label
    #os.system('ffmpeg -threads 4 -y -i %s/%s -vf fps=%d -s 1280x720 %s/%%d.png' %
    #          (INPUT_PATH, test_file, FPS, TMP_PATH))
    for each_y in range(0, HEIGHT, IMG_HEIGHT):
        for each_x in range(0, WIDTH, IMG_WIDTH):

            test_file = test_file_full  + '_' + str(each_x) + '_' + str(each_y)

            EACH_IMG_PATH = IMG_PATH + '/' + test_file
            #TMP_PATH = 'tmp_' + mode + '_' + test_file
            #TMP2_PATH = 'tmp2_' + mode + '_' + test_file
            TMP_PATH = 'tmp_' + test_file
            #TMP2_PATH = 'tmp2_' + test_file

            #os.system('mkdir img_%s' % (mode))
            #os.system('mkdir img_%s/%s' % (test_file))
            #os.system('mkdir tmp_%s_%s' % (test_file))
            #os.system('mkdir tmp2_%s_%s' % (test_file))

            os.system('mkdir %s' % (IMG_PATH))
            os.system('mkdir %s' % (EACH_IMG_PATH))
            os.system('mkdir %s' % (TMP_PATH))
            #os.system('mkdir %s' % (TMP2_PATH))

            #=== gen label
            os.system('ffmpeg -threads 4 -y -i %s/%s -vf fps=%d -vf "crop=w=%d:h=%d:x=%d:y=%d" %s/%%d.png' %
              (INPUT_PATH, test_file_full, FPS, IMG_WIDTH, IMG_HEIGHT, each_x, each_y, TMP_PATH))

    #os.system('ffmpeg -threads 4 -y -i tmp_%s/%%d.png -vf fps=5 -s 64x36 img/%s_%%d.png' %

            os.system('ffmpeg -threads 4 -y -i %s/%%d.png -vf fps=%d -s %dx%d %s/%s_%%d.png' %
            #os.system('ffmpeg -threads 4 -y -i tmp_%s/%%d.png -vf fps=5 -s 1280x720 img/%s_%%d.png' %
                      (TMP_PATH, FPS, IMG_WIDTH, IMG_HEIGHT, EACH_IMG_PATH, test_file))

            #
            img_files = os.listdir('%s/' % TMP_PATH)
            img_files.sort()
            _count = len(img_files)
            #_file = open(test_file + '_vmaf.log', 'w')
            _filelen = open(test_file + '_len.log', 'w')

            df_video = pd.DataFrame()


            df = pd.DataFrame()
            #_file = open(test_file + '_frm_' + str(_frame) + '_vmaf.log', 'w')
            #for _p in xrange(FPS):
            #    os.system('cp -f tmp_%s/%d.png tmp2_%s/%d.png' %
            #              (test_file, _frame + _p, test_file, _p))
            os.system(
                'ffmpeg -threads 4 -y -i %s/%%d.png -pix_fmt yuv420p tmp_%s.yuv' % (TMP_PATH, test_file))
            for each_range in testrange:
                _range = each_range / N_PARTITION 
                os.system(
                    'ffmpeg -threads 4 -y -i %s/%%d.png -vcodec libx264 -s %dx%d -b:v %dk -f flv tmp_%s.flv' % 
                    (TMP_PATH, IMG_WIDTH, IMG_HEIGHT, _range, test_file))
                os.system(
                    '../ffmpeg2vmaf %d %d tmp_%s.yuv tmp_%s.flv --ref-fmt yuv420p --ref-width %d --ref-height %d --out-fmt json 1>tmp_%s_%d.json' % 
                    #(IMG_WIDTH, IMG_HEIGHT, test_file, test_file, IMG_WIDTH, IMG_HEIGHT, test_file, _range))
                    (IMG_WIDTH, IMG_HEIGHT, test_file, test_file, IMG_WIDTH, IMG_HEIGHT, test_file, each_range))
                _size = os.path.getsize('tmp_%s.flv' % (test_file, ))
                _filelen.write(str(_size))
                _filelen.write(',')
                #with open('tmp_' + test_file + '_' + str(_range) + '.json') as json_file:
                with open('tmp_' + test_file + '_' + str(each_range) + '.json') as json_file:
                    data = json.load(json_file)
                    #score = float(data['aggregate']['VMAF_score']) / 100.0
                    list_score = []
                    for each_frame in xrange(0, _count):
                        score = float(data['frames'][each_frame]['VMAF_score']) / 100.0
                        list_score.append(score)
                    #df[str(_range)] = pd.Series(list_score)    
                    df[str(each_range)] = pd.Series(list_score)    

            _filelen.write('\n')
            #_file.close()
            #df.to_csv(test_file + '_frm_' + str(_frame) + '_vmaf.log', index=False, header=None, sep=',')
            #df_video = df_video.append(df)
            #_file.close()
            _filelen.close()
            df.to_csv(test_file + '_vmaf.log', index=False, header=None, sep=',')
            #os.system('rm -rf tmp_%s' % (test_file))
            #os.system('rm -rf tmp2_%s' % (test_file))
            #os.system('rm -rf tmp_%s.flv' % (test_file))
            #os.system('rm -rf tmp_%s.yuv' % (test_file))
    print 'done'


import sys
mode = sys.argv[1]
each_file = sys.argv[2]
if __name__ == '__main__':
    os.system('export PYTHONPATH=\"$(pwd)/../python/src:$PYTHONPATH\"')
    #for _file in os.listdir('mov/'):
    #    eventloop(_file)
    eventloop(mode, each_file)
