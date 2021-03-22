#! /usr/bin/env python3
############################################################
# Copyright(c) 2017, Sara Mirzaee                          #
############################################################
import numpy as np
import os
import sys
from osgeo import gdal
import osr
import glob
import argparse
from minsar.objects.auto_defaults import PathFind
from minsar.utils.process_utilities import xmlread, cmd_line_parse
from minsar.objects import message_rsmas

pathObj = PathFind()
########################################

EXAMPLE = """example:
  create_amplitude_tif.py LombokSenAT156VV.template 
"""


def main(iargs=None):
    """
    Crops SLC images from Isce merged/SLC directory and creates georectified and orthorectified products.
    """

    inps = cmd_line_parse(iargs, script='export_amplitude_tif')

    secondary_dir = os.path.join(inps.work_dir, pathObj.mergedslcdir)
    pic_dir = os.path.join(inps.work_dir, pathObj.tiffdir)

    if not os.path.exists(pic_dir):
        os.mkdir(pic_dir)

    if not iargs is None:
        input_arguments = iargs
    else:
        input_arguments = sys.argv[1::]

    message_rsmas.log(pic_dir, os.path.basename(__file__) + ' ' + ' '.join(input_arguments))

    os.chdir(secondary_dir)

    try:
        os.system('rm '+ inps.input_file + '/geo*')
    except:
        print('geocoding ...')

    slc = inps.input_file

    if inps.im_type == 'ortho':
        inps.geo_reference_dir = os.path.join(inps.work_dir, pathObj.georeferencedir)
    else:
        inps.geo_reference_dir = os.path.join(inps.work_dir, pathObj.geomlatlondir)

    os.chdir(os.path.join(secondary_dir, inps.input_file))

    geocode_file(inps)

    gfile = 'geo_' + slc + '.slc.ml'
    ds = gdal.Open(gfile + '.vrt', gdal.GA_ReadOnly)
    array = np.abs(ds.GetRasterBand(1).ReadAsArray())
    del ds

    ##
    array = np.where(array > 0, 10.0 * np.log10(pow(array, 2)) - 83.0, array)

    if inps.im_type == 'ortho':
        dst_file = 'orthorectified_' + slc + '_backscatter.tif'
    else:
        dst_file = 'georectified_' + slc + '_backscatter.tif'

    data = gdal.Open(gfile, gdal.GA_ReadOnly)
    transform = data.GetGeoTransform()

    ##
    xmlfile = glob.glob(os.path.join(inps.work_dir, pathObj.referencedir, '*.xml'))[0]
    attributes = xmlread(xmlfile)
    Metadata = {'SAT': attributes['missionname'], 'Mode': attributes['passdirection'],
                'Image_Type': '{}_BackScatter'.format(inps.im_type), 'Date': slc}

    raster2geotiff(dst_file, transform, array, Metadata)

    print('Find the output in {}'.format(pic_dir))

    os.system('mv *.tif {}'.format(pic_dir))
    os.system('rm geo*')

    return


def raster2geotiff(newRasterfn, gtransform, array, metadata):
    """
    Exports the raster data to a geotiff format.
    :param newRasterfn: the name of output geotiff file
    :param gtransform: geo transform object for gdal
    :param array: raster to be written to the file
    :param metadata: all other metadata to be attached to the file
    """

    cols = array.shape[1]
    rows = array.shape[0]

    driver = gdal.GetDriverByName('GTiff')
    dst_options = ['COMPRESS=LZW']
    dst_nbands = 1
    outRaster = driver.Create(newRasterfn, cols, rows, dst_nbands, gdal.GDT_Float32, dst_options)
    outRaster.SetGeoTransform(gtransform)
    outband = outRaster.GetRasterBand(1)
    outband.SetMetadata(metadata)
    outband.WriteArray(array)
    outRasterSRS = osr.SpatialReference()
    outRasterSRS.ImportFromEPSG(4326)
    outRaster.SetProjection(outRasterSRS.ExportToWkt())
    outband.FlushCache()

    return


def geocode_file(inps):
    """
    Geocodes the input file
    :param inps: input name space
    """
    if 'stripmap' in inps.prefix:
        sys.path.append(os.path.join(os.getenv('ISCE_STACK'), 'stripmapStack'))
    else:
        sys.path.append(os.path.join(os.getenv('ISCE_STACK'), 'topsStack'))

    import geocodeGdal as gg

    inps.cropbox = [val for val in inps.cropbox.split()]
    if len(inps.cropbox) != 4:
        raise Exception('Bbox should contain 4 floating point values')

    scp_arg = {'latFile': os.path.abspath(os.path.join(inps.geo_reference_dir, inps.lat_file)),
                'lonFile': os.path.abspath(os.path.join(inps.geo_reference_dir, inps.lon_file)),
                'xOff': 0,
                'yOff': 0,
                'prodlist': [inps.input_file + '.slc.ml'],
                'resamplingMethod': 'near'}

    scp_arg = argparse.Namespace(**scp_arg)
    #scp_arg.prodlist = [inps.prod_list + '.slc.ml']

    WSEN = str(inps.cropbox[2]) + ' ' + str(inps.cropbox[0]) + ' ' + str(inps.cropbox[3]) + ' ' + str(inps.cropbox[1])
    latFile, lonFile = gg.prepare_lat_lon(scp_arg)

    gg.getBound(latFile, float(inps.cropbox[0]), float(inps.cropbox[1]), 'lat')
    gg.getBound(lonFile, float(inps.cropbox[2]), float(inps.cropbox[3]), 'lon')

    infile = os.path.abspath(inps.input_file + '.slc.ml')
    print('geocoding ' + infile)
    outFile = os.path.join(os.path.dirname(infile), "geo_" + os.path.basename(infile))
    gg.writeVRT(infile, latFile, lonFile)

    cmd = 'gdalwarp -of ENVI -geoloc  -te ' + WSEN + ' -tr ' + str(inps.lat_step) + ' ' + \
          str(inps.lon_step) + ' -srcnodata 0 -dstnodata 0 ' + ' -r ' + inps.resampling_method + \
          ' -co INTERLEAVE=BIL ' + infile + '.vrt ' + outFile
    print(cmd)
    os.system(cmd)

    # write_xml(outFile)
    cmd = "gdal2isce_xml.py -i " + outFile
    os.system(cmd)

    return


if __name__ == '__main__':
    '''
    Crop SLCs.
    '''
    main()
