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
import fnmatch

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
from clu import AMQPClient, AMQPReply, BaseClient, CommandStatus

from .exceptions import ProxyPartialInvokeException, ProxyActorIsNotReachableException, ProxyUnpackKeysNotAllFoundException

class Client(AMQPClient):
    """An amqpc client with enviroment support.
    """
    def __init__(self, **kwargs):
        """ init """

        kwargs = {"url": os.getenv("RMQ_URL", None), "host": os.getenv("RMQ_HOST", "localhost"), **kwargs}
        name = f"{gethostname()}_{basename(sys.argv[0])}-{uuid.uuid4().hex[:8]}"
        AMQPClient.__init__(self, name=name, **kwargs)


class Proxy():
    """A proxy client with actor commands.
    """
   
    __commands = "__commands"
    __commands_key = "help"
    __pull_commands_task = "_pull_commands_task"
    
    __amqpc = None

    pull_commands_delay = 2
    pull_commands_attempts = 42

    def __init__(self, actor:str, amqpc:BaseClient = None, **kwargs):
        """ init """

        self.actor = actor
        self.amqpc = amqpc

        if not self.amqpc:
            if Proxy.__amqpc:
                self.amqpc = Proxy.__amqpc
            else:
                self.amqpc = Proxy.__amqpc = Client(**kwargs)

    async def start(self, amqpc:BaseClient = None):
        """Query and set actor commands."""

        if amqpc:
            if self.amqpc:
                await self.amqpc.stop()
            self.amqpc = amqpc

        if not self.isAmqpcConnected():
            await self.amqpc.start()

        await self._pull_commands()
   
        return self


    async def stop(self):
        """stop actor"""
        await self.__delattr_pull_commands_task(cancel=True)

    @staticmethod
    def setDefaultAmqpc(amqpc):
        Proxy.__amqpc = amqpc

    def __getattr__(self, attr):
        # order is important !
        if attr != Proxy.__pull_commands_task and hasattr(self, Proxy.__pull_commands_task):
            return partial(self.call_command, attr)
        return super(Proxy, self).__getattribute__(attr)


    async def __delattr_pull_commands_task(self, cancel=False):
        lock = asyncio.Lock()
        async with lock:
            if hasattr(self, Proxy.__pull_commands_task):
                if cancel:
                    self._pull_commands_task.cancel()
                    try:
                        await self._pull_commands_task
                    except asyncio.exceptions.CancelledError as ex:
                        self.amqpc.log.debug(f"error {ex}")
                delattr(self ,Proxy.__pull_commands_task)
        

    async def _pull_commands(self, delay = 0, attempts = 1):
        for c in range(attempts):
            try:
                await asyncio.sleep(delay)

                reply = await self.call_command(Proxy.__commands)

                commands = reply[Proxy.__commands_key] if isinstance(reply, dict) else reply.help

                for c in commands:
                    setattr(self, c, partial(self.call_command, c))
                    # setattr(self, f"nowait_{c}", partial(self.call_command, c, nowait=True))

                await self.__delattr_pull_commands_task()
                return


            except Exception as ex:
                if not delay:
                    self.amqpc.log.warning(f"actor {self.actor} currently not reachable.")
                if not hasattr(self, Proxy.__pull_commands_task):
                    self.amqpc.log.debug(f"actor {self.actor} connect as background task.")
                    self._pull_commands_task = self.amqpc.loop.create_task(self._pull_commands(Proxy.pull_commands_delay, Proxy.pull_commands_attempts))
                    return    

        self.amqpc.log.debug(f"actor {self.actor} connect attempts stopped.")
        await self.__delattr_pull_commands_task()


    def isAmqpcConnected(self):
        if not self.amqpc.connection.connection:
            return False
        return not self.amqpc.connection.connection.is_closed



    async def _handle_command_reply(self, fu):

        reply = await fu

        if hasattr(reply, "status") and reply.status.did_fail:
            raise self._errorMapToException(reply.replies[-1].message['error'])

        msg = ProxyDict(reply.replies[-1].message)
        msg.sender = reply.actor

        return msg

    def _handle_callback(self, callback: Optional[Callable[[AMQPReply], None]], reply: AMQPReply):
        msg = ProxyDict(json.loads(reply.message.body))
        msg.command_status = CommandStatus.code_to_status(reply.message_code)
        msg.sender = reply.sender
        callback(msg)

    async def call_command(self,
                           command: str,
                           *args,
                           callback: Optional[Callable[[dict], None]] = None,
                           time_limit: Optional[float] = 42.0,
                           nowait:Bool = False,
                           nosync:Bool = False,
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
                                           callback=partial(self._handle_callback, callback) if callback else None,
                                           time_limit=time_limit)
        


        if nosync: return
        if nowait: return self._handle_command_reply(fu)

        return await self._handle_command_reply(fu)


    @staticmethod
    def _errorMapToException(em):
        if isinstance(em, dict):
            return Proxy._stringToException(em['exception_message'],
                                            em['exception_type'],
                                            em['exception_module'])
        return Exception(em)

    @staticmethod
    def _exceptionToMap(ex):
        return { "exception_module": ex.__class__.__module__, "exception_type": ex.__class__.__name__, "exception_message": str(ex) }


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

    def isProxy(p):
        return 'self' in p.cr_frame.f_locals and isinstance(p.cr_frame.f_locals['self'], Proxy)

    actors=[c.cr_frame.f_locals['self'].actor if isProxy(c) else 'local' for c in cmds]

    ret = await asyncio.gather(*cmds, return_exceptions=True)

    def _format(r):
        if isinstance(r, dict): return ProxyDict(r)
        elif isinstance(r, Exception): return ProxyDict({'error': r}) 
        else: return r

    ret = ProxyListOfDicts([_format(r) for r in ret])
    ret.actors = actors

    if not return_exceptions:
        for r in ret:
            if isinstance(r, dict) and "error" in r.keys():
                raise ProxyPartialInvokeException(*ret)

    return ret


def unpack(data, *keys, as_seq:bool=False, exception_on_missing_keys:bool=False):
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

    if len(data) == 0:
        return

    def unpacking(data:list, as_seq:bool=False):
        if len(data) > 1 or as_seq: return data
        return data[0] if len(data) else None

    if isinstance(data, list):
        if len(keys) > 0:
            rkeys = [k for r in data for k in list(r.keys())]
            if exception_on_missing_keys:
                bkeys = [k for k in keys if not fnmatch.filter(rkeys, k)]
                if bkeys:
                    raise ProxyUnpackKeysNotAllFoundException(bkeys)

            return unpacking([d[fn] for k in keys for d in data for fn in fnmatch.filter(d, k)],  as_seq)
        else:
            return unpacking([val for d in data for val in list(d.values())], as_seq)

    if len(data) == 1:
        return unpacking(list(data.values()), as_seq)
    elif len(keys) > 0:
        return unpacking([data[fn] for k in keys for fn in fnmatch.filter(data, k)], as_seq)
    return list(data.values())


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

   def unpack(self, *keys, as_seq:bool=False, exception_on_missing_keys:bool=False):
        return unpack(self, *keys, as_seq=as_seq, exception_on_missing_keys=exception_on_missing_keys)


class ProxyListOfDicts(list):
   """ Extra helper class for the reply list of dicts """
   def flatten(self):
        return ProxyListOfDicts([flatten(d) for d in self])

   def unpack(self, *keys, as_seq:bool=False, exception_on_missing_keys:bool=False):
        return unpack(self, *keys, as_seq=as_seq, exception_on_missing_keys=exception_on_missing_keys)

   def with_actors(self):
        return dict(zip(self.actors, self))

