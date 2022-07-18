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
from cluplus.proxy import Proxy

from proto.actor.actor import ProtoActor

@pytest.mark.asyncio
async def test_proxy_async_delayed(event_loop):

    Proxy.pull_commands_delay = 0.1

    actor = ProtoActor(name=f"proto_delayed-{uuid.uuid4().hex[:8]}")

    proxy = await Proxy(actor.name).start()

    assert(hasattr(proxy, "_pull_commands_task"))

    await proxy.stop()
    assert(not hasattr(proxy, "_pull_commands_task"))

    await proxy.start()
    assert(hasattr(proxy, "_pull_commands_task"))
    
    await actor.start()
   
    await asyncio.sleep(0.1)
    assert(not hasattr(proxy, "_pull_commands_task"))

    await proxy.help()
    assert(not hasattr(proxy, "_pull_commands_task"))

    await proxy.stop()

    await actor.stop()
