#!/bin/bash
echo "Actualizar desde GDrive"
rclone sync $1 GDrive:/panda3d/mundo . --filter-from rclone-filter.txt --verbose=1
