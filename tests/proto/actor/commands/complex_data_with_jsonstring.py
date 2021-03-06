#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @Author: Florian Briegel (briegel@mpia.de)
# @Date: 2021-08-12
# @Filename: complex_data_with_jsonstring.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)

'''
'''

from __future__ import annotations

import click
from clu.command import Command
from clu.parsers.click import command_parser
from cluplus.parsers.jsonstring import JsonStringParamType

import numpy as np


list_data = [1,2,3,4.0,5]
dict_data = {'a"': 10, "b": 20}
mixed_data = ["Hello there", 'Rigil Kent', 'C', 3, 0.815, {'D': 4711, 'e': "88"}]


@command_parser.command("sendData")
@click.argument("listdata", type=JsonStringParamType())
@click.argument("dictdata", type=JsonStringParamType())
@click.argument("mixeddata", type=JsonStringParamType())
async def sendData(command: Command, listdata, dictdata, mixeddata):

    if list_data != listdata: 
        command.fail(error=Exception("list data didnt work"))
        return
    
    if dict_data != dictdata: 
        command.fail(error=Exception("dict data didnt work"))
        return

    if mixed_data != mixeddata: 
        command.fail(error=Exception("mixed data didnt work"))
        return

    command.finish()


fits_dict =  [ \
['WCSAXES',                    2, "number of World Coordinate System axes"], \
['CRPIX1',               535.384, "x-coordinate of reference pixel"], \
['CRPIX2',                536.67, "y-coordinate of reference pixel"], \
['CRVAL1',    8.561000000000E+03, "first axis value at reference pixel"], \
['CRVAL2',    0.000000000000E+00, "second axis value at reference pixel2"], \
['CTYPE1',  'LAMBDA  '          , "the coordinate type for the first axis"], \
['CTYPE2',  'ANGLE   '          , "the coordinate type for the second axis"], \
['CD1_1 ',                 0.554, "partial of first axis coordinate w.r.t. x"], \
['CD1_2 ',                    0., "partial of first axis coordinate w.r.t. y"], \
['CD2_1 ',                    0., "partial of second axis coordinate w.r.t. x"], \
['CD2_2 ',   1.38889000000000E-5, "partial of second axis coordinate w.r.t. y"], \
['LTV1  ',                   19., "offset in X to subsection start"], \
['LTV2  ',                   20., "offset in Y to subsection start"], \
['LTM1_1',                    1., "reciprocal of sampling rate in X"], \
['LTM2_2',                    1., "reciprocal of sampling rate in Y"], \
['RA_APER',   1.761216666667E+02, "RA of aperture reference position"], \
['DEC_APER',   4.851611111111E+01, "Declination of aperture reference position"], \
['PA_APER',   1.143617019653E+02, "Position Angle of reference aperture center [de"], \
['DISPAXIS',                    1, "dispersion axis; 1 = axis 1, 2 = axis 2, none"], \
['CUNIT1',  'angstrom'          , "units of first coordinate value"], \
['CUNIT2',  'deg     '          , "units of second coordinate value"] \
]


@command_parser.command("fitsStyleData")
@click.argument("data", type=JsonStringParamType())
@click.option("--optData", type=JsonStringParamType(), default=None)
async def fitsStyleData(command: Command, data, optdata):

    if fits_dict != data: 
        command.fail(error=Exception("that didnt work"))
        return
    
    if optdata and fits_dict != optdata[0]: 
        command.fail(error=Exception("that didnt work"))
        return

    command.finish()




