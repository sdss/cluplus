# -*- coding: utf-8 -*-
#
# @Author: Florian Briegel (briegel@mpia.de)
# @Date: 2021-08-18
# @Filename: test_lvm_actor.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)

import json
from types import SimpleNamespace


#class LVM():
    #class SCI():
        #FOC = "lvm.sci.foc"
        #KM = "lvm.sci.km"
        #PWI = "lvm.sci.pwi"
    #SCI = SCI()

    #class SKYE():
        #FOC = "lvm.skye.foc"
        #KM = "lvm.skye.km"
        #PWI = "lvm.skye.pwi"
    #SKYE = SKYE()

    #class SKYW():
        #FOC = "lvm.skyw.foc"
        #KM = "lvm.skyw.km"
        #PWI = "lvm.skyw.pwi"
    #SKYW = SKYW()

    #class SPEC():
        #FIBSEL = "lvm.spec.fibsel"
        #FOC = "lvm.spec.foc"
        #PWI = "lvm.spec.pwi"
    #SPEC = SPEC()


lvm_tree = '{ "SCI":  \
              { "FOC":   "lvm.sci.foc", \
                "KM":    "lvm.sci.km", \
                "PWI":   "lvm.sci.pwi" \
              }, \
             "SKYW":  \
              { "FOC":   "lvm.skyw.foc", \
                "KM":    "lvm.skyw.km", \
                "PWI":   "lvm.skyw.pwi" \
              }, \
             "SKYE":  \
              { "FOC":   "lvm.skye.foc", \
                "KM":    "lvm.skye.km", \
                "PWI":   "lvm.skye.pwi" \
              }, \
             "SPEC":  \
              { "FOC":   "lvm.spec.foc", \
                "FISEL": "lvm.spec.fibsel", \
                "PWI":   "lvm.spec.pwi" \
              } \
            }'

LVM = json.loads(lvm_tree, object_hook=lambda d: SimpleNamespace(**d))


