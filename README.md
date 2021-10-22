# cluplus

![Versions](https://img.shields.io/badge/python->3.7-blue)
[![Documentation Status](https://readthedocs.org/projects/sdss-cluplus/badge/?version=latest)](https://sdss-cluplus.readthedocs.io/en/latest/?badge=latest)
[![Travis (.org)](https://img.shields.io/travis/wasndas/cluplus)](https://travis-ci.org/wasndas/cluplus)
[![codecov](https://codecov.io/gh/wasndas/cluplus/branch/main/graph/badge.svg)](https://codecov.io/gh/wasndas/cluplus)

Skymaker camera based on sdss-basecam

## from [lvmtan](https://github.com/sdss/lvmtan) run:

    poetry run container_start --name lvm.all

## from [lvmpwi](https://github.com/sdss/lvmpwi) run:

    poetry run container_start --name=lvm.sci.pwi --simulator

## from cluplus run:

    poetry run python utils/plot_cluplus.py -v -c python/cluplus/etc/cameras.yaml lvm.sci.agw.cam


