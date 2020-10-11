import os
#MODE = 'train'
MODE = 'test'
TEST_FOLDER = './mov_' + MODE

def main():
    test_files = os.listdir(TEST_FOLDER)
    file_list_py = [file for file in file_list if file.endswith(".264")]
    for files in file_list_py:
        #os.system('python generate.py ' + files + '&')
        os.system('python generate.py ' + MODE + ' ' + files)

if __name__ == '__main__':
    main()
