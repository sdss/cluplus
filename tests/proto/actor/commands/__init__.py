import glob
import importlib
import os

import click
from clu.parsers.click import command_parser
from cluplus.parsers.click import __commands, foo

command_parser.add_command(__commands)
command_parser.add_command(foo)

from . import complex_data_with_jsonpickle
from . import erronous
from . import multioptsargs
