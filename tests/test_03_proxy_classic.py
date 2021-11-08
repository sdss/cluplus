#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @Author: José Sánchez-Gallego (gallegoj@uw.edu)
# @Date: 2020-08-26
# @Filename: proto_proxy.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)

import pytest

import logging
from time import sleep

from clu import AMQPClient, CommandStatus

from cluplus import __version__
from cluplus.proxy import Proxy, invoke, unpack

from proto.actor.actor import ProtoActor


def test_proxy_classic_single_basic(proto_test_actor):

    amqp_client = AMQPClient(name=f"{proto_test_actor.name}_client")

    proto_proxy = Proxy(amqp_client, proto_test_actor.name)
    proto_proxy.start()

    assert (proto_proxy.ping() == {'text': 'Pong.'})
    
    assert (proto_proxy.setEnabled(True) == {'enable': True, 'axis0': True, 'axis1': True} )

    assert (proto_proxy.setEnabled(False, axis0=True) == {'enable': False, 'axis0': True, 'axis1': True} )


def test_proxy_classic_single_callback(proto_test_actor):

    amqp_client = AMQPClient(name=f"{proto_test_actor.name}_client")
    proto_proxy = Proxy(amqp_client, proto_test_actor.name)
    proto_proxy.start()
    
    def callback(reply): 
        amqp_client.log.debug(f"Reply: {CommandStatus.code_to_status(reply.message_code)} {reply.body}")
        if CommandStatus.code_to_status(reply.message_code) == CommandStatus.DONE:
             assert (reply.body == {'enable': True, 'axis0': True, 'axis1': True} )
    
    assert (proto_proxy.setEnabled(True, callback=callback) == {'enable': True, 'axis0': True, 'axis1': True} )


def test_proxy_classic_single_unpack(proto_test_actor):

    amqp_client = AMQPClient(name=f"{proto_test_actor.name}_client")
    proto_proxy = Proxy(amqp_client, proto_test_actor.name)
    proto_proxy.start()
    
    assert (unpack(proto_proxy.ping()) == 'Pong.')

    a, b, c = unpack(proto_proxy.setEnabled(False))
    assert ([a, b, c] == [False, True, True])


def test_proxy_classic_multiple_basic(proto_test_actor):

    amqp_client = AMQPClient(name=f"{proto_test_actor.name}_client")
    proto_proxy = Proxy(amqp_client, proto_test_actor.name)
    proto_proxy.start()

    rc = invoke(proto_proxy.async_setEnabled(True, axis0=True),
                proto_proxy.async_gotoRaDecJ2000(10,20))
    assert (rc == [{'enable': True, 'axis0': True, 'axis1': True}, {'ra_h': 10.0, 'deg_d': 20.0}])


def test_proxy_classic_multiple_unpack(proto_test_actor):

    amqp_client = AMQPClient(name=f"{proto_test_actor.name}_client")
    proto_proxy = Proxy(amqp_client, proto_test_actor.name)
    proto_proxy.start()

    rc = unpack(invoke(proto_proxy.async_setEnabled(True, axis0=True),
                             proto_proxy.async_gotoRaDecJ2000(10,20)))
    assert (rc == [True, True, True, 10.0, 20.0])

    a, a0, a1, *c = unpack(invoke(proto_proxy.async_setEnabled(True, axis0=True),
                                  proto_proxy.async_gotoRaDecJ2000(10,20)))

    assert ([a, a0, a1, c] == [True, True, True, [10.0, 20.0]])



def test_proxy_classic_exception_single_command(proto_test_actor):

    from proto.actor.exceptions import ProtoActorAPIError
    from pydoc import getdoc
    
    amqp_client = AMQPClient(name=f"{proto_test_actor.name}_client")
    proto_proxy = Proxy(amqp_client, proto_test_actor.name)
    proto_proxy.start()

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
        proto_proxy.errPassAsError(callback=callback)

    except Exception as ex:
        assert(isinstance(ex, ProtoActorAPIError))
        return

    pytest.fail("... should not have reached this point")


def test_proxy_classic_exception_multiple_invoke(proto_test_actor):

    amqp_client = AMQPClient(name=f"{proto_test_actor.name}_client")
    from cluplus.exceptions import ProxyPartialInvokeException
    from proto.actor.exceptions import ProtoActorAPIError

    proto_proxy = Proxy(amqp_client, proto_test_actor.name)
    proto_proxy.start()

    try:
        invoke(proto_proxy.async_ping(),
                     proto_proxy.async_version(),
                     proto_proxy.async_errPassAsError())

    except ProxyPartialInvokeException as ex:
        assert(isinstance(ex, ProxyPartialInvokeException))
        ping, version, errPassAsError = ex.args
        assert(ping['text'] == 'Pong.')
        assert(version['version'] != '?')
        assert(isinstance(errPassAsError, ProtoActorAPIError))
        return

    pytest.fail("... should not have reached this point")


def test_proxy_classic_single_callback(proto_test_actor):

    amqp_client = AMQPClient(name=f"{proto_test_actor.name}_client")
    proto_proxy = Proxy(amqp_client, proto_test_actor.name)
    proto_proxy.start()
    
    assert(len(proto_proxy.foo()["help"]) > 0)



