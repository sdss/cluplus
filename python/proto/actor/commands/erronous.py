# -*- coding: utf-8 -*-
#
# @Author: Florian Briegel (briegel@mpia.de
# @Date: 2021-07-06
# @Filename: __init__.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)


'''
import os
import sys
import logging
import time
import uuid

import asyncio
from proto.actor.exceptions import ProtoActorAPIError

from clu import AMQPClient, CommandStatus
from cluplus.proxy import Proxy, ProxyException, ProxyPlainMessagException, invoke, unpack

loop=asyncio.new_event_loop()

amqpc = AMQPClient(name=f"{sys.argv[0]}.proxy-{uuid.uuid4().hex[:8]}")
loop.run_until_complete(amqpc.start())

def call(command):
    async def _call(command):
        proxy = amqpc.proxy('proto')
        fut = await proxy.send_command(command)
        return await fut
    return loop.run_until_complete(_call(command))


rc = call('errraise')
rc.status.did_fail
rc.replies[-1].body

rc = call('errpass')
rc.status.did_fail
rc.replies[-1].body

def exceptionDeserialize(value, type_name='Exception', module_name='builtins'):        
    try:
       if isinstance(value, dict):
           value_string = value["error"]["exception_message"]
           type_name = value["error"]["exception_type"]
           module_name = value["error"]["exception_module"]
    
       module = sys.modules[module_name] if module_name in sys.modules else __import__(module_name, fromlist=type_name)
       return getattr(module, type_name)(value_string)
    except AttributeError:
       return Exception(f'Unknown exception type {type_name} - {value_string}')
    except ImportError:
       return Exception(f'Unknown module type {module_name} - {type_name}: {value_string}')




rc = call('errpassaserror')
rc.status.did_fail
error = rc.replies[-1].body

raise exceptionDeserialize(error)

'''



from __future__ import annotations

import click
from clu.command import Command

#from . import command_parser
from clu.parsers.click import command_parser

from proto.actor.exceptions import ProtoActorAPIError


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
    


