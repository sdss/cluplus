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


@command_parser.command(name='errRaise')
def errRaise(command: Command):
    """Raise Exception"""

    raise ProtoActorAPIError(message="boom ...")


@command_parser.command(name='errPass')
def errPass(command: Command):
    """Pass exception as argument."""

    command.fail(ProtoActorAPIError())
    

@command_parser.command(name='errPassAsError')
def errPassAsError(command: Command):
    """Pass exception as argument."""

    command.fail(error=ProtoActorAPIError())
    


