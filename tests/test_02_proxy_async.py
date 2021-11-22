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
async def async_amqp_client(proto_test_actor):

    client = AMQPClient(name=f"{proto_test_actor.name}_client-{uuid.uuid4().hex[:8]}")
    await client.start()

    yield client

    await client.stop()


@pytest.fixture(scope="session")
async def async_proto_proxy(async_amqp_client, proto_test_actor):

    proxy = Proxy(async_amqp_client, proto_test_actor.name)
    await proxy.start()

    yield proxy


@pytest.mark.asyncio
async def test_proxy_async_single_basic(async_proto_proxy):

    assert (await async_proto_proxy.ping() == {'text': 'Pong.'})
    
    assert (await async_proto_proxy.setEnabled(True) == {'enable': True, 'axis0': True, 'axis1': True} )

    assert (await async_proto_proxy.setEnabled(False, axis0=True) == {'enable': False, 'axis0': True, 'axis1': True} )


@pytest.mark.asyncio
async def test_proxy_async_single_callback(async_proto_proxy):

    def callback(reply): 
#        async_amqp_client.log.warning(f"Reply: {CommandStatus.code_to_status(reply.message_code)} {reply.body}")
        if CommandStatus.code_to_status(reply.message_code) == CommandStatus.DONE:
             assert (reply.body == {'enable': True, 'axis0': True, 'axis1': True} )
    
    assert (await async_proto_proxy.setEnabled(True, callback=callback) == {'enable': True, 'axis0': True, 'axis1': True} )


@pytest.mark.asyncio
async def test_proxy_async_single_unpack(async_proto_proxy):

    assert (unpack(await async_proto_proxy.ping()) == 'Pong.')

    a, b, c = unpack(await async_proto_proxy.setEnabled(False))
    assert ([a, b, c] == [False, True, True])


@pytest.mark.asyncio
async def test_proxy_async_multiple_basic(async_proto_proxy):

    rc = await invoke(async_proto_proxy.setEnabled(True, axis0=True),
                      async_proto_proxy.gotoRaDecJ2000(10,20))
    assert (rc == [{'enable': True, 'axis0': True, 'axis1': True}, {'ra_h': 10.0, 'deg_d': 20.0}])


@pytest.mark.asyncio
async def test_proxy_async_multiple_unpack(async_proto_proxy):

    rc = unpack(await invoke(async_proto_proxy.setEnabled(True, axis0=True),
                             async_proto_proxy.gotoRaDecJ2000(10,20)))
    assert (rc == [True, True, True, 10.0, 20.0])

    a, a0, a1, *c = unpack(await invoke(async_proto_proxy.setEnabled(True, axis0=True),
                             async_proto_proxy.gotoRaDecJ2000(10,20)))

    assert ([a, a0, a1, c] == [True, True, True, [10.0, 20.0]])


@pytest.mark.asyncio
async def test_proxy_async_exception_single_command(async_proto_proxy):

    from proto.actor.exceptions import ProtoActorAPIError
    
    try:
        await async_proto_proxy.errPassAsError()

    except Exception as ex:
        assert(isinstance(ex, ProtoActorAPIError))
        return

    pytest.fail("... should not have reached this point")


@pytest.mark.asyncio
async def test_proxy_async_exception_multiple_invoke(async_proto_proxy):

    from cluplus.exceptions import ProxyPartialInvokeException
    from proto.actor.exceptions import ProtoActorAPIError

    try:
        await invoke(async_proto_proxy.ping(),
                     async_proto_proxy.version(),
                     async_proto_proxy.errPassAsError())

    except ProxyPartialInvokeException as ex:
        assert(isinstance(ex, ProxyPartialInvokeException))
        ping, version, errPassAsError = ex.args
        assert(ping['text'] == 'Pong.')
        assert(version['version'] != '?')
        assert(isinstance(errPassAsError, ProtoActorAPIError))
        return

    pytest.fail("... should not have reached this point")
