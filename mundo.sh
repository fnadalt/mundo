#!/bin/bash

if [[ "$1" ]] && [[ "$1" = "01" ]];
then echo "Mundo 01" && cd $1 && python $2 main.py && cd ..;
elif [[ "$1" ]] && [[ "$1" = "02" ]];
then echo "Mundo 02" && cd $1 && python $2 main.py && cd ..;
fi;
