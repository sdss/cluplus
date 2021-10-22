import glob
import importlib
import os

import click
from clu.parsers.click import command_parser
from cluplus.parsers.click import __commands, __exthelp

command_parser.add_command(__commands)
command_parser.add_command(__exthelp)

# Autoimport all modules in this directory so that they are added to the parser.

exclusions = ["__init__.py"]

cwd = os.getcwd()
os.chdir(os.path.dirname(os.path.realpath(__file__)))

files = [
    file_ for file_ in glob.glob("**/*.py", recursive=True) if file_ not in exclusions
]

for file_ in files:
    modname = file_[0:-3].replace("/", ".")
    mod = importlib.import_module("proto.actor.commands." + modname)

os.chdir(cwd)
