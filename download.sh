#!/bin/sh

folder=j-archive

mkdir -pv $folder; cd $folder
for i in {1..3970}
do
  curl -O "http://j-archive.com/showgame.php?game_id=$i"
done
