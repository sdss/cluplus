#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @Author: Florian Briegel (briegel@mpia.de)
# @Date: 2021-11-19
# @Filename: test_06_jsonstring.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)


import pytest
import asyncio
import logging
import uuid

from clu import AMQPClient, CommandStatus

from cluplus import __version__
from cluplus.proxy import Proxy, invoke, unpack
#from cluplus.parsers.jsonstring import pickle, unpickle, JsonStringParamType

from proto.actor.actor import ProtoActor
from proto.actor.commands.complex_data_with_jsonstring import fits_dict, list_data, dict_data, mixed_data


@pytest.fixture(scope="session")
async def amqp_client(proto_test_actor, event_loop):

    client = AMQPClient(name=f"{proto_test_actor.name}_client-{uuid.uuid4().hex[:8]}")
    await client.start()

    yield client

    await client.stop()


def test_proxy_jsonstring():
    import json

    x0 = ["Hello' there", 'Rigil " Kent', 'C', 3, 0.815, {'D': 4711, 'e': '88'}]

    a = f"'{json.dumps(x0)}'"

    x1 = json.loads(a[1:-1])

    assert(x0==x1)

def test_proxy_jsonstring2():
    import json

    a = f"'{json.dumps(fits_dict)}'"
    fd1 = json.loads(a[1:-1])
    assert(fits_dict == fd1)
    
    a = f"'{json.dumps(list_data)}'"
    fd1 = json.loads(a[1:-1])
    assert(list_data == fd1)
    
    a = f"'{json.dumps(dict_data)}'"
    fd1 = json.loads(a[1:-1])
    assert(dict_data == fd1)
    
    a = f"'{json.dumps(mixed_data)}'"
    fd1 = json.loads(a[1:-1])
    assert(mixed_data == fd1)
    
    

@pytest.mark.asyncio
async def test_proxy_json_list_and_dict(amqp_client, proto_test_actor):

    proto_proxy = Proxy(proto_test_actor.name, amqpc=amqp_client)
    await proto_proxy.start()
    
    try:
        await proto_proxy.sendData(list_data, dict_data, mixed_data)
        return
    
    except Exception as ex:
        pytest.fail("... should not have reached this point: {ex}" )


@pytest.mark.asyncio
async def test_proxy_json_fits(amqp_client, proto_test_actor):

    proto_proxy = Proxy(proto_test_actor.name, amqpc=amqp_client)
    await proto_proxy.start()
    
    try:
        await proto_proxy.fitsStyleData(fits_dict)
        return
    
    except Exception as ex:
        pytest.fail("... should not have reached this point: {ex}" )


@pytest.mark.asyncio
async def test_proxy_json_fits_with_opt(amqp_client, proto_test_actor):

    proto_proxy = Proxy(proto_test_actor.name, amqpc=amqp_client)
    await proto_proxy.start()
    
    try:
        await proto_proxy.fitsStyleData(fits_dict, optData=[fits_dict, 4711, "Hello world"])
        return
    
    except Exception as ex:
        pytest.fail("... should not have reached this point: {ex}" )


@pytest.mark.asyncio
async def test_proxy_json_bogus(amqp_client, proto_test_actor):
    ''' clu doesnt handle click parser errors coreectly'''


    proto_proxy = Proxy(proto_test_actor.name, amqpc=amqp_client)
    await proto_proxy.start()
    
    try:
        await proto_proxy.fitsStyleData("bogus data")
    
    except Exception as ex:
        return

    pytest.fail("... should not have reached this point")

