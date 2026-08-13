import sys

import structlog

from camp_match.config.settings import Settings


def configure_logging(settings: Settings) -> None:
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer(),
        ],
        logger_factory=structlog.PrintLoggerFactory(sys.stderr),
    )
    # Note: actual log level management for standard library logging
    # would need additional setup, but for structlog it works fine.
