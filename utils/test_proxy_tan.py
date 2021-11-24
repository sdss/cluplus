# -*- coding: utf-8 -*-
#
# @Author: Florian Briegel (briegel@mpia.de)
# @Date: 2021-08-18
# @Filename: proxy_test.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)

import uuid
import sys


from clu import AMQPClient, CommandStatus
from cluplus.proxy import Proxy, unpack, invoke


class LVM():
    class SCI():
        FOC = "lvm.sci.foc"
        KM = "lvm.sci.km"
        PWI = "lvm.sci.pwi"
    SCI = SCI()
    class SKYE():
        FOC = "lvm.skye.foc"
        KM = "lvm.skye.km"
        PWI = "lvm.skye.pwi"
    SKYE = SKYE()
    class SKYW():
        FOC = "lvm.skyw.foc"
        KM = "lvm.skyw.km"
        PWI = "lvm.skyw.pwi"
    SKYW = SKYW()
    class SPEC():
        FIBSEL = "lvm.spec.fibsel"
        KM = "lvm.spec.km"
        PWI = "lvm.spec.pwi"
    SPEC = SPEC()

amqpc = AMQPClient(name=f"{sys.argv[0]}.client-{uuid.uuid4().hex[:8]}")

lvm_sci_foc=Proxy(amqpc, LVM.SCI.FOC).start()
lvm_skyw_foc=Proxy(amqpc, LVM.SCI.FOC).start()
lvm_skye_foc=Proxy(amqpc, LVM.SCI.FOC).start()
lvm_spec_foc=Proxy(amqpc, LVM.SCI.FOC).start()


invoke(
    lvm_sci_foc.moveToHome(),
    lvm_skye_foc.moveToHome(),
    lvm_skyw_foc.moveToHome(),
    lvm_spec_foc.moveToHome(),
)

