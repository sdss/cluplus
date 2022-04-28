# -*- coding: utf-8 -*-
#
# @Author: Florian Briegel (briegel@mpia.de)
# @Date: 2021-11-19
# @Filename: test_03_proxy_classic.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)


import pytest
import uuid

import logging
from time import sleep

from clu import AMQPClient, CommandStatus

from cluplus import __version__
from cluplus.proxy import Proxy, invoke, unpack

from proto.actor.actor import ProtoActor


@pytest.fixture(scope="session")
def classic_proto_proxy(proto_test_actor):

    client = AMQPClient(name=f"{proto_test_actor.name}_client-{uuid.uuid4().hex[:8]}")

    proxy = Proxy(client, proto_test_actor.name).start()

    yield proxy


def test_proxy_classic_single_basic(classic_proto_proxy):

    assert (classic_proto_proxy.ping() == {'text': 'Pong.'})
    
    assert (classic_proto_proxy.setEnabled(True) == {'enable': True, 'axis0': True, 'axis1': True} )

    assert (classic_proto_proxy.setEnabled(False, axis0=True) == {'enable': False, 'axis0': True, 'axis1': True} )


def test_proxy_classic_single_callback(classic_proto_proxy):

    def callback(reply): 
        amqp_client.log.debug(f"Reply: {CommandStatus.code_to_status(reply.message_code)} {reply.body}")
        if CommandStatus.code_to_status(reply.message_code) == CommandStatus.DONE:
             assert (reply.body == {'enable': True, 'axis0': True, 'axis1': True} )
    
    assert (classic_proto_proxy.setEnabled(True, callback=callback) == {'enable': True, 'axis0': True, 'axis1': True} )


def test_proxy_classic_single_unpack(classic_proto_proxy):

    assert (unpack(classic_proto_proxy.ping()) == 'Pong.')

    a, b, c = unpack(classic_proto_proxy.setEnabled(False))
    assert ([a, b, c] == [False, True, True])


def test_proxy_classic_multiple_basic(classic_proto_proxy):

    rc = invoke(classic_proto_proxy.async_setEnabled(True, axis0=True),
                classic_proto_proxy.async_gotoRaDecJ2000(10,20))
    assert (rc == [{'enable': True, 'axis0': True, 'axis1': True}, {'ra_h': 10.0, 'deg_d': 20.0}])


def test_proxy_classic_multiple_unpack(classic_proto_proxy):

    rc = unpack(invoke(classic_proto_proxy.async_setEnabled(True, axis0=True),
                             classic_proto_proxy.async_gotoRaDecJ2000(10,20)))
    assert (rc == [True, True, True, 10.0, 20.0])

    a, a0, a1, *c = unpack(invoke(classic_proto_proxy.async_setEnabled(True, axis0=True),
                                  classic_proto_proxy.async_gotoRaDecJ2000(10,20)))

    assert ([a, a0, a1, c] == [True, True, True, [10.0, 20.0]])



def test_proxy_classic_exception_single_command(classic_proto_proxy):

    from proto.actor.exceptions import ProtoActorAPIError
    from pydoc import getdoc
    
    def callback(reply): 

        if CommandStatus.code_to_status(reply.message_code) == CommandStatus.RUNNING:
            return
        if CommandStatus.code_to_status(reply.message_code) == CommandStatus.FAILED:
            error=reply.body["error"]
            assert(error["exception_module"] == 'proto.actor.exceptions')
            assert(error["exception_type"] == 'ProtoActorAPIError')
            assert(error["exception_message"] == '')
            assert(getdoc(ProtoActorAPIError) == 'A custom exception for API errors')
        else:
            pytest.fail(f"... returned wrong commandstatus: {CommandStatus.code_to_status(reply.message_code)}")
    
    try:
        classic_proto_proxy.errPassAsError(callback=callback)

    except Exception as ex:
        assert(isinstance(ex, ProtoActorAPIError))
        return

    pytest.fail("... should not have reached this point")


def test_proxy_classic_exception_multiple_invoke(classic_proto_proxy):

    from cluplus.exceptions import ProxyPartialInvokeException
    from proto.actor.exceptions import ProtoActorAPIError

    try:
        invoke(classic_proto_proxy.async_ping(),
                     classic_proto_proxy.async_version(),
                     classic_proto_proxy.async_errPassAsError())

    except ProxyPartialInvokeException as ex:
        assert(isinstance(ex, ProxyPartialInvokeException))
        ping, version, errPassAsError = ex.args
        assert(ping['text'] == 'Pong.')
        assert(version['version'] != '?')
        assert(isinstance(errPassAsError, ProtoActorAPIError))
        return

    pytest.fail("... should not have reached this point")


def test_proxy_classic_single_callback(classic_proto_proxy):

    assert(len(classic_proto_proxy.foo()["help"]) > 0)


def test_proxy_classic_constructor(classic_proto_proxy):

    try:
        Proxy()

    except TypeError as ex:
        
        try:
            Proxy(7)

        except TypeError as ex:
            
            try:
                Proxy(AMQPClient(name="none"))

            except TypeError as ex:
                return

    pytest.fail("... should not have reached this point")


