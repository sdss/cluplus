# -*- coding: utf-8 -*-
#
# @Author: Florian Briegel (briegel@mpia.de)
# @Date: 2021-08-18
# @Filename: proxy.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)


from __future__ import annotations

import sys
import uuid
import os
import asyncio
from os.path import basename
from socket import gethostname

from functools import partial
from itertools import chain
from typing import Callable, Optional
from collections.abc import MutableMapping

from shlex import quote
import json

from inspect import getcoroutinelocals, iscoroutine
from clu import AMQPClient, AMQPReply, BaseClient

from .exceptions import ProxyPartialInvokeException, ProxyActorIsNotReachableException


class Proxy():
    """A proxy client with actor commands.
    """
   
    __commands = "__commands"
    __commands_key = "help"
    
    __amqpc = None

    def __init__(self, actor:str, amqpc:BaseClient = None, **kwargs):
        """ init """

        self.actor = actor
        self.amqpc = amqpc
#        self.task = None

        if not self.amqpc:
            if Proxy.__amqpc:
                self.amqpc = Proxy.__amqpc
            else:
                kwa = {"host": os.getenv("RMQ_HOST","localhost"), **kwargs}
                self.amqpc = Proxy.__amqpc = AMQPClient(name=f"{gethostname()}_{basename(sys.argv[0])}-{uuid.uuid4().hex[:8]}", **kwa)

 
    async def start(self):
        """Query and set actor commands."""

        if not self.isAmqpcConnected():
            await self.amqpc.start()

        await self.__pull_commands()
   
        return self


    async def stop(self):
        """stop actor"""
        pass # maybe stopping __pull_commands might be good

    @staticmethod
    def setDefaultAmqpc(amqpc):
        Proxy.__amqpc = amqpc


    def __getattr__(self, attr):
        try:
            object.__getattribute__(self, "ping")

        except AttributeError:
            self.amqpc.log.warning(f"actor {self.actor} {attr} currently not reachable.")
            setattr(self, attr, partial(self.call_command, attr))
#            raise ProxyActorIsNotReachableException()

        return self.__getattribute__(attr)

    async def __pull_commands(self, delay = 0):

        try:
            await asyncio.sleep(delay)

            reply = await self.call_command(Proxy.__commands)

            commands = reply[Proxy.__commands_key] if isinstance(reply, dict) else reply.help

            for c in commands:
                setattr(self, c, partial(self.call_command, c))
                # setattr(self, f"nowait_{c}", partial(self.call_command, c, nowait=True))
            # self.task = None

        except Exception as ex:
            if not delay:
                self.amqpc.log.warning(f"actor {self.actor} currently not reachable.")
            # self.task = self.amqpc.loop.create_task(self.__pull_commands(2))
            self.amqpc.loop.create_task(self.__pull_commands(2))


    def isAmqpcConnected(self):
        if not self.amqpc.connection.connection:
            return False
        return not self.amqpc.connection.connection.is_closed


    async def call_command(self,
                           command: str,
                           *args,
                           callback: Optional[Callable[[AMQPReply], None]] = None,
                           nowait:Bool = False,
                           object_hook: Optional[Callable[[AMQPReply], None]] = None,
                           **kwargs):

        def encode(v):
            if isinstance(v, (int, float, bool)): return v
            elif isinstance(v, str): return v if v[0] in "'\"" and v[-1] in "'\"" else quote(v)
            return f"'{json.dumps(v)}'"

        args = [encode(v) for v in args] \
             + list(chain.from_iterable(('--' + k, encode(v))
                                        for k, v in kwargs.items()))

        fu = await self.amqpc.send_command(self.actor,
                                                command,
                                                *args,
                                                callback=callback)
        
        if nowait: return fu

        ret = await fu

        if hasattr(ret, "status") and ret.status.did_fail:
            raise self._errorMapToException(ret.replies[-1].message['error'])

        return ProxyDict(ret.replies[-1].message)

    @staticmethod
    def _errorMapToException(em):
        if isinstance(em, dict):
            return Proxy._stringToException(em['exception_message'],
                                            em['exception_type'],
                                            em['exception_module'])
        return Exception(em)


    @staticmethod
    def _stringToException(sval, tn='Exception', mn='builtins'):
        try:
            module = sys.modules[mn] if mn in sys.modules \
                                     else __import__(mn, fromlist=tn)
            return getattr(module, tn)(sval)

        except AttributeError:
            return Exception(f'Unknown exception type {tn}-{sval}')

        except ImportError:
            return Exception(f'Unknown module type {mn}-{tn}:{sval}')


async def invoke(*cmds, return_exceptions:Bool=False):
    """invokes one or many commands in parallel

    On error it throws an exception if one of the commands fails as a dict
    with an exception and return values for every command.
    """
    
    ret = await asyncio.gather(*cmds, return_exceptions=True)

    ret = ProxyListOfDicts([ProxyDict(r) if isinstance(r, dict) else r for r in ret])

    if not return_exceptions:
        for r in ret:
            if isinstance(r, Exception):
                raise ProxyPartialInvokeException(*ret)
    return ret


def unpack(ret, *keys):
    """ unpacks every parameter from the message of the finish reply or list of replies.

        Pythons list unpacking mechanism PEP3132 can be used to assign the value(s)
        
        Be warned if you dont use it the correct way, 
        whould also be a good place to check the reply message format with schemas.

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
        keys
        return only the parameters from keys
    """

    if len(ret) == 0:
        return
    
    if isinstance(ret, list):
        if len(keys) > 0:
            rkeys = [k for r in ret for k in list(r.keys())]
            bkeys = [k for k in keys if k not in rkeys]
            if bkeys:
                raise KeyError(bkeys)

            return [d[k] for d in ret for k in keys if k in d]
        else:
            return [val for d in ret for val in list(d.values())]

    if len(ret) == 1:
        return list(ret.values())[0]
    elif len(keys) > 0:
        return [ret[k] for k in keys]
    else:
        return list(ret.values())


def flatten(d: MutableMapping, parent_key: str = '', sep: str = '.'):
    """ flattens a dict of dicts structure """
    def _flatten_dict_gen(d, parent_key, sep):
        for k, v in d.items():
            new_key = parent_key + sep + k if parent_key else k
            if isinstance(v, MutableMapping):
                yield from flatten(v, new_key, sep=sep).items()
            else:
                yield new_key, v

    return ProxyDict(_flatten_dict_gen(d, parent_key, sep))


class ProxyDict(dict):
   """ Extra helper class for the reply dict """
   def flatten(self):
        return flatten(self)

   def unpack(self, *keys):
        return unpack(self, *keys)


class ProxyListOfDicts(list):
   """ Extra helper class for the reply list of dicts """
   def flatten(self):
        return ProxyListOfDicts([flatten(d) for d in self])

   def unpack(self, *keys):
        return unpack(self, *keys)

