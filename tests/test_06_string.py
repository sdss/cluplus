# -*- coding: utf-8 -*-
#
# @Author: Florian Briegel (briegel@mpia.de)
# @Date: 2021-11-19
# @Filename: test_05_jsonpickle_numpy.py
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

import hashlib

@pytest.fixture(scope="session")
async def amqp_client(proto_test_actor, event_loop):

    client = AMQPClient(name=f"{proto_test_actor.name}_client-{uuid.uuid4().hex[:8]}")
    await client.start()

    yield client

    await client.stop()


@pytest.fixture(scope="session")
async def proto_proxy(amqp_client, proto_test_actor):

    proxy = Proxy(amqp_client, proto_test_actor.name)
    await proxy.start()

    yield proxy


@pytest.mark.asyncio
async def test_proxy_string_plain(amqp_client, proto_proxy):

    try:
        st="jjjj"
        await proto_proxy.stringTest(st, hashlib.md5(st.encode()).hexdigest())
        
        # this string will be quoted internally.
        st="Lorem ipsum dolor sit amet, consectetur adipisici elit, …"
        await proto_proxy.stringTest(st, hashlib.md5(st.encode()).hexdigest())
        
        # this string will be quoted internally.
        st='Lorem ipsum dolor sit amet, consectetur adipisici elit, …'
        await proto_proxy.stringTest(st, hashlib.md5(st.encode()).hexdigest())
        
        
    except Exception as ex:
        pytest.fail(f"... should not have reached this point {ex}")


@pytest.mark.asyncio
async def test_proxy_string_with_quotes(amqp_client, proto_proxy):

    try:
        st="°#~ !% '"
        await proto_proxy.stringTest(st, hashlib.md5(st.encode()).hexdigest())
        
        st='°#~ !% "'
        await proto_proxy.stringTest(st, hashlib.md5(st.encode()).hexdigest())
        
        st='°#~ !% \' " '
        await proto_proxy.stringTest(st, hashlib.md5(st.encode()).hexdigest())
        
        st="°#~ !% \" ' "
        await proto_proxy.stringTest(st, hashlib.md5(st.encode()).hexdigest())
        
        st=""" °#~ !% " ' """
        await proto_proxy.stringTest(st, hashlib.md5(st.encode()).hexdigest())
        
    except Exception as ex:
        pytest.fail(f"... should not have reached this point {ex}")



@pytest.mark.asyncio
async def test_proxy_string_user_quoted(amqp_client, proto_proxy):

    try:
        # quoted strings are not quoted again and on the actor side they are removed from the click parser,
        # shoudlnt be done, only for backward compatibility
        st="'Lorem ipsum dolor sit amet, consectetur adipisici elit, …'"
        await proto_proxy.stringTest(st, hashlib.md5(st[1:-1].encode()).hexdigest())
        
        st='"Lorem ipsum dolor sit amet, consectetur adipisici elit, …"'
        await proto_proxy.stringTest(st, hashlib.md5(st[1:-1].encode()).hexdigest())
        
        st='"!% \'"'
        await proto_proxy.stringTest(st, hashlib.md5(st[1:-1].encode()).hexdigest())
        
    except Exception as ex:
        pytest.fail(f"... should not have reached this point {ex}")

