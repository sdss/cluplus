# -*- coding: utf-8 -*-
#
# @Author: Florian Briegel (briegel@mpia.de)
# @Date: 2021-11-19
# @Filename: test_00_misc.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)

import pytest
import asyncio
import logging
import uuid

from clu import AMQPClient, CommandStatus

from cluplus import __version__
from cluplus.proxy import Proxy, unpack, flatten, ProxyDict, ProxyListOfDicts

from proto.actor.actor import ProtoActor


def test_proxy_string_to_exception():

    e = Proxy._stringToException("Unknown")
    assert(type(e) == Exception)

    e = Proxy._stringToException("Unknown", "NOMODULE")
    assert(type(e) == Exception)

    e = Proxy._stringToException("Unknown", "NOMODULE", "WRONGTYPE")
    assert(type(e) == Exception)


def test_proxy_null_unpack():

    assert(unpack({}) == None)

    
def test_proxy_single_unpack():

    data = {'a': 1}

    assert(unpack(data) == 1)
    assert(unpack(data, 'a') == 1)

    data = {'a': 1, 'b': 2, 'c': 3, 'd': 4}

    a, b, c, d = unpack(data)
    assert(a == 1)
    assert(b == 2)
    assert(c == 3)
    assert(d == 4)
    
    a, *b = unpack(data)
    assert(a == 1)
    assert(b == list(data.values())[1:])
    
    a, c = unpack(data, 'a', 'c')
    assert(a == 1)
    assert(c == 3)

    c, a = unpack(data, 'c', 'a')
    assert(a == 1)
    assert(c == 3)

    d = unpack(data, 'd')
    assert(d == 4)
    assert(unpack(data, 'b') == 2)

    data = ProxyDict(data)

    a, b, c, d = data.unpack()
    assert(a == 1)
    assert(b == 2)
    assert(c == 3)
    assert(d == 4)

    a, c = data.unpack('a', 'c')
    assert(a == 1)
    assert(c == 3)
    
    #c = data.unpack('c')
    #assert(c == 3)

def test_proxy_mult_unpack():

    data = [{'a': 1, 'b': 2, 'e': 7}, {'c': 3, 'd': 4, 'e': 8}]

    a, b, e1, c, d, e2  = unpack(data)
    assert(a == 1)
    assert(b == 2)
    assert(c == 3)
    assert(d == 4)
    assert(e1 == 7)
    assert(e2 == 8)
    
    a, c = unpack(data, 'a', 'c')
    assert(a == 1)
    assert(c == 3)

    a, e1, e2 = unpack(data, 'a', 'e')
    assert(a == 1)
    assert(e1 == 7)
    assert(e2 == 8)

    e1, e2 = unpack(data, 'e')
    assert(e1 == 7)
    assert(e2 == 8)
    
    try:
        e2 = unpack(data, 'f')

    except KeyError as ex:
        assert(ex.args[0] == ['f'])

    except Exception as ex:
        pytest.fail(f"... should not have reached this point {ex}")

    data = ProxyListOfDicts(data)
        
    a, b, e1, c, d, e2  = data.unpack()
    assert(a == 1)
    assert(b == 2)
    assert(c == 3)
    assert(d == 4)
    assert(e1 == 7)
    assert(e2 == 8)
    

def test_proxy_single_seq_unpack():

    data = {'a': 1}

    assert(unpack(data, as_seq=True) == [1])
    assert(unpack(data, 'a', as_seq=True) == [1])


def test_proxy_wildcard_unpack():

    data = {"east.filename": "/bla", "kkk": 2, "west.filename": "/foo", "jjj": 3, "north.filename": "/bar"}

    a = unpack(data, '*.filename')
    assert(a == ["/bla", "/foo", "/bar"])


    data = [{"east.filename": "/bla", "kkk": 2, "west.filename": "/foo", "jjj": 3}, {"north.filename": "/bar"}]

    a = unpack(data, '*.filename')
    assert(a == ["/bla", "/foo", "/bar"])

def test_proxy_flatten():
    data = {'a': 1, 'b': 2, 'e': {'c': 3, 'd': 4, 'e': 8}}
    assert(flatten(data) == {'a': 1, 'b': 2, 'e.c': 3, 'e.d': 4, 'e.e': 8})

    data = ProxyDict(data)
    assert(data.flatten() == {'a': 1, 'b': 2, 'e.c': 3, 'e.d': 4, 'e.e': 8})

    data = ProxyListOfDicts([data, data])
    assert(data.flatten()[1] == {'a': 1, 'b': 2, 'e.c': 3, 'e.d': 4, 'e.e': 8})
