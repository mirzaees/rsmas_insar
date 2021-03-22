#!/usr/bin/env bash
echo "sourcing ${RSMASINSAR_HOME}/setup/environment.bash ..."
#####################################
# Setting the environment (don't modify)
# check for required variables
#  set customizable variables to defaults if not given

############ FOR PROCESSING  #########
export SSARAHOME=${RSMASINSAR_HOME}/3rdparty/SSARA
export ISCE_HOME=/opt/conda/lib/python3.8/site-packages/isce
export ISCE_STACK=/opt/conda/share/isce2
export MINTPY_HOME=${RSMASINSAR_HOME}/sources/MintPy
export MINOPY_HOME=${RSMASINSAR_HOME}/sources/MiNoPy
export MIMTPY_HOME=${RSMASINSAR_HOME}/sources/MimtPy

############ FOR MODELLING  ###########
export GEODMOD_HOME=${RSMASINSAR_HOME}/sources/geodmod

###########  USEFUL VARIABLES  #########
export SAMPLESDIR=${RSMASINSAR_HOME}/samples

############## DASK ##############
export DASK_CONFIG=${MINTPY_HOME}/mintpy/defaults/
#export DASK_CONFIG=${RSMASINSAR_HOME}/sources/MintPy/mintpy/defaults

############## LAUNCHER ##############
export LAUNCHER_DIR=${RSMASINSAR_HOME}/3rdparty/launcher
export LAUNCHER_PLUGIN_DIR=${LAUNCHER_DIR}/plugins

##############  PYTHON  ##############
export PYTHON3DIR=/opt/conda
export CONDA_ENVS_PATH=/opt/conda/envs
export CONDA_PREFIX=${PYTHON3DIR}
export PROJ_LIB=${PYTHON3DIR}/share/proj
export GDAL_DATA=${PYTHON3DIR}/share/gdal

export PYTHONPATH=${PYTHONPATH-""}
export PYTHONPATH=${PYTHONPATH}:${MINTPY_HOME}
export PYTHONPATH=${PYTHONPATH}:${INT_SCR}
export PYTHONPATH=${PYTHONPATH}:${PYTHON3DIR}/lib/python3.8/site-packages:${ISCE_HOME}:${ISCE_HOME}/components
export PYTHONPATH=${PYTHONPATH}:${MINOPY_HOME}
export PYTHONPATH=${PYTHONPATH}:${MIMTPY_HOME}
export PYTHONPATH=${PYTHONPATH}:${RSMASINSAR_HOME}
export PYTHONPATH=${PYTHONPATH}:${RSMASINSAR_HOME}/sources/rsmas_tools
export PYTHONPATH=${PYTHONPATH}:${RSMASINSAR_HOME}/3rdparty/PyAPS/pyaps3
export PYTHONPATH=${PYTHONPATH}:${RSMASINSAR_HOME}/minsar/utils/ssara_ASF
export PYTHONPATH=${PYTHONPATH}:${RSMASINSAR_HOME}/sources      # needed for mimt. Need to talk to Sara on how to do this smarter
export PYTHONPATH_RSMAS=${PYTHONPATH}

######### Ignore warnings ############
export PYTHONWARNINGS="ignore"

############  PATH  #################
#####################################
export PATH=${PATH}:${SSARAHOME}
export PATH=${PATH}:${MINOPY_HOME}/minopy
export PATH=${PATH}:${MIMTPY_HOME}/mimtpy
export PATH=${PATH}:${RSMASINSAR_HOME}/minsar:${RSMASINSAR_HOME}/minsar/utils
export PATH=${PATH}:${RSMASINSAR_HOME}/minsar
export PATH=${PATH}:${RSMASINSAR_HOME}/minsar/utils/ssara_ASF
export PATH=${ISCE_HOME}/applications:${ISCE_HOME}/bin:${ISCE_STACK}:${PATH}
export PATH=${ISCE_HOME}/applications:${ISCE_HOME}/bin:${PATH}
export PATH=${PATH}:${RSMASINSAR_HOME}/sources/MimtPy
export PATH=${PATH}:${MINTPY_HOME}/mintpy:${MINTPY_HOME}/sh
export PATH=${PYTHON3DIR}/bin:${PATH}
export PATH=${PATH}:${PROJ_LIB}
export PATH=${PATH}:${RSMASINSAR_HOME}/3rdparty/tippecanoe
export PATH=${PATH}:${RSMASINSAR_HOME}/sources/insarmaps_scripts
export PATH=${PATH}:${DASK_CONFIG}
export PATH=${RSMASINSAR_HOME}/3rdparty/snaphu/bin:${PATH}

export LD_LIBRARY_PATH=${LD_LIBRARY_PATH-""}
export LD_LIBRARY_PATH=${PYTHON3DIR}/lib
export LD_RUN_PATH=${PYTHON3DIR}/lib

if [ -n "${prompt}" ]
then
    echo "RSMASINSAR_HOME:" ${RSMASINSAR_HOME}
    echo "PYTHON3DIR:     " ${PYTHON3DIR}
    echo "SSARAHOME:      " ${SSARAHOME}
fi



