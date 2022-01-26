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

import hashlib


@command_parser.command("stringTest")
@click.argument("string", type=str)
@click.argument("md5digest", type=str)
async def stringTest(command: Command, string: str, md5digest: str):
    """mount enable/disable axis"""

    string_md5digest = hashlib.md5(string.encode()).hexdigest()

    if md5digest != string_md5digest:
        print(f"{string} {md5digest} {string_md5digest}")
        return command.fail(error=Exception("md5 hash differ", string))
    
    return command.finish()
