# cluplus

![Versions](https://img.shields.io/badge/python->3.7-blue)
[![Documentation Status](https://readthedocs.org/projects/sdss-cluplus/badge/?version=latest)](https://sdss-cluplus.readthedocs.io/en/latest/?badge=latest)
[![Test](https://github.com/wasndas/cluplus/actions/workflows/test.yml/badge.svg)](https://github.com/wasndas/cluplus/actions/workflows/test.yml)
[![codecov](https://codecov.io/gh/wasndas/cluplus/branch/main/graph/badge.svg)](https://codecov.io/gh/wasndas/cluplus)

## Features

- RPC/Corba/Zeroc Ice style actor communications
- Recursive config file loading

   
## Prerequisites

Some linux distributions do not have python >= 3.7 as the standard python3 version.

### Centos 8.X

    # as root
    yum install python38
    # as user 
    python3.8  -m pip  install --user --upgrade pip
    pip3.8 install poetry
    export PATH=~/.local/bin/:$PATH

### OpenSuSe 15.2/15.3

    # as root
    zypper ar https://download.opensuse.org/repositories/devel:/languages:/python:/Factory/openSUSE_Leap_15.2/ devel_python
    zypper install python39-devel
    # as user 
    python3.9 -m ensurepip --default-pip # Alternatve: python3.9 -m venv ~/.local 
    pip3.9 install --upgrade pip
    pip3.9 install poetry
    export PATH=~/.local/bin/:$PATH
