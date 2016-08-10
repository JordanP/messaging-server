#!/usr/bin/python3.5
import argparse
import asyncio
import logging
import typing

from autobahn.asyncio.websocket import WebSocketServerFactory
from autobahn.asyncio.websocket import WebSocketServerProtocol
from autobahn.websocket.protocol import ConnectionRequest
from autobahn.websocket.types import IncomingMessage

LOG = logging.getLogger()


class ServerProtocol(WebSocketServerProtocol):
    """Asyncio-based WebSocket server protocol."""

    def onConnect(self, request: ConnectionRequest):
        error = None
        if 'clientId' not in self.http_request_params:
            error = "Missing client ID"
        elif len(self.http_request_params['clientId']) != 1:
            error = "Ambiguous client ID"
        else:
            try:
                self.id = int(self.http_request_params['clientId'][0])
            except ValueError:
                error = "The client ID is not a valid integer"
        if error:
            raise ValueError(error)

    def onOpen(self):
        self.factory.register(self)

    def onClose(self, wasClean: bool, code: typing.Union[int, None],
                reason: typing.Union[str, None]):
        self.factory.unregister(self)

    def onMessage(self, payload: IncomingMessage, isBinary: bool):
        LOG.debug("Got %r from %s", payload, self.peer)
        error = None
        try:
            recipient_client_id, msg = payload.split(b'\x00', 1)
            if not recipient_client_id:
                error = b"Empty recipient client ID"
        except ValueError:
            error = b'Missing recipient client ID'
        if error:
            self.sendMessage(error)
        else:
            recipient_client_id = int(recipient_client_id)
            self.factory.send_msg_to_recipient(self, recipient_client_id, msg)


class ServerFactory(WebSocketServerFactory):
    """Asyncio-based WebSocket server factory"""

    def __init__(self, *args, **kwargs):
        super(ServerFactory, self).__init__(*args, **kwargs)
        self.clients = {}

    def register(self, client: ServerProtocol):
        self.clients[client.id] = client
        LOG.info("Added client: peer=%s, id=%d", client.peer, client.id)
        LOG.debug("%d client(s) currently registered", len(self.clients))

    def unregister(self, client: ServerProtocol):
        self.clients.pop(client.id, None)
        LOG.info("Removed client: peer=%s, id=%d", client.peer, client.id)
        LOG.debug("%d client(s) currently registered", len(self.clients))

    def send_msg_to_recipient(self, sender_client: ServerProtocol,
                              recipient_client_id: int, msg: bytes):
        if recipient_client_id not in self.clients:
            msg = "Client {:d} is not connected".format(recipient_client_id)
            sender_client.sendMessage(msg.encode('utf-8'))
        else:
            self.clients[recipient_client_id].sendMessage(msg)


def main():
    parser = argparse.ArgumentParser(
        description='Messaging server using Websocket',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        '-v', '--verbose', help='Log at DEBUG level',
        dest='verbose', action='store_true'
    )
    parser.add_argument(
        '-p', '--port', help='Listen port',
        dest='listen_port', type=int, default=9000
    )

    args = parser.parse_args()
    configure_logging(args.verbose)

    factory = ServerFactory(u"ws://127.0.0.1:%d" % args.listen_port)
    factory.protocol = ServerProtocol

    loop = asyncio.get_event_loop()
    coro = loop.create_server(factory, '0.0.0.0', args.listen_port)
    server = loop.run_until_complete(coro)

    try:
        loop.run_forever()
    finally:
        server.close()
        loop.close()


def configure_logging(verbose):
    if verbose:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO
    logging.basicConfig(level=log_level)
