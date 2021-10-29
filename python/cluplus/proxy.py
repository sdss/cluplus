# -*- coding: utf-8 -*-
#
# @Author: Florian Briegel (briegel@mpia.de)
# @Date: 2021-08-18
# @Filename: proxy.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)

import asyncio
# import logging
import sys
from functools import partial
from itertools import chain
from typing import Callable, Optional
from enum import Enum
from inspect import getcoroutinelocals, iscoroutine
from clu import AMQPReply, BaseClient

from .exceptions import ProxyPartialInvokeException


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

    def send_command(self, *args,
                     callback: Optional[Callable[[AMQPReply], None]] = None,):
        """Sends a command to the actor.

        Returns the result of calling the client ``send_command()`` method
        with the actor and concatenated arguments as parameters. Note that
        in some cases the client ``send_command()`` method may be a coroutine
        function, in which case the returned coroutine needs to be awaited.

        Parameters
        ----------
        args
            Arguments to pass to the actor.
            They will be concatenated using spaces.

        """

        command = " ".join(map(str, args))

        return self.client.send_command(self.actor, command)


class Proxy(ProxyClient):
    """A proxy client with actor commands.

import uuid
from clu import AMQPClient, CommandStatus
from cluplus.proxy import Proxy, invoke, unpack

actor = "proto"

amqpc = AMQPClient(name=f"proxy-{uuid.uuid4().hex[:8]}")

proto = Proxy(amqpc, actor)
proto.start()

async def start_now(proto):
    await amqpc.start()
    await proto.start()
    await amqpc.stop()

amqpc.loop.run_until_complete(start_now(proto))

print(proto.ping())

async def start_ping(proto):
    await amqpc.start()
    print(await proto.ping())
    await amqpc.stop()

amqpc.loop.run_until_complete(start_ping(proto))

async def start_async_ping(proto):
    await amqpc.start()
    print(await proto.async_ping())
    await amqpc.stop()

amqpc.loop.run_until_complete(start_async_ping(proto))


invoke(proto.async_setEnabled(True, axis0=True),
       proto.async_gotoRaDecJ2000(10,20))


unpack(proto.ping())

a, a0, b0, *coord = unpack(invoke(proto.async_setEnabled(True, axis0=True),
                                  proto.async_gotoRaDecJ2000(10,20)))
try:
   proto.errPassAsError()
   
except Exception as ex:
   print(f"got: {ex}")

try:
   amqpc.loop.run_until_complete(invoke(proto.ping(async_mode=True),
                                        proto.async_version(),
                                        proto.async_errPassAsError()))
except Exception as ex:
   print(ex)

try:
    async def start_async_invoke():
        await amqpc.start()
        await invoke(proto.ping(),
                     proto.version(),
                     proto.errPassAsError())
        await amqpc.stop()
    amqpc.loop.run_until_complete(start_async_invoke())
except Exception as ex:
   print(ex)



    """
    
    __commands="__commands"
    __comkey="help"
    
    def __init__(self, client: BaseClient, actor: str):
        super().__init__(client, actor)

    def start(self):
        """Query and set actor commands."""
        def set_commands(commands):
            for c in commands:
                setattr(self, c, partial(self._hybrid_call_command, c))
                setattr(self, f"async_{c}", partial(self.call_command, c))
            
        async def start_async():
            commands = (await self.call_command(Proxy.__commands))[Proxy.__comkey]
            set_commands(commands)
            
        if self.client.loop.is_running():
            return start_async()
        else:
            coro=self._sync_call_command(Proxy.__commands)
            commands = self.client.loop.run_until_complete(coro)[Proxy.__comkey]
            set_commands(commands)

    async def _sync_call_command(self, command, *args, **kwargs):
        if not self.client.connection.connection or self.client.connection.connection.is_closed:
            await self.client.start()
        ret = await self.call_command(command, *args, **kwargs)
        await self.client.stop()
        return ret


    def _hybrid_call_command(self, command, *args, async_mode=False, **kwargs):
        if self.client.loop.is_running() or async_mode:
            return self.call_command(command, *args, **kwargs)
        else:
            return self.client.loop.run_until_complete(self._sync_call_command(command, *args, **kwargs))


    async def call_command(self,
                           command: str,
                           *args,
                           callback:
                               Optional[Callable[[AMQPReply], None]] = None,
                           **kwargs):

        opts = list(chain.from_iterable(('--' + k, v)
                                        for k, v in kwargs.items()))
        
        future = await self.client.send_command(self.actor,
                                                 command,
                                                 *args,
                                                 *opts,
                                                 callback=callback)

        ret = await future

        if hasattr(ret, "status") and ret.status.did_fail:
            raise self._errorMapToException(ret.replies[-1].body['error'])

        return ret.replies[-1].body

    @staticmethod
    def _errorMapToException(em: dict):
        return Proxy._stringToException(em['exception_message'],
                                        em['exception_type'],
                                        em['exception_module'])

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


def invoke(*cmds):
    """invokes one or many commands in parallel

    On error it throws an exception if one of the commands fails as a dict
    with an exception and return values for every command.
    """
    async def invoke_now(client, *cmds):
        if client:
            if not client.connection.connection or client.connection.connection.is_closed:
                await client.start()
        ret = await asyncio.gather(*[asyncio.create_task(cmd) for cmd in cmds], 
                                return_exceptions=True)
        if client:
            await client.stop()
        for r in ret:
            if isinstance(r, Exception):
                raise ProxyPartialInvokeException(ret)
        return ret


    first_coro=cmds[0]
    assert(iscoroutine(first_coro))

    client = getcoroutinelocals(first_coro)['self'].client
    loop = client.loop
    
    if loop.is_running():
        return invoke_now(None, *cmds)
    else:
        return loop.run_until_complete(invoke_now(client, *cmds))


def unpack(ret, *keys):
    """ unpacks every parameter from the body of the finish reply or list of replies.

        Pythons list unpacking mechanism PEP3132 can be used to assign the value(s)
        
        Be warned if you dont use it the correct way, 
        whould also be a good place to check the reply body format with schemas.

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
        if len(keys) > 1:
            return [d[i] for d in ret for i in keys if i in d]
        else:
            return [val for d in ret for val in list(d.values())]


    if len(ret) == 1:
        return list(ret.values())[0]
    elif len(keys) > 1:
        return [ret[i] for i in keys]
    else:
        return list(ret.values())
        

