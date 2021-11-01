# !usr/bin/env python
# -*- coding: utf-8 -*-
#
# Licensed under a 3-clause BSD license.
#
# @Author: Brian Cherinka
# @Date:   2017-12-05 12:01:21
# @Last modified by:   Brian Cherinka
# @Last Modified time: 2017-12-05 12:19:32


from __future__ import absolute_import, division, print_function


class ProtoActorError(Exception):
    """A custom core ProtoActor exception"""

    pass

class ProtoActorNotImplemented(ProtoActorError):
    """A custom exception for not yet implemented features."""

    pass

class ProtoActorAPIError(ProtoActorError):
    """A custom exception for API errors"""

    pass


class ProtoActorApiAuthError(ProtoActorAPIError):
    """A custom exception for API authentication errors"""

    pass


class ProtoActorMissingDependency(ProtoActorError):
    """A custom exception for missing dependencies."""

    pass


class ProtoActorWarning(Warning):
    """Base warning for ProtoActor."""

    pass

class ProtoActorUserWarning(UserWarning, ProtoActorWarning):
    """The primary warning class."""

    pass


class ProtoActorSkippedTestWarning(ProtoActorUserWarning):
    """A warning for when a test is skipped."""

    pass


class ProtoActorDeprecationWarning(ProtoActorUserWarning):
    """A warning for deprecated features."""

    pass
