#!/bin/bash

for i in {001..090}
do
  TARGET="videoSRC${i}_1280x720_30_qp_00.264"
  echo $TARGET
  mkdir $TARGET
  mv ${TARGET}_*.png $TARGET
done

for i in {091..099}
do
  TARGET="videoSRC${i}_1280x720_24_qp_00.264"
  echo $TARGET
  mkdir $TARGET
  mv ${TARGET}_*.png $TARGET
done

#for i in {201..220}
#do
#  TARGET="videoSRC${i}_1280x720_24_qp_00.264"
#  echo $TARGET
#  mkdir $TARGET
#  mv ${TARGET}_*.png $TARGET
#done
