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


@pytest.fixture(scope="session")
async def async_proto_proxy(proto_test_actor):

    Proxy.setDefaultAmqpc(AMQPClient(name=f"{proto_test_actor.name}_client2-{uuid.uuid4().hex[:8]}"))

    proxy = Proxy(proto_test_actor.name)
    await proxy.start()

    yield proxy


@pytest.mark.asyncio
async def test_proxy_async_single_basic(async_proto_proxy):

    assert (await async_proto_proxy.ping() == {'text': 'Pong.'})
    


@pytest.mark.asyncio
async def test_proxy_async_single_basic(proto_test_actor):

    proxy = await Proxy("nonexistant").start()
    try:
       await proxy.ping()
       
    except Exception as ex:
        return

    pytest.fail("... should not have reached this point")
