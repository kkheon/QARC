#FROM nvidia/cuda:10.0-base-ubuntu16.04
FROM nvidia/cuda:10.0-base
FROM tensorflow/tensorflow:1.15.0-gpu

RUN apt-get update \
    && apt-get install -y \
        vim

RUN apt-get install libsvm-dev -y
RUN DEBIAN_FRONTEND="noninteractive" apt-get install python-tk -y

# for python
#RUN pip install h5py pillow scipy pandas opencv-python scikit-image
RUN pip install tflearn==0.3.2 scipy==1.2.2 matplotlib opencv-python tensorboard scikit-learn
RUN apt install -y libsm6 libxext6 libxrender1

# for memory leak detect
RUN pip install pympler memory_profiler

COPY . /home/kkheon
WORKDIR /home/kkheon

#VOLUME /data/kkheon/checkpoint
#VOLUME /data/kkheon/data_vsr_bak
#VOLUME /data/kkheon/dataset

#VOLUME /data/kkheon/checkpoint/lanczos_2160_to_1080_down
#VOLUME /data/kkheon/dataset/myanmar_v1/downsampled_lanczos_2160_to_1080/train_hm/lanczos_1080_to_2160
#VOLUME /data/kkheon/data_vsr_bak/train/train_lanczos_2160_to_1080/label
#COPY /data/kkheon/sr/datasets/loaded_harmonic sr/datasets

#CMD python sr/train.py
