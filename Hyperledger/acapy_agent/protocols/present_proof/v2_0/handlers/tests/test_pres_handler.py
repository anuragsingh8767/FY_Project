from unittest import IsolatedAsyncioTestCase

from ......core.oob_processor import OobMessageProcessor
from ......messaging.request_context import RequestContext
from ......messaging.responder import MockResponder
from ......tests import mock
from ......transport.inbound.receipt import MessageReceipt
from ......utils.testing import create_test_profile
from ...messages.pres import V20Pres
from .. import pres_handler as test_module


class TestV20PresHandler(IsolatedAsyncioTestCase):
    async def test_called(self):
        request_context = RequestContext.test_context(await create_test_profile())
        request_context.message_receipt = MessageReceipt()
        request_context.settings["debug.auto_verify_presentation"] = False

        oob_record = mock.MagicMock()
        mock_oob_processor = mock.MagicMock(OobMessageProcessor, autospec=True)
        mock_oob_processor.find_oob_record_for_inbound_message = mock.CoroutineMock(
            return_value=oob_record
        )
        request_context.injector.bind_instance(OobMessageProcessor, mock_oob_processor)

        with mock.patch.object(
            test_module, "V20PresManager", autospec=True
        ) as mock_pres_mgr:
            mock_pres_mgr.return_value.receive_pres = mock.CoroutineMock()
            request_context.message = V20Pres()
            request_context.connection_ready = True
            request_context.connection_record = mock.MagicMock()
            handler = test_module.V20PresHandler()
            responder = MockResponder()
            await handler.handle(request_context, responder)

        mock_pres_mgr.assert_called_once_with(request_context.profile)
        mock_pres_mgr.return_value.receive_pres.assert_called_once_with(
            request_context.message, request_context.connection_record, oob_record
        )
        assert not responder.messages

    async def test_called_auto_verify(self):
        request_context = RequestContext.test_context(await create_test_profile())
        request_context.message_receipt = MessageReceipt()
        request_context.settings["debug.auto_verify_presentation"] = True

        oob_record = mock.MagicMock()
        mock_oob_processor = mock.MagicMock(OobMessageProcessor, autospec=True)
        mock_oob_processor.find_oob_record_for_inbound_message = mock.CoroutineMock(
            return_value=oob_record
        )
        request_context.injector.bind_instance(OobMessageProcessor, mock_oob_processor)

        with mock.patch.object(
            test_module, "V20PresManager", autospec=True
        ) as mock_pres_mgr:
            mock_pres_mgr.return_value.receive_pres = mock.CoroutineMock()
            mock_pres_mgr.return_value.verify_pres = mock.CoroutineMock()
            request_context.message = V20Pres()
            request_context.connection_ready = True
            request_context.connection_record = mock.MagicMock()
            handler = test_module.V20PresHandler()
            responder = MockResponder()
            await handler.handle(request_context, responder)

        mock_pres_mgr.assert_called_once_with(request_context.profile)
        mock_pres_mgr.return_value.receive_pres.assert_called_once_with(
            request_context.message, request_context.connection_record, oob_record
        )
        assert not responder.messages

    async def test_called_auto_verify_x(self):
        request_context = RequestContext.test_context(await create_test_profile())
        request_context.message_receipt = MessageReceipt()
        request_context.settings["debug.auto_verify_presentation"] = True

        oob_record = mock.MagicMock()
        mock_oob_processor = mock.MagicMock(OobMessageProcessor, autospec=True)
        mock_oob_processor.find_oob_record_for_inbound_message = mock.CoroutineMock(
            return_value=oob_record
        )
        request_context.injector.bind_instance(OobMessageProcessor, mock_oob_processor)

        with mock.patch.object(
            test_module, "V20PresManager", autospec=True
        ) as mock_pres_mgr:
            mock_pres_mgr.return_value = mock.MagicMock(
                receive_pres=mock.CoroutineMock(
                    return_value=mock.MagicMock(save_error_state=mock.CoroutineMock())
                ),
                verify_pres=mock.CoroutineMock(side_effect=test_module.LedgerError()),
            )

            request_context.message = V20Pres()
            request_context.connection_ready = True
            request_context.connection_record = mock.MagicMock()
            handler = test_module.V20PresHandler()
            responder = MockResponder()

            with mock.patch.object(
                handler._logger, "exception", mock.MagicMock()
            ) as mock_log_exc:
                await handler.handle(request_context, responder)
                mock_log_exc.assert_called_once()
