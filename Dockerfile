#FROM nvidia/cuda:10.0-base-ubuntu16.04
FROM nvidia/cuda:10.0-base
FROM tensorflow/tensorflow:1.15.0-gpu

RUN apt-get update \
    && apt-get install -y \
        vim

RUN apt-get install libsvm-dev -y
RUN apt-get install ffmpeg -y
RUN DEBIAN_FRONTEND="noninteractive" apt-get install python-tk -y

# for python
#RUN pip install h5py pillow scipy pandas opencv-python scikit-image
RUN pip install tflearn==0.3.2 scipy==1.2.2 matplotlib opencv-python tensorboard scikit-learn
RUN apt install -y libsm6 libxext6 libxrender1

# for memory leak detect
#RUN pip install pympler memory_profiler

COPY . /home/kkheon

# run make of vmaf
WORKDIR /home/kkheon/QARC/vmaf
RUN make

WORKDIR /home/kkheon

