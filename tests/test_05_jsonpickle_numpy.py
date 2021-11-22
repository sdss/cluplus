#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @Author: Florian Briegel (briegel@mpia.de)
# @Date: 2021-11-19
# @Filename: test_04_numpy.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)

import pytest
import asyncio
import logging
import uuid

from clu import AMQPClient, CommandStatus

from cluplus import __version__
from cluplus.proxy import Proxy, invoke, unpack
from cluplus.parsers.jsonpickle import pickle, unpickle, JsonPickleParamType

from proto.actor.actor import ProtoActor

import numpy as np


@pytest.fixture(scope="session")
async def amqp_client(proto_test_actor, event_loop):

    client = AMQPClient(name=f"{proto_test_actor.name}_client-{uuid.uuid4().hex[:8]}")
    await client.start()

    yield client

    await client.stop()


def test_proxy_json_paramtype():

    import click
    
    bright = np.rec.array([(1,'Sirius', -1.45, 'A1V'),
                        (2,'Canopus', -0.73, 'F0Ib'),
                        (3,'Rigil Kent', -0.1, 'G2V')],
                        formats='int16,a20,float32,a10',
                        names='order,name,mag,Sp')

    j = JsonPickleParamType()
    j.convert(pickle(bright)[1:-1], None, None)
    
    
    try:
        j = JsonPickleParamType()
        j.convert("not valid !", None, None)
        
    except click.exceptions.BadParameter as e:
        return
    
    pytest.fail("... should not have reached this point")


def test_pickle_unpickle():

    bright = np.rec.array([(1,'Sirius', -1.45, 'A1V'),
                        (2,'Canopus', -0.73, 'F0Ib'),
                        (3,'Rigil Kent', -0.1, 'G2V')],
                        formats='int16,a20,float32,a10',
                        names='order,name,mag,Sp')

    a = pickle(bright)
    bright_copy = unpickle(a)
    assert((bright == bright_copy).all())

    a, b = pickle(bright, bright)
    assert(a == b)
    
    aa, bb = unpickle(a, b)
    assert((aa == bb).all())


@pytest.mark.asyncio
async def test_proxy_json_simple(amqp_client, proto_test_actor):

    proto_proxy = Proxy(amqp_client, proto_test_actor.name)
    await proto_proxy.start()

    bright = np.rec.array([(1,'Sirius', -1.45, 'A1V'),
                        (2,'Canopus', -0.73, 'F0Ib'),
                        (3,'Rigil Kent', -0.1, 'G2V')],
                        formats='int16,a20,float32,a10',
                        names='order,name,mag,Sp')

    try:
        bright_ret = unpickle(unpack(await proto_proxy.bigData(pickle(bright))))
        assert((bright == bright_ret).all())
    
    except Exception as ex:
        raise Exception(f"Something went wrong: {ex}")


@pytest.mark.asyncio
async def test_proxy_json_multiple(amqp_client, proto_test_actor):

    proto_proxy = Proxy(amqp_client, proto_test_actor.name)
    await proto_proxy.start()

    bright = np.rec.array([(1,'Sirius', -1.45, 'A1V'),
                        (2,'Canopus', -0.73, 'F0Ib'),
                        (3,'Rigil Kent', -0.1, 'G2V')],
                        formats='int16,a20,float32,a10',
                        names='order,name,mag,Sp')

    try:
        ret = await proto_proxy.moreBigData(*pickle(bright, bright), 4711)
        #print(ret)
    
    except Exception as ex:
        raise Exception(f"Something went wrong: {ex}")


@pytest.mark.asyncio
async def test_proxy_json_numpy_array(amqp_client, proto_test_actor):

    proto_proxy = Proxy(amqp_client, proto_test_actor.name)
    await proto_proxy.start()

    arr = np.vander(np.linspace(0, 1, 1200), 2)
    a = pickle(arr)
    arr_copy = unpickle(a)
    assert((arr == arr_copy).all())

    try:
        arr_ret = unpickle(unpack(await proto_proxy.bigData(pickle(arr))))
        assert((arr == arr_ret).all())
    
    except Exception as ex:
        raise Exception(f"Something went wrong: {ex}")

