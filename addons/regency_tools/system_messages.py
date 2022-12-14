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
    "M-004": "Please, make sure you’ve allowed Consumption Agreement creation!",
    "M-005": "%s is confirmed. Please, send it to the customer!<br/>The link to portal: %s",
    "M-009": "%s %s created!",
    "M-010": "%s is created!",
    "M-011": "%s has signed the %s",
    "M-013": "%s requests your approval"
}
