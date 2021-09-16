#!/bin/bash

while true; do
  time_ui=$(date -r ./gui_full.ui)
  time_python=$(date -r ./gui_full.py)

  time_ui2=$(date -r ./image_labeler.ui)
  time_python2=$(date -r ./image_labeler.py)

  #echo $time_python
  #echo $time_ui


  if [ "$time_ui" != "$time_python" ]; then
    pyuic5 -x gui_full.ui -o gui_full.py
    echo "Converted gui_full"
    touch gui_full.py
    touch gui_full.ui
  else
    echo "Converted Nothing"
  fi

  if [ "$time_ui2" != "$time_python2" ]; then
    pyuic5 -x image_labeler.ui -o image_labeler.py
    echo "Converted image_labeler"
    touch gui_full.py
    touch gui_full.ui
  else
    echo "Converted Nothing"
  fi



  sleep 10s
done