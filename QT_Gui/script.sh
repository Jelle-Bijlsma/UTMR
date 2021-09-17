#!/bin/bash

while true; do
  time_ui=$(date -r ./gui_full.ui)
  time_python=$(date -r ./gui_full.py)

  time_ui2=$(date -r ./image_labeler.ui)
  time_python2=$(date -r ./image_labeler.py)

  time_ui3=$(date -r ./listbox.ui)
  time_python3=$(date -r ./listbox.py)

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
    touch image_labeler.py
    touch image_labeler.ui
  else
    echo "Converted Nothing"
  fi
  
    if [ "$time_ui3" != "$time_python3" ]; then
    pyuic5 -x listbox.ui -o listbox.py
    echo "Converted listbox"
    touch listbox.py
    touch listbox.ui
  else
    echo "Converted Nothing"
  fi



  sleep 10s
done
