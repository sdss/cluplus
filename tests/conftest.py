# encoding: utf-8
#
# conftest.py

"""
Here you can add fixtures that will be used for all the tests in this
directory. You can also add conftest.py files in underlying subdirectories.
Those conftest.py will only be applies to the tests in that subdirectory and
underlying directories. See https://docs.pytest.org/en/2.7.3/plugins.html for
more information.
"""

import asyncio
import os
import pathlib

import pytest

from proto.actor.actor import ProtoActor


@pytest.fixture
async def proto_test_actor(event_loop):

    actor = ProtoActor(name="proto_test")
    await actor.start()
   
    yield actor

    await actor.stop()
