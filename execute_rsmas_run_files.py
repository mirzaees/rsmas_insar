#!/usr/bin/env python3

import os
import sys
import logging
import argparse
import _process_utilities as putils
sys.path.insert(0, os.getenv('SSARAHOME'))
from pysar.utils import readfile
from pysar.utils import utils

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
std_formatter = logging.Formatter("%(levelname)s - %(message)s")
# process_rsmas.log File Logging
fileHandler = logging.FileHandler(os.getenv('SCRATCHDIR')+'/process_rsmas.log', 'a+', encoding=None)
fileHandler.setLevel(logging.INFO)
fileHandler.setFormatter(std_formatter)

# command line logging
streamHandler = logging.StreamHandler()
streamHandler.setLevel(logging.INFO)
streamHandler.setFormatter(std_formatter)

logger.addHandler(fileHandler)
logger.addHandler(streamHandler)


def create_parser():
    """ Creates command line argument parser object. """

    parser = argparse.ArgumentParser()
    parser.add_argument('custom_template_file', type=str, metavar="FILE", help='template file to use.')
    parser.add_argument('start', type=int,  help='Starting Run File to execute.')
    parser.add_argument('stop', type=int, help='Stopping Run File to execute.')
    return parser


def command_line_parse(args):
    """ Parses command line agurments into inps variable. """

    global inps;

    parser = create_parser();
    inps = parser.parse_args(args)


def get_run_files():

    logfile = os.path.join(inps.work_dir, 'out_stackSentinel.log')
    run_file_list = []
    with open(logfile, 'r') as f:
        new_f = f.readlines()
        f.seek(0)
        for line in new_f:
            if '/run_files/' in line:
                 run_file_list.append('run_files/'+line.split('/')[-1][:-1])
    return run_file_list[inps.start - 1:inps.stop]


def get_template_values(inps):

    # write default template
    inps.template_file = putils.create_default_template()

    inps.custom_template = putils.create_custom_template(
        custom_template_file=inps.custom_template_file,
        work_dir=inps.work_dir)

    if not inps.template_file == inps.custom_template:
        inps.template_file = utils.update_template_file(
            inps.template_file, inps.custom_template)

    inps.template = readfile.read_template(inps.template_file)

    putils.set_default_options(inps)



if __name__ == "__main__":
    command_line_parse(sys.argv[1:])
    inps.projName = putils.get_project_name(inps.custom_template_file)
    inps.work_dir = os.getenv('SCRATCHDIR') + '/' + inps.projName
    get_template_values(inps)
    logger.info("Executing Runfiles %s", str(inps.start) + ' to ' + str(inps.stop))
    run_file_list = get_run_files()
    memoryuse = putils.get_memory_defaults(inps.workflow)
    putils.submit_isce_jobs(run_file_list, inps.work_dir, memoryuse)
    logger.info("-----------------Done Executing Run files-------------------")
    
    
