#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @Author: Florian Briegel (briegel@mpia.de)
# @Date: 2021-08-12
# @Filename: jsonpickle.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)

'''
import os
import sys
import logging
import time
import uuid

import numpy as np
import jsonpickle
import asyncio
from proto.actor.exceptions import ProtoActorAPIError

from clu import AMQPClient, CommandStatus

loop=asyncio.new_event_loop()

amqpc = AMQPClient(name=f"{sys.argv[0]}.proxy-{uuid.uuid4().hex[:8]}")
loop.run_until_complete(amqpc.start())

def bigData(data):
    async def _call(data):
        proxy = amqpc.proxy('proto')
        fut = await proxy.send_command("bigData", "'" + data + "'")
        return await fut
    pickled_data = jsonpickle.encode(data, make_refs=False)
    return loop.run_until_complete(_call(pickled_data))
    


bright = np.rec.array([(1,'Sirius', -1.45, 'A1V'),
                       (2,'Canopus', -0.73, 'F0Ib'),
                       (3,'Rigil Kent', -0.1, 'G2V')],
                       formats='int16,a20,float32,a10',
                       names='order,name,mag,Sp')

ret = bigData(bright)
'''

from __future__ import annotations

import click
from clu.command import Command
from clu.parsers.click import command_parser
from cluplus.parsers.json import JsonPickleParamType, pickle, unpickle

import numpy as np


@command_parser.command("bigData")
@click.argument("data", type=JsonPickleParamType())
async def bigData(command: Command, data):
    """Returns the status of the outlets."""

    return command.finish(data=pickle(data))


@command_parser.command("moreBigData")
@click.argument("data1", type=JsonPickleParamType())
@click.argument("data2", type=JsonPickleParamType())
@click.argument("ival", type=int)
@click.option("--optData", type=JsonPickleParamType(), default=None)
async def moreBigData(command: Command, data1, data2, ival:int, optdata):
    """Returns the status of the outlets."""


    return command.finish()



