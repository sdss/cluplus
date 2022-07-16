# -*- coding: utf-8 -*-
#
# @Author: Florian Briegel (briegel@mpia.de
# @Date: 2021-10-18
# @Filename: configloader.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)


import os

from yaml import SafeLoader, load
from expandvars import expand

class Loader(SafeLoader):
    def __init__(self, stream):
        self._root = os.path.split(stream.name)[0]
        super(Loader, self).__init__(stream)
        self.add_constructor('!include', Loader.include)
        self.add_constructor('!env', Loader.env)

    def include(self, node):
        filename = os.path.join(self._root, self.construct_scalar(node))
        with open(filename, 'r') as f:
            return load(f, Loader)

    def env(self, node):
        return expand(self.construct_scalar(node))
