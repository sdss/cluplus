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


async def test_single_param_return():
    
    consumer = "lvm.sci.foc"
    amqpc = AMQPClient(name=f"{sys.argv[0]}.proxy-{uuid.uuid4().hex[:8]}")
    await amqpc.start()
    
    lvm_sci_foc=Proxy(amqpc, consumer)
    await lvm_sci_foc.start()
    
    amqpc.log.warning(sys.argv[0])
        
    amqpc.log.warning(f'#1: {unpack(await lvm_sci_foc.isReachable())}')
    
    pos, unit = unpack(await lvm_sci_foc.getDeviceEncoderPosition("UM"))
    amqpc.log.warning(f'#2: {pos}, {unit}')

    amqpc.log.warning(f'#3: {(await invoke(lvm_sci_foc.getPosition())).Position}')

    pos = await invoke(lvm_sci_foc.getDeviceEncoderPosition("UM"))
    amqpc.log.warning(f'#4: {pos.DeviceEncoderPosition}')

    pos = unpack(await lvm_sci_foc.getDeviceEncoderPosition("UM"))
    amqpc.log.warning(f'#5 {pos}')

    amqpc.log.warning(f'#6: {await invoke(lvm_sci_foc.getNamedPosition(1))}')

    try:
        await invoke(lvm_sci_foc.getNamedPosition(1), lvm_sci_foc.getNamedPosition(10), lvm_sci_foc.getNamedPosition(12))
    except ProxyException as e:
        amqpc.log.warning(f"Exception: {e}")

    try:
        await invoke(lvm_sci_foc.getNamedPosition(10))
    except Exception as e:
        amqpc.log.warning(f"Exception: {e}")

    try:
        unpack(await lvm_sci_foc.getDeviceEncoderPositin("UM"))
    except Exception as e:
        amqpc.log.warning(f"Exception: {e}")


asyncio.run(test_single_param_return())


async def test_single_param_return():
    
    consumer = "lvm.sci.foc"
    amqpc = AMQPClient(name=f"{sys.argv[0]}.client-{uuid.uuid4().hex[:8]}")
    await amqpc.start()
    
    lvm_sci_foc=Proxy(amqpc, consumer)
    await lvm_sci_foc.start()
    
    amqpc.log.warning(f'#1: {(await invoke(lvm_sci_foc.isReachable())).Reachable}')
    
    amqpc.log.warning(f'#2: {unpack(await lvm_sci_foc.isReachable())}')
    amqpc.log.warning(f'#3: {unpack(await lvm_sci_foc.getDeviceEncoderPosition("UM"))}')
    
asyncio.run(test_single_param_return())


async def test_callback_and_blocking():
    
    consumer = "lvm.sci.foc"
    amqpc = AMQPClient(name=f"{sys.argv[0]}.client-{uuid.uuid4().hex[:8]}")
    await amqpc.start()
    
    lvm_sci_foc=Proxy(amqpc, consumer)
    await lvm_sci_foc.start()
    
    def toHome_callback(reply): amqpc.log.warning(f"Reply: {CommandStatus.code_to_status(reply.message_code)} {reply.body}")
    await lvm_sci_foc.moveToHome(callback=toHome_callback)
    
    def toLimit_callback(reply): amqpc.log.warning(f"Reply: {CommandStatus.code_to_status(reply.message_code)} {reply.body}")
    await lvm_sci_foc.moveToLimit(-1, callback=toLimit_callback)



asyncio.run(test_callback_and_blocking())

async def test_tasks():
    
    amqpc = AMQPClient(name=f"{sys.argv[0]}.client-{uuid.uuid4().hex[:8]}")
    await amqpc.start()
    
    lvm_sci_foc=Proxy(amqpc, "lvm.sci.foc")
    await lvm_sci_foc.start()
    
    lvm_skye_foc=Proxy(amqpc, "lvm.skye.foc")
    await lvm_skye_foc.start()
    
    lvm_skyw_foc=Proxy(amqpc, "lvm.skyw.foc")
    await lvm_sci_foc.start()
    
    lvm_skyw_foc=Proxy(amqpc, "lvm.spec.foc")
    await lvm_spec_foc.start()
    
    ret = await invoke(
            lvm_sci_foc.moveToHome(),
            lvm_skye_foc.moveToHome(),
            lvm_skyw_foc.moveToHome(),
            lvm_spec_foc.moveToHome(),
          )
    amqpc.log.warning(f"{ret}")
    
    ret = await invoke(
                lvm_sci_foc.moveToLimit(-1),
                lvm_skye_foc.moveToLimit(-1),
                lvm_skyw_foc.moveToLimit(-1),
                lvm_spec_foc.moveToLimit(-1),
            )
    amqpc.log.warning(f"{ret}")

asyncio.run(test_tasks())

async def test_callback_and_parallel_classic():
    
    amqpc = AMQPClient(name=f"{sys.argv[0]}.client-{uuid.uuid4().hex[:8]}")
    await amqpc.start()
    
    lvm_sci_foc=Proxy(amqpc, "lvm.sci.foc")
    lvm_skye_foc=Proxy(amqpc, "lvm.skye.foc")
    
    def toHome_callback(reply): amqpc.log.warning(f"Reply: {CommandStatus.code_to_status(reply.message_code)} {reply.body}")
    
    lvm_sci_foc_future = await lvm_sci_foc.moveToHome(callback=toHome_callback, blocking=False)
    lvm_skye_foc_future = await lvm_skye_foc.moveToHome(callback=toHome_callback, blocking=False)
    await lvm_sci_foc_future
    await lvm_skye_foc_future
    
    def toLimit_callback(reply): amqpc.log.warning(f"Reply: {CommandStatus.code_to_status(reply.message_code)} {reply.body}")
    
    lvm_sci_foc_future = await lvm_sci_foc.moveToLimit(-1, callback=toLimit_callback, blocking=False)
    lvm_skye_foc_future = await lvm_skye_foc.moveToLimit(-1, callback=toLimit_callback, blocking=False)
    await lvm_sci_foc_future
    await lvm_skye_foc_future
    

asyncio.run(test_callback_and_parallel_classic())

async def test_callback_and_gather_raw():
    
    amqpc = AMQPClient(name=f"{sys.argv[0]}.client-{uuid.uuid4().hex[:8]}")
    await amqpc.start()
    
    lvm_sci_foc=Proxy(amqpc, "lvm.sci.foc")
    lvm_skye_foc=Proxy(amqpc, "lvm.skye.foc")
    lvm_skyw_foc=Proxy(amqpc, "lvm.skyw.foc")
    lvm_spec_foc=Proxy(amqpc, "lvm.spec.foc")
    
    
    ret = await asyncio.gather(
            await lvm_sci_foc.moveToHome(blocking=False),
            await lvm_skye_foc.moveToHome(blocking=False),
            await lvm_skyw_foc.moveToHome(blocking=False),
            await lvm_spec_foc.moveToHome(blocking=False),
            return_exceptions=True
          )
    amqpc.log.warning(f"{ret}")
    
    ret = await asyncio.gather(
                    await lvm_sci_foc.moveToLimit(-1, blocking=False),
                    await lvm_skye_foc.moveToLimit(-1, blocking=False),
                    await lvm_skyw_foc.moveToLimit(-1, blocking=False),
                    await lvm_spec_foc.moveToLimit(-1, blocking=False),
                    return_exceptions=True 
                  )
    amqpc.log.warning(f"{ret}")

asyncio.run(test_callback_and_gather_raw())





