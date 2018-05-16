#!/usr/bin/env python

import argparse

import logging
log=logging.getLogger("main")

from land import Land

#
# __main__
#
if __name__=="__main__":
    # args
    parser=argparse.ArgumentParser()
    parser.add_argument("land_file", help="land description file")
    parser.add_argument("-r","--remove_files", action="store_true", default=False, help="delete files in directory")
    parser.add_argument("-c","--create_default_land_file", action="store_true", default=False, help="creates default land file")
    parser.add_argument("-d","--show_debug_info", action="store_true", default=False, help="logger level DEBUG")
    parser.add_argument("-g","--generate_data", action="store_true", default=False, help="generate data files")
    parser.add_argument("-i","--generate_images", action="store_true", default=False, help="generate corresponding images (heightmaps, ...)")
    parser.add_argument("-m","--generate_map", choices=["topography", "temperature", "humidity"], default="", help="generate map")
    parser.add_argument("-s","--map_size", type=int, default=1024, help="map size")
    args=parser.parse_args()
    # log
    log_level=logging.DEBUG if args.show_debug_info else logging.INFO
    logging.basicConfig(level=log_level)
    log.info("Land Creator")
    # land
    land=Land()
    land.execute(args)
