#!/bin/bash

while true; do
  time_ui=$(date -r ./gui_full.ui)
  time_python=$(date -r ./gui_full.py)

  #echo $time_python
  #echo $time_ui


  if [ "$time_ui" != "$time_python" ]; then
    pyuic5 -x gui_full.ui -o gui_full.py
    echo "we did it boys"
    touch gui_full.py
    touch gui_full.ui
  else
    echo "hola, nothing happening here!"
  fi


  # this sets the time back to midnight, but it serves the purpose
  #
  #echo "The UI file is from:"
  #echo $(date -r ./gui_full.ui)
  #echo "The Python file is from:"
  #echo $(date -r ./gui_full.py)

  sleep 10s
done