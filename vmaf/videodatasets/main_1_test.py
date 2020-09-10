import os
#MODE = 'train'
MODE = 'test'
TEST_FOLDER = './mov_test'

def main():
    test_files = os.listdir(TEST_FOLDER)
    for files in test_files:
        #os.system('python generate_1.py ' + MODE + ' ' + files + '&')
        os.system('python generate_1.py ' + MODE + ' ' + files)

if __name__ == '__main__':
    main()
