#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @Author: José Sánchez-Gallego (gallegoj@uw.edu)
# @Date: 2020-08-26
# @Filename: proto_proxy.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)

import pytest
import asyncio
import logging
import uuid
from time import sleep

from clu import AMQPClient, CommandStatus

from cluplus import __version__
from cluplus.proxy import Proxy, invoke, unpack


@pytest.fixture
async def amqp_client(proto_test_actor, event_loop):

    client = AMQPClient(name=f"{proto_test_actor.name}_client-{uuid.uuid4().hex[:8]}")
    await client.start()

    yield client

    await client.stop()


@pytest.mark.asyncio
async def test_proxy_async_single_basic(amqp_client, proto_test_actor):

    proto_proxy = Proxy(amqp_client, proto_test_actor.name)
    await proto_proxy.start()
    
    assert (await proto_proxy.ping() == {'text': 'Pong.'})
    
    assert (await proto_proxy.setEnabled(True) == {'enable': True, 'axis0': True, 'axis1': True} )

    assert (await proto_proxy.setEnabled(False, axis0=True) == {'enable': False, 'axis0': True, 'axis1': True} )


@pytest.mark.asyncio
async def test_proxy_async_single_callback(amqp_client, proto_test_actor):

    proto_proxy = Proxy(amqp_client, proto_test_actor.name)
    await proto_proxy.start()
    
    def callback(reply): 
#        amqp_client.log.warning(f"Reply: {CommandStatus.code_to_status(reply.message_code)} {reply.body}")
        if CommandStatus.code_to_status(reply.message_code) == CommandStatus.DONE:
             assert (reply.body == {'enable': True, 'axis0': True, 'axis1': True} )
    
    assert (await proto_proxy.setEnabled(True, callback=callback) == {'enable': True, 'axis0': True, 'axis1': True} )


@pytest.mark.asyncio
async def test_proxy_async_single_unpack(amqp_client, proto_test_actor):

    proto_proxy = Proxy(amqp_client, proto_test_actor.name)
    await proto_proxy.start()
    
    assert (unpack(await proto_proxy.ping()) == 'Pong.')

    a, b, c = unpack(await proto_proxy.setEnabled(False))
    assert ([a, b, c] == [False, True, True])


@pytest.mark.asyncio
async def test_proxy_async_multiple_basic(amqp_client, proto_test_actor):

    proto_proxy = Proxy(amqp_client, proto_test_actor.name)
    await proto_proxy.start()

    rc = await invoke(proto_proxy.setEnabled(True, axis0=True),
                      proto_proxy.gotoRaDecJ2000(10,20))
    assert (rc == [{'enable': True, 'axis0': True, 'axis1': True}, {'ra_h': 10.0, 'deg_d': 20.0}])


@pytest.mark.asyncio
async def test_proxy_async_multiple_unpack(amqp_client, proto_test_actor):

    proto_proxy = Proxy(amqp_client, proto_test_actor.name)
    await proto_proxy.start()

    rc = unpack(await invoke(proto_proxy.setEnabled(True, axis0=True),
                             proto_proxy.gotoRaDecJ2000(10,20)))
    assert (rc == [True, True, True, 10.0, 20.0])

    a, a0, a1, *c = unpack(await invoke(proto_proxy.setEnabled(True, axis0=True),
                             proto_proxy.gotoRaDecJ2000(10,20)))

    assert ([a, a0, a1, c] == [True, True, True, [10.0, 20.0]])


@pytest.mark.asyncio
async def test_proxy_async_exception_single_command(amqp_client, proto_test_actor):

    from proto.actor.exceptions import ProtoActorAPIError
    
    proto_proxy = Proxy(amqp_client, proto_test_actor.name)
    await proto_proxy.start()

    try:
        await proto_proxy.errPassAsError()

    except Exception as ex:
        assert(isinstance(ex, ProtoActorAPIError))
        return

    pytest.fail("... should not have reached this point")


@pytest.mark.asyncio
async def test_proxy_async_exception_multiple_invoke(amqp_client, proto_test_actor):

    from cluplus.exceptions import ProxyPartialInvokeException
    from proto.actor.exceptions import ProtoActorAPIError

    proto_proxy = Proxy(amqp_client, proto_test_actor.name)
    await proto_proxy.start()

    try:
        await invoke(proto_proxy.ping(),
                     proto_proxy.version(),
                     proto_proxy.errPassAsError())

    except ProxyPartialInvokeException as ex:
        assert(isinstance(ex, ProxyPartialInvokeException))
        ping, version, errPassAsError = ex.args
        assert(ping['text'] == 'Pong.')
        assert(version['version'] != '?')
        assert(isinstance(errPassAsError, ProtoActorAPIError))
        return

    pytest.fail("... should not have reached this point")
