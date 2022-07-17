# -*- coding: utf-8 -*-
#
## @Author: Florian Briegel (briegel@mpia.de)
# @Date: 2021-11-19
# @Filename: test_02_proxy_async.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)


import pytest
import asyncio
import logging
import uuid
from time import sleep

from clu import AMQPClient, CommandStatus

from cluplus import __version__
from cluplus.proxy import Proxy, invoke, unpack
from cluplus.exceptions import ProxyActorIsNotReachableException

@pytest.mark.asyncio
async def test_proxy_exception_to_map():
    
    em = Proxy._exceptionToMap(ProxyActorIsNotReachableException())
    assert  (em['exception_module'] == 'cluplus.exceptions')
    assert  (em['exception_type'] == 'ProxyActorIsNotReachableException')
    assert  (em['exception_message'] == '')


@pytest.mark.asyncio
async def test_proxy_async_default_amqpc(proto_test_actor):

    Proxy.setDefaultAmqpc(AMQPClient(name=f"{proto_test_actor.name}_client2-{uuid.uuid4().hex[:8]}"))
    
    proxy = await Proxy(proto_test_actor.name).start()

    assert (await proxy.ping() == {'text': 'Pong.'})
    
    

@pytest.mark.asyncio
async def test_proxy_async_single_basic(proto_test_actor):

    proxy = await Proxy("nonexistant").start()
    try:
        await proxy.ping()
       
    except Exception as ex:
        await asyncio.sleep(0.2)
        return

    pytest.fail("... should not have reached this point")


    
@pytest.mark.asyncio
async def proto_test_delayed_actor(event_loop):

    Proxy.__pull_commands_delay = 0.1

    actor2 = ProtoActor(name=f"proto_delayed-{uuid.uuid4().hex[:8]}")

    proxy = await Proxy(actor2.name).start()

    await asyncio.sleep(0.3)
    assert(proxy.hasattr(self, "__pull_commands_task"))
    await proxy.stop()
    assert(not proxy.hasattr(self, "__pull_commands_task"))

    await proxy.start()
    assert(proxy.hasattr(self, "__pull_commands_task"))
    
    await actor2.start()
   
    await asyncio.sleep(0.2)
    assert(not proxy.hasattr(self, "__pull_commands_task"))

    await proxy.help()
    assert(not proxy.hasattr(self, "__pull_commands_task"))

