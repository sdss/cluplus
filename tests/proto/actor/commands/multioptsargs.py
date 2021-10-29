# -*- coding: utf-8 -*-
#
# @Author: Florian Briegel (briegel@mpia.de
# @Date: 2021-07-06
# @Filename: __init__.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)



from __future__ import annotations

import click
from clu.command import Command

#from . import command_parser
from clu.parsers.click import command_parser

from ..exceptions import ProtoActorAPIError


@command_parser.command("setEnabled")
@click.argument("enable", type=bool)
@click.option("--axis0", type=bool, default=True)
@click.option("--axis1", type=bool, default=True)
async def setEnabled(command: Command, enable:bool, axis0:bool, axis1:bool):
    """mount enable/disable axis"""

    return command.finish(
             enable=enable,
             axis0=axis0,
             axis1=axis1
           )

@command_parser.command("gotoRaDecJ2000")
@click.argument("RA_H", type=float)
@click.argument("DEG_D", type=float)
async def gotoRaDecJ2000(command: Command, ra_h: float, deg_d: float):
    """mount goto_ra_dec_j2000"""

    return command.finish(
             ra_h=ra_h,
             deg_d=deg_d
           )
