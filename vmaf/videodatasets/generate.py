import os
import sys
import json
import commands
import re

testrange = [300, 500, 800, 1100, 1400]
# QP 
testrange = [22, 27, 32, 37, 42]

#WIDTH, HEIGHT = 800, 480
WIDTH, HEIGHT = 1280, 720
FPS = 25


def eventloop(mode, test_file):
    INPUT_PATH = './mov_' + mode
    IMG_PATH = 'img_' + mode
    EACH_IMG_PATH = IMG_PATH + '/' + test_file
    #TMP_PATH = 'tmp_' + mode + '_' + test_file
    #TMP2_PATH = 'tmp2_' + mode + '_' + test_file
    TMP_PATH = 'tmp_' + test_file
    TMP2_PATH = 'tmp2_' + test_file

    #os.system('mkdir img_%s' % (mode))
    #os.system('mkdir img_%s/%s' % (test_file))
    #os.system('mkdir tmp_%s_%s' % (test_file))
    #os.system('mkdir tmp2_%s_%s' % (test_file))

    os.system('mkdir %s' % (IMG_PATH))
    os.system('mkdir %s' % (EACH_IMG_PATH))
    os.system('mkdir %s' % (TMP_PATH))
    os.system('mkdir %s' % (TMP2_PATH))

    # ffmpeg -i mov/1.flv -vf fps=25 -s 1280x720 img/1.flv/%5d.png
    os.system('ffmpeg -threads 4 -y -i %s/%s -vf fps=%d -s 1280x720 %s/%%d.png' %
              (INPUT_PATH, test_file, FPS, TMP_PATH))

    # downscale && sampling 25 fps to 5 fps
    os.system('ffmpeg -threads 4 -y -i %s/%%d.png -vf fps=5 -s 64x36 %s/%s_%%d.png' %
    #os.system('ffmpeg -threads 4 -y -i tmp_%s/%%d.png -vf fps=5 -s 1280x720 img/%s_%%d.png' %
              (TMP_PATH, EACH_IMG_PATH, test_file))
    img_files = os.listdir('tmp_%s/' % test_file)
    img_files.sort()
    _count = len(img_files)
    _file = open(test_file + '_vmaf.log', 'w')
    _filelen = open(test_file + '_len.log', 'w')

    for _frame in xrange(1, _count + 1, FPS):
        for _p in xrange(FPS):
            os.system('cp -f tmp_%s/%d.png tmp2_%s/%d.png' %
                      (test_file, _frame + _p, test_file, _p))
        os.system(
            'ffmpeg -threads 4 -y -i tmp2_%s/%%d.png -pix_fmt yuv420p tmp_%s.yuv' % (test_file, test_file))
        for _range in testrange:
            #os.system(
            #    'ffmpeg -threads 4 -y -i tmp2_%s/%%d.png -vcodec libx264 -s %dx%d -b:v %dk -f flv tmp_%s.flv' % (test_file, WIDTH, HEIGHT, _range, test_file))
            os.system(
                'ffmpeg -threads 4 -y -i tmp2_%s/%%d.png -vcodec libx264 -s %dx%d -qp %d -f flv tmp_%s.flv' % (test_file, WIDTH, HEIGHT, _range, test_file))
            os.system(
                '../ffmpeg2vmaf %d %d tmp_%s.yuv tmp_%s.flv --ref-fmt yuv420p --ref-width 1280 --ref-height 720 --out-fmt json 1>tmp_%s.json' % (WIDTH, HEIGHT, test_file, test_file, test_file))
            _size = os.path.getsize('tmp_%s.flv' % (test_file))
            _filelen.write(str(_size))
            _filelen.write(',')
            with open('tmp_' + test_file + '.json') as json_file:
                data = json.load(json_file)
                score = float(data['aggregate']['VMAF_score']) / 100.0
                _file.write(str(score))
                _file.write(',')
        _file.write('\n')
        _filelen.write('\n')
    _file.close()
    _filelen.close()
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
