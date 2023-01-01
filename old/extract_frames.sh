#!/bin/sh

ffmpeg -ss $2 -i "$1" -t $3 -f image2pipe -vf "format=gray, scale=$4:-2" -c:v pgm $4
