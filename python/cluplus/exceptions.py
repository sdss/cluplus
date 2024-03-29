# -*- coding: utf-8 -*-
#
# @Author: Florian Briegel (briegel@mpia.de)
# @Date: 2021-08-18
# @Filename: exceptions.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)


class ProxyException(Exception):
    """Base proxy exception"""
    
    pass


class ProxyPartialInvokeException(ProxyException):
    """One or more invocation failed"""

    pass

class ProxyActorIsNotReachableException(ProxyException):
    """The actor is not reachable"""

    pass

class ProxyUnpackKeysNotAllFoundException(ProxyException):
    """More than one provided unpack filter keys not found"""

    pass
