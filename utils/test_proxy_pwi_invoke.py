# -*- coding: utf-8 -*-
#
# @Author: Florian Briegel (briegel@mpia.de)
# @Date: 2021-08-18
# @Filename: proxy_test.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)

import uuid
import sys

from clu import AMQPClient, CommandStatus
from cluplus.proxy import Proxy, ProxyClient, unpack, invoke

import asyncio

async def test_proxy_pwi_invoke(ra, dec):
    amqpc = AMQPClient(name=f"{sys.argv[0]}.proxy-{uuid.uuid4().hex[:8]}")
    await amqpc.start()
    
    lvm_sci_pwi=Proxy(amqpc, "lvm.sci.pwi")
    lvm_skye_pwi=Proxy(amqpc, "lvm.skye.pwi")
    lvm_skyw_pwi=Proxy(amqpc, "lvm.skyw.pwi")
    lvm_spec_pwi=Proxy(amqpc, "lvm.spec.pwi")

    await lvm_sci_foc.start()
    await lvm_skye_foc.start()
    await lvm_sci_foc.start()
    await lvm_spec_foc.start()
    
    try:
        await invoke(
                 lvm_sci_pwi.setConnected(True),
                 lvm_skye_pwi.setConnected(True),
                 lvm_skyw_pwi.setConnected(True),
                 lvm_spec_pwi.setConnected(True),
              )
        
        await invoke(
                 lvm_sci_pwi.setEnabled(True),
                 lvm_skye_pwi.setEnabled(True),
                 lvm_skyw_pwi.setEnabled(True),
                 lvm_spec_pwi.setEnabled(True),
              )
        
        # lets define a callback for status updates.
        def callback(reply): amqpc.log.warning(f"Reply: {CommandStatus.code_to_status(reply.message_code)} {reply.body}")
        
        rc = await invoke(
                 lvm_sci_pwi.gotoRaDecJ2000(ra, dec, callback=callback),
                 lvm_skye_pwi.gotoRaDecJ2000(ra, dec),
                 lvm_skyw_pwi.gotoRaDecJ2000(ra, dec),
                 lvm_spec_pwi.gotoRaDecJ2000(ra, dec),
              )
        
        # we do use send_command/click options without --, it will be added internally
        await lvm_sci_pwi.offset(ra_add_arcsec=10)
        
    except Exception as e:
        amqpc.log.warning(f"Exception: {e}")


print (len(sys.argv))
if len(sys.argv) < 3:
    print(f'missing ra dec param')
    
asyncio.run(test_proxy_pwi_invoke(sys.argv[1], sys.argv[2]))

