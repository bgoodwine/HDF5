#!/bin/bash  
ts=$(date +%s%N)  
gzip files/katrina_frame.mp4
echo "single frame gzip compress:   $((($(date +%s%N) - $ts)/1000000)) ms"
ts=$(date +%s%N)  
gzip -d files/katrina_frame.mp4.gz
echo "single frame gzip uncompress: $((($(date +%s%N) - $ts)/1000000)) ms"
