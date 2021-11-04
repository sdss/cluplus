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

from clu import AMQPClient, CommandStatus

from cluplus import __version__
from cluplus.proxy import Proxy, invoke, unpack
from cluplus.parsers.json import pickle, unpickle

from proto.actor.actor import ProtoActor


import numpy as np


@pytest.fixture
async def amqp_client(proto_test_actor, event_loop):

    client = AMQPClient(name=f"{proto_test_actor.name}_client-{uuid.uuid4().hex[:8]}")
    await client.start()

    yield client

    await client.stop()


@pytest.mark.asyncio
async def test_proxy_json_simple(amqp_client, proto_test_actor):

    proto_proxy = Proxy(amqp_client, proto_test_actor.name)
    await proto_proxy.start()

    bright = np.rec.array([(1,'Sirius', -1.45, 'A1V'),
                        (2,'Canopus', -0.73, 'F0Ib'),
                        (3,'Rigil Kent', -0.1, 'G2V')],
                        formats='int16,a20,float32,a10',
                        names='order,name,mag,Sp')


    a = pickle(bright)
    bright_copy = unpickle(a)
    assert((bright == bright_copy).all())

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

    a, b = pickle(bright, bright)
    assert(a == b)

    try:
        ret = await proto_proxy.moreBigData(*pickle(bright, bright), 4711)
        #print(ret)
    
    except Exception as ex:
        raise Exception(f"Something went wrong: {ex}")
