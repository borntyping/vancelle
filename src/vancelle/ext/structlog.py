import sys

import structlog


def configure_logging():
    structlog.configure_once(
        processors=[
            structlog.stdlib.add_log_level,
            structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S"),
            structlog.dev.ConsoleRenderer(pad_event=0, sort_keys=False),
        ],
        logger_factory=structlog.PrintLoggerFactory(sys.stderr),
    )
