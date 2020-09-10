import os
MODE = 'train'
TEST_FOLDER = './mov_train'

def main():
    test_files = os.listdir(TEST_FOLDER)
    for files in test_files:
        #os.system('python generate_1.py ' + files + '&')
        os.system('python generate_1.py ' + MODE + ' ' + files)

if __name__ == '__main__':
    main()
