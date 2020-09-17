import os
#MODE = 'train'
MODE = 'test'
TEST_FOLDER = './mov_' + MODE

def main():
    file_list = os.listdir(TEST_FOLDER)
    file_list_py = [file for file in file_list if file.endswith(".264")]
    for files in file_list_py:
        print(files)
        #os.system('python generate_1_crop.py ' + MODE + ' ' + files)


    ## test
    #files = test_files[0]
    #os.system('python generate_1_crop.py ' + MODE + ' ' + files)


if __name__ == '__main__':
    main()
