import asyncio
import logging
import unittest
from unittest import mock

# Tells Autobahn to use the asyncio framework
import autobahn.asyncio  # noqa: F401
from autobahn.websocket.protocol import ConnectionRequest

from messaging_server import main


class TestMain(unittest.TestCase):
    def test_configure_logging(self):
        with mock.patch('logging.basicConfig', autospec=True) as mock_logging:
            self.assertEqual(None, main.configure_logging(verbose=False))
        mock_logging.assert_called_with(level=logging.INFO)

    def test_configure_logging_verbose(self):
        with mock.patch('logging.basicConfig', autospec=True) as mock_logging:
            self.assertEqual(None, main.configure_logging(verbose=True))
        mock_logging.assert_called_with(level=logging.DEBUG)

    @mock.patch('argparse.ArgumentParser.parse_args')
    def test_main(self, mock_parse_args: mock.Mock):
        mock_parse_args.return_value.listen_port = 0  # Random unused port
        loop = asyncio.get_event_loop()

        async def wait_and_stop():
            """Stops the `run_forever` statement in main() after some time."""
            await asyncio.sleep(0.5)
            loop.stop()

        loop.create_task(wait_and_stop())
        main.main()


class TestServerProtocol(unittest.TestCase):
    def setUp(self):
        self.mock_connection_request = mock.Mock(spec_set=ConnectionRequest)
        self.log_patcher = mock.patch.object(main, 'LOG')
        self.log_patcher.start()

    def tearDown(self):
        self.log_patcher.stop()

    def test_on_connect(self):
        sp = main.ServerProtocol()
        sp.http_request_params = {'clientId': [123]}

        self.assertIsNone(sp.onConnect(self.mock_connection_request))
        self.assertEqual(sp.id, 123)

    def test_on_connect_missing_client_id(self):
        sp = main.ServerProtocol()
        sp.http_request_params = {}

        self.assertRaisesRegex(ValueError, "Missing client ID", sp.onConnect,
                               self.mock_connection_request)

    def test_on_connect_ambiguous_client_id(self):
        sp = main.ServerProtocol()
        sp.http_request_params = {'clientId': ['1', '2']}

        self.assertRaisesRegex(ValueError, "Ambiguous client ID", sp.onConnect,
                               self.mock_connection_request)

    def test_on_connect_client_id_not_an_int(self):
        sp = main.ServerProtocol()
        sp.http_request_params = {'clientId': ['str']}

        self.assertRaisesRegex(
            ValueError, "The client ID is not a valid integer",
            sp.onConnect, self.mock_connection_request
        )

    def test_on_open(self):
        sp = main.ServerProtocol()
        sp.factory = mock.Mock(spec_set=main.ServerFactory)

        sp.onOpen()

        sp.factory.register.assert_called_once_with(sp)

    def test_on_close(self):
        sp = main.ServerProtocol()
        sp.factory = mock.Mock(spec_set=main.ServerFactory)

        sp.onClose(wasClean=True, code=1000, reason="")

        sp.factory.unregister.assert_called_once_with(sp)

    def test_on_message_empty_recipient(self):
        sp = main.ServerProtocol()

        with mock.patch.object(sp, 'sendMessage') as mock_send_msg:
            sp.onMessage(b'\x00msg', False)

        mock_send_msg.assert_called_once_with(b"Empty recipient client ID")

    def test_on_message_missing_recipient(self):
        sp = main.ServerProtocol()

        with mock.patch.object(sp, 'sendMessage') as mock_send_msg:
            sp.onMessage(b'msg', False)

        mock_send_msg.assert_called_once_with(b"Missing recipient client ID")

    def test_on_message(self):
        sp = main.ServerProtocol()
        sp.factory = mock.Mock(spec_set=main.ServerFactory)

        with mock.patch.object(sp, 'sendMessage'):
            sp.onMessage(b'123\x00msg', False)

        sp.factory.send_msg_to_recipient.assert_called_once_with(
            sp, 123, b'msg'
        )


class TestServerFactory(unittest.TestCase):
    def setUp(self):
        self.log_patcher = mock.patch.object(main, 'LOG')
        self.log_patcher.start()

    def tearDown(self):
        self.log_patcher.stop()

    def test_init(self):
        sf = main.ServerFactory()
        self.assertEqual({}, sf.clients)

    def test_register(self):
        sf = main.ServerFactory()
        client = mock.Mock(id=123)
        sf.register(client)

        self.assertEqual({123: client}, sf.clients)

    def test_unregister(self):
        sf = main.ServerFactory()
        client = mock.Mock(id=123)
        sf.clients = {123: client}

        sf.unregister(client)

        self.assertEqual({}, sf.clients)

    def test_send_msg_to_recipient_unknown_recipient(self):
        sf = main.ServerFactory()
        sp = mock.Mock(spec_set=main.ServerProtocol)

        sf.send_msg_to_recipient(sp, 42, "msg")

        sp.sendMessage.assert_called_once_with(b"Client 42 is not connected")

    def test_send_msg_to_recipient(self):
        sf = main.ServerFactory()
        client = mock.Mock(id=123)
        sf.clients = {123: client}

        sf.send_msg_to_recipient(client, client.id, "msg")

        client.sendMessage.assert_called_once_with("msg")
