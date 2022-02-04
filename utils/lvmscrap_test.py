import asyncio
from datetime import datetime as dt
import aio_pika as apika

from clu.client import AMQPClient, AMQPReply


class AMQPClientScrap(AMQPClient):
    async def handle_reply(self, message: apika.IncomingMessage) -> AMQPReply:
        """Handles a reply received from the exchange.
        """
        reply = AMQPReply(message, log=self.log)
        print(f"{dt.now()} {reply.sender} {reply.body}")


async def main(loop):
   client = await AMQPClientScrap('lvm.scrap', host='localhost').start()
   

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(main(loop))
    print("waiting ...")
    loop.run_forever()

