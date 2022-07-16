# -*- coding: utf-8 -*-
#
# @Author: Florian Briegel (briegel@mpia.de)
# @Date: 2021-11-19
# @Filename: test_01_configloader.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)


import os
import pytest

# from clu import JSONActor
from clu import AMQPActor
from cluplus.configloader import Loader


@pytest.fixture(scope="session")
def lvmnps_config_file():
    return os.path.join(os.path.dirname(__file__),
                               "proto/etc/lvmnps/lvmnps_dli.yml")


@pytest.mark.asyncio
async def test_config(lvmnps_config_file):

    actor = AMQPActor.from_config(lvmnps_config_file, loader=Loader)

    assert "switches" in actor.config
    assert(actor.config["switches"]["DLI_NPS_01"]["hostname"]
           == "10.7.45.22")
    assert(actor.config["switches"]["DLI_NPS_02"]["password"]
           == "VCrht9wfx2CQN9b")

    assert(actor.config["actor"]["host"]
           == "localhost")

@pytest.mark.asyncio
async def test_config_environ(lvmnps_config_file):

    os.environ["SHOULD_NOT_EXIST_SOMWHERE"]="somewhere"
    
    actor = AMQPActor.from_config(lvmnps_config_file, loader=Loader)

    assert(actor.config["actor"]["host"]
           == "somewhere")
