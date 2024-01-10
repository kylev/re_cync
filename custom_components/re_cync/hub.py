"""ReCync Hub."""

import logging

_LOGGER = logging.getLogger(__name__)


class Hub:
    """Cync's cloud "hub" that works over IP."""

    def __init__(self) -> None:
        _LOGGER.debug("Init")
