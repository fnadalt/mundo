#!/bin/bash

rclone --verbose=2 --exclude="*.pyc" --exclude=".*" --exclude=".*/**"  --exclude="*.blend1" --exclude="parcelas/**" -u $1 sync /home/flaco/panda3d/mundo GDrive:/panda3d/mundo
