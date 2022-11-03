import logging

_logger = logging.getLogger(__name__)


def accept_format_string(mes, *args):
    """
    Use it for System Messages.
    Accept any args to format string. Not raise error if wrong arguments passed.


    example:
    mes = "New message from %s to test %d functions"
    accept_format_string(mes, ('system', 22))
    """
    try:
        message = mes % args
    except TypeError as e:
        message = "Format system message error: %s" % e
        _logger.error(message)
    return message


SystemMessages = {
    "M-003": "Quantity is not set! Please, populate Quantity field with the necessary value.",
    "M-004": "Please, make sure the Order type is chosen correctly!"
}
