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
from cluplus.proxy import Proxy, unpack

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


def test_proxy_mult_unpack():

    data = [{'a': 1, 'b': 2}, {'c': 3, 'd': 4}]

    a, b, c, d = unpack(data)
    assert(a == 1)
    assert(b == 2)
    assert(c == 3)
    assert(d == 4)
    
    a, c = unpack(data, 'a', 'c')
    assert(a == 1)
    assert(c == 3)

