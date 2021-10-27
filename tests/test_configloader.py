# encoding: utf-8
#
# test_main.py

import os
import pytest

from sdsstools.logger import get_logger
from sdsstools.configuration import read_yaml_file

from clu import JSONActor, AMQPActor
from clu.testing import setup_test_actor

from cluplus.configloader import Loader

@pytest.fixture
def lvmnps_config():
    config_file = os.path.join(os.path.dirname(__file__), "proto/etc/lvmnps/lvmnps_dli.yml")
    actor = AMQPActor.from_config(config_file, loader=Loader)
    
    return actor.config


@pytest.mark.asyncio
async def test_config(lvmnps_config):
    assert "switches" in lvmnps_config

    assert(lvmnps_config["switches"]["DLI_NPS_01"]["hostname"] == "10.7.45.22")
    assert(lvmnps_config["switches"]["DLI_NPS_02"]["password"] == "VCrht9wfx2CQN9b")
    
    
