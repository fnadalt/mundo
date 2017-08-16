#!/bin/bash

rclone --verbose=1 --exclude="*.pyc" --exclude=".*" --exclude=".*/**"  --exclude="*.blend1" --exclude="parcelas/**" --exclude="*.7z" --exclude="*.xcf" -u $1 sync /home/flaco/panda3d/mundo GDrive:/panda3d/mundo
