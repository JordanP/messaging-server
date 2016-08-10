#!/usr/bin/env python3.5
import asyncio
import os
import random
import typing

from autobahn.asyncio.websocket import WebSocketClientFactory
from autobahn.asyncio.websocket import WebSocketClientProtocol
from autobahn.websocket.protocol import ConnectionResponse

CLIENT_COUNT = int(os.environ.get("CLIENT_COUNT", "3"))
PING_INTERVAL = int(os.environ.get("PING_INTERVAL", "5"))

clients = {}


async def client_count():
    while True:
        print("Connected clients: %s" % len(clients))
        await asyncio.sleep(1)


class MyClientProtocol(WebSocketClientProtocol):
    def onConnect(self, response: ConnectionResponse):
        print("Connected to server: {0}".format(response.peer))

    @asyncio.coroutine
    def onOpen(self):
        clients[self] = True
        # start sending messages repeatedly
        while True:
            recipient_id = random.randint(0, len(clients) - 1)
            self.sendMessage(b"%d\x00Hello World" % recipient_id)
            yield from asyncio.sleep(PING_INTERVAL)

    def onMessage(self, payload: bytes, isBinary: bool):
        print("Text message received: {0}".format(payload.decode('utf8')))

    def onClose(self, wasClean: bool, code: typing.Union[int, None],
                reason: typing.Union[str, None]):
        print("Connection closed: {0}".format(reason))
        clients.pop(self, None)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(client_count())

    for i in range(CLIENT_COUNT):
        factory = WebSocketClientFactory("ws://127.0.0.1:9000?clientId=%d" % i)
        factory.protocol = MyClientProtocol
        coro = loop.create_connection(factory, '127.0.0.1', 9000)
        loop.create_task(coro)

    try:
        loop.run_forever()
    finally:
        loop.close()
