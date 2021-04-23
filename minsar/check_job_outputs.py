#!/usr/bin/env python3
########################
# Authors: Sara Mirzaee, Falk Amelung
#######################
import argparse
import os
import re
import glob
from pathlib import Path


def cmd_line_parser(iargs=None):

    parser = argparse.ArgumentParser(description='Check job outputs')
    parser.add_argument('job_files', nargs='+', type=str, help='batch job name:\n')
    inps = parser.parse_args(args=iargs)

    return inps


def main(iargs=None):

    inps = cmd_line_parser(iargs)
    work_dir = os.path.dirname(os.path.abspath(inps.job_files[0]))
    project_dir = os.path.dirname(work_dir)
    known_issues_file = os.path.join(os.getenv('RSMASINSAR_HOME'), 'docs/known_issues.md')

    error_happened = False
    error_strings  = [
                    'No annotation xml file found in zip file',
                    'There appears to be a gap between slices. Cannot stitch them successfully',
                    'no element found: line',
                    'Exiting ...',
                    'Segmentation fault',
                    'Bus',
                    'Aborted',
                    'ERROR',
                    'Error',
                    'FileNotFoundError',
                    'IOErr',
                    'Traceback'
                   ]

    #job_file = inps.job_files[0]
    #job_name = job_file.split('.')[0]
    #job_files = inps.job_files

    job_names=[]
    for job_file in inps.job_files:
        job_names.append(job_file.split('.')[0])
       
    job_file = inps.job_files[0]
    job_name = job_names[0]

    if 'run_' in job_name:
        run_file_base = '_'.join(job_name.split('_')[:-1])
    else:
        run_file_base = job_name

    matched_error_strings = []
    for job_name in job_names:
       print('checking *.e, *.o from ' + job_name + '.job')
       #job_name = job_file.split('.')[0]

       if 'filter_coherence' in job_name:
           remove_line_counter_lines_from_error_files(run_file=job_name)

       if 'run_' in job_name:
           remove_zero_size_or_length_error_files(run_file=job_name)
       
       if 'run_' in job_name:
           putils.remove_launcher_message_from_error_file(run_file=job_name)

       if 'run_' in job_name:
           putils.remove_zero_size_or_length_error_files(run_file=job_name)
       
       error_files = glob.glob(job_name + '*.e')
       out_files = glob.glob(job_name + '*.o')
       error_files.sort()
       out_files.sort()
       #error_files = natsorted(error_files)
       #out_files =  natsorted(out_files)

       for file in error_files + out_files:
           for error_string in error_strings:
               if check_words_in_file(file, error_string):
                   if skip_error(file, error_string):
                       break
                   matched_error_strings.append('Error: \"' + error_string + '\" found in ' + file + '\n')
                   print( 'Error: \"' + error_string + '\" found in ' + file )

    if len(matched_error_strings) != 0:
        with open(run_file_base + '_error_matches.e', 'w') as f:
            f.write(''.join(matched_error_strings))
    else:
        print("no known error found")
        
    if 'run_' in job_name:
         concatenate_error_files(run_file=run_file, work_dir=project_dir)
    else:
         out_error_file = os.path.dirname(error_files[-1]) + '/out_' + os.path.basename(error_files[-1])
         os.popen('cp {a} {b}'.format(a=error_files[-1], b=out_error_file))
         #shutil.copy(error_files[-1], out_error_file)

    if len(matched_error_strings) != 0:
        print('For known issues see https://github.com/geodesymiami/rsmas_insar/tree/master/docs/known_issues.md')
        raise RuntimeError('Error in run_file: ' + run_file_base)

    # move only if there was no error
    if len(os.path.dirname(run_file))==0:
       run_file = os.getcwd() + '/' + run_file
    move_out_job_files_to_stdout(run_file=run_file)

    return

def skip_error(file, error_string):
    """ skip error for merge_reference step if contains has different number of bursts (7) than the reference (9)  """
    """ https://github.com/geodesymiami/rsmas_insar/issues/436  """
    """ prior to https://github.com/isce-framework/isce2/pull/195 it did not raise exception  """

    skip = False
    if 'merge_reference_secondary_slc' in file or 'merge_burst_igram' in file:
       with open(file) as f:
        lines=f.read()
        if 'has different number of bursts' in lines and 'than the reference' in lines:
           skip = True

    with open(file) as f:
       lines=f.read()
       if '--- Logging error ---' in lines or '---Loggingerror---' in lines:
            skip = True


    return skip


def remove_line_counter_lines_from_error_files(run_file):
    """Removes lines with e.g. 'line:   398' from *.e files (filter_coherence step)"""

    error_files = glob.glob(run_file + '*.e*')
    error_files.sort()
    #error_files = natsorted(error_files)
    for item in error_files:
        f = open(item, 'r')
        lines = f.read()
        if "\nline:" in lines:
           tmp_line = lines.replace(" ","")
           new_lines = re.sub(r"\nline:\d+","", tmp_line)
           f.close()
           f = open(item, 'w')
           f.write(new_lines)

    return None

def remove_zero_size_or_length_error_files(run_file):
    """Removes files with zero size or zero length (*.e files in run_files)."""

    error_files = glob.glob(run_file + '*.e*') + glob.glob(run_file + '*.o*')
    error_files.sort()
    #error_files = natsorted(error_files)
    for item in error_files:
        if os.path.getsize(item) == 0:  # remove zero-size files
            os.remove(item)
        elif file_len(item) == 0:
            os.remove(item)  # remove zero-line files
    return None

def concatenate_error_files(run_file, work_dir):
    """
    Concatenate error files to one file (*.e files in run_files).
    :param directory: str
    :param out_name: str
    :return: None
    """

    out_file = os.path.abspath(work_dir) + '/out_' + run_file.split('/')[-1] + '.e'
    if os.path.isfile(out_file):
        os.remove(out_file).wait()

    out_name = os.path.dirname(run_file) + '/out_' + run_file.split('/')[-1] + '.e'

    error_files = glob.glob(run_file + '*.e*')
    error_files = natsorted(error_files)

    if not len(error_files) == 0:
        with open(out_name, 'w+') as outfile:
            for fname in error_files:
                outfile.write('#########################\n')
                outfile.write('#### ' + fname + ' \n')
                outfile.write('#########################\n')
                with open(fname) as infile:
                    outfile.write(infile.read())
                # os.remove(fname)

    if os.path.exists(os.path.abspath(out_name)):
        os.popen('cp -r {a} {b}'.format(a=os.path.abspath(out_name), b=os.path.abspath(work_dir)))
        # shutil.copy(os.path.abspath(out_name), os.path.abspath(work_dir))
        # os.remove(os.path.abspath(out_name))

    return None

def move_out_job_files_to_stdout(run_file):
    """move the stdout file into stdout_files directory"""
    stdout_files = glob.glob(run_file + '*.o')

    if len(stdout_files) == 0:
        return

    dir_name = os.path.dirname(run_file)
    out_folder = dir_name + '/stdout_' + os.path.basename(run_file)
    if not os.path.exists(out_folder):
        os.makedirs(out_folder, exist_ok=True)
    else:
        #shutil.rmtree(out_folder)
        os.popen('rm -rf {}'.format(out_folder))
        os.makedirs(out_folder, exist_ok=True)

    if len(stdout_files) >= 1:           #changed 9/2020. was 2 but unclear why
        for item in stdout_files:
            os.popen('mv {a} {b}'.format(a=item, b=out_folder))
            #shutil.move(item, out_folder)

    return None

def check_words_in_file(errfile, eword):
    """
    Checks for existence of a specific word in a file
    :param errfile: The file to be checked
    :param eword: The word to search for in the file
    :return: True if the word is in the file
    """

    with open(errfile, 'r') as f:
        lines = f.readlines()

    check_eword = [eword in item for item in lines]

    if sum(1*check_eword) > 0:
        return True
    else:
        return False

if __name__ == "__main__":
    main()


