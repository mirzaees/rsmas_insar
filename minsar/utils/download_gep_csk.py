#!/usr/bin/env python3
# Author: Sara Mirzaee

import os
import sys
import time
import subprocess
import datetime
import argparse
from minsar.objects.rsmas_logging import RsmasLogger, loglevel
from minsar.objects import message_rsmas
from minsar.utils import process_utilities as putils
import multiprocessing as mp


def main(iargs=None):

    inps = putils.cmd_line_parse(iargs, script='')

    if not iargs is None:
        input_arguments = iargs
    else:
        input_arguments = sys.argv[1::]

    message_rsmas.log(inps.work_dir, os.path.basename(__file__) + ' ' + ' '.join(input_arguments))

    logfile_name = inps.work_dir + '/gep_download.log'
    logger = RsmasLogger(file_name=logfile_name)

    if not inps.template['raw_image_dir'] in [None, 'None']:
        inps.slc_dir = inps.template['raw_image_dir']
    else:
        inps.slc_dir = os.path.join(inps.work_dir, 'RAW_data')

    project_slc_dir = os.path.join(inps.work_dir, 'RAW_data')
    os.makedirs(project_slc_dir, exist_ok=True)
    os.chdir(inps.slc_dir)

    logger.log(loglevel.INFO, "DATASET: %s", str(inps.custom_template_file.split('/')[-1].split(".")[0]))
    logger.log(loglevel.INFO, "DATE: %s", datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f"))


    start_date = inps.template['ssaraopt.startDate']
    start_date = datetime.datetime.strptime(start_date, '%Y%m%d')
    end_date = inps.template['ssaraopt.endDate']
    end_date = datetime.datetime.strptime(end_date, '%Y%m%d')


    if 'stripmapStack.boundingBox' in inps.template:
        bbox = inps.template['stripmapStack.boundingBox']
    else:
        bbox = inps.template['topsStack.boundingBox']

    bbox = bbox.split(' ')
    bbox = '{},{},{},{}'.format(bbox[2], bbox[0], bbox[3], bbox[1])
    user = subprocess.check_output("grep gepuser $RSMASINSAR_HOME/3rdparty/SSARA/password_config.py |\
     sed 's/\"//g''' | cut -d '=' -f 2", shell=True).decode('UTF-8').split('\n')[0]
    passwd = subprocess.check_output("grep geppass $RSMASINSAR_HOME/3rdparty/SSARA/password_config.py |\
     sed 's/\"//g''' | cut -d '=' -f 2", shell=True).decode('UTF-8').split('\n')[0]

    command_get_list = 'curl -s "https://catalog.terradue.com/csk/search?format=atom&count=1000&bbox={bbox}" |\
     xmllint --format - | grep enclosure | sed "s/.*<link rel="enclosure".*href="\(.*\)"\/>/\1/g"'.format(bbox=bbox)
    print(command_get_list)

    data_list = subprocess.check_output(command_get_list, shell=True).decode('UTF-8') #os.system(command_get_list)

    data_list = data_list.split('/>\n')
    data_list = [x.split('"')[-2] for x in data_list[0:-1]]

    cmd_all = []
    for data in data_list:
        if len(data.split('/')[-1]) > 20:
            date = datetime.datetime.strptime(data.split('/')[-1].split('_')[-1][0:8],'%Y%m%d')
            swath = int(data.split('/')[-1].split('_')[-6])
            if date >= start_date and date <= end_date and swath == int(inps.template['ssaraopt.relativeOrbit']):
                cmd = 'curl -u {username}:{password} -o $(basename ${enclosure}) {enclosure}'.format(username=user,
                                                                                                     password=passwd,
                                                                                                     enclosure=data)
                cmd_all.append(cmd)

    print(cmd_all)
    pool = mp.Pool(6)
    pool.map(os.system, cmd_all)
    pool.close()

    logger.log(loglevel.INFO, "Download Finish")
    logger.log(loglevel.INFO, "------------------------------------")

    return None


if __name__ == '__main__':
    main()
