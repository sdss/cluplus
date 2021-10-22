# -*- coding: utf-8 -*-
#
# @Author: Florian Briegel (briegel@mpia.de)
# @Date: 2021-08-18
# @Filename: proxy.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)

import logging
import asyncio
import sys
from copy import copy, deepcopy

import json
from types import SimpleNamespace
from typing import Any, Callable, Optional, Awaitable
from itertools import chain

from clu import BaseClient, AMQPReply, command_parser


class ProxyException(Exception):
    """Base proxy exception"""

    def __init__(self, argv):

        super(ProxyException, self).__init__(argv)


class ProxyPartialInvokeException(ProxyException):
    """Plain message formed exception string"""

    def __init__(self, *argv):

        super(ProxyPartialInvokeException, self).__init__(argv)



class ProxyClient:
    """A proxy representing an actor.

    Parameters
    ----------
    client
        The client used to command the actor.
    actor
        The actor to command.

    """

    def __init__(self, client: BaseClient, actor: str):

        self.client = client
        self.actor = actor

    def send_command(self, *args, callback: Optional[Callable[[AMQPReply], None]] = None,):
        """Sends a command to the actor.

        Returns the result of calling the client ``send_command()`` method
        with the actor and concatenated arguments as parameters. Note that
        in some cases the client ``send_command()`` method may be a coroutine
        function, in which case the returned coroutine needs to be awaited.

        Parameters
        ----------
        args
            Arguments to pass to the actor. They will be concatenated using spaces.

        """

        command = " ".join(map(str, args))

        return self.client.send_command(self.actor, command)


class Proxy(ProxyClient):
    """A proxy client with actor commands.

import uuid
from clu import AMQPClient, CommandStatus
from cluplus.proxy import Proxy, unpack, invoke

actor = "proto"

amqpc = AMQPClient(name=f"proxy-{uuid.uuid4().hex[:8]}")
amqpc.loop.run_until_complete(amqpc.start())

proxy = Proxy(amqpc, actor)
amqpc.loop.run_until_complete(proxy.start())

amqpc.loop.run_until_complete(proxy.ping())
unpack(amqpc.loop.run_until_complete(proxy.ping()))

try:
   amqpc.loop.run_until_complete(proxy.errPassAsError())
except Exception as ex:
   print(ex)

try:
   amqpc.loop.run_until_complete(invoke(proxy.ping(), proxy.version(), proxy.errPassAsError()))
except Exception as ex:
   print(ex)

    """
    def __init__(self, client: BaseClient, actor: str):
       super().__init__(client, actor)

    async def start(self):
        """Query actor for commands."""

        reply = await (await self.send_command("__commands"))

        commands = reply.replies[-1].body['help']
        
        for c in commands:
            setattr(self, c, lambda c=c, *args, blocking=True, **kwargs: self.call_command(c, *args, blocking=blocking, **kwargs))


    async def call_command(
        self,
        command: str,
        *args,
        callback: Optional[Callable[[AMQPReply], None]] = None,
        blocking: bool = True,
        **kwargs,
    ):
        opts=list(chain.from_iterable(('--'+k, v) for k, v in kwargs.items()))

        command =  await self.client.send_command(self.actor, command, *args, *opts, callback=callback)
        
        if not blocking: return command
    
        ret = await command

        if hasattr(ret, "status") and ret.status.did_fail:
            raise self._errorMapToException(ret.replies[-1].body['error'])

        return ret.replies[-1].body

    @staticmethod
    def _errorMapToException(em: dict):
        return Proxy._stringToException(em['exception_message'], em['exception_type'], em['exception_module'])


    @staticmethod
    def _stringToException(value_string, type_name='Exception', module_name='builtins'):
        try:
            module = sys.modules[module_name] if module_name in sys.modules else __import__(module_name, fromlist=type_name)
            return getattr(module, type_name)(value_string)

        except AttributeError:
            return Exception(f'Unknown exception type {type_name} - {value_string}')

        except ImportError:
            return Exception(f'Unknown module type {module_name} - {type_name}: {value_string}')



async def invoke(*argv):
    """invokes one or many commands in parallel
    
    On error it throws an exception if one of the commands fails as a dict with an exception and return values for every command.
    """
    ret = await asyncio.gather(*[asyncio.create_task(cmd) for cmd in argv], return_exceptions=True)
    for r in ret:
        if isinstance(r, Exception):
            raise ProxyPartialInvokeException(ret)
    return ret
        

def unpack(ret, *argv):
    """ invokes one command and unpacks every parameter from the body of the finish reply
    
        It uses pythons list unpacking mechanism PEP3132, be warned if you dont use it the correct way.
    
        >>> a, b, c = [1, 2, 3]
        >>> a
        1
        
        >>> a = [1, 2, 3]
        >>> a
        [1, 2, 3]
        
        >>> a, b = [1, 2, 3]
        Traceback (most recent call last):
        File "<stdin>", line 1, in <module>
        ValueError: too many values to unpack (expected 2)

        >>> a, *b = [1, 2, 3]
        >>> a
        1
        >>> b
        [2, 3]

        Parameters
        ----------
    
        argv
        return only the parameters from argv
    """
    
    if len(ret) == 0: return
    elif len(ret) == 1: return list(ret.values())[0] # Maybe we should check if argv is not empty and throw an exception
    elif len(argv) > 1: return [ret[i] for i in argv]
    else: return list(ret.values())

