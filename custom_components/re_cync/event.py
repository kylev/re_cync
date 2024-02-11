"""Event-driven cloud connection."""

import asyncio
import ssl

from asyncio.coroutines import iscoroutinefunction
from enum import Enum
import logging
import struct
from typing import TYPE_CHECKING, NoReturn, TypedDict
from collections.abc import Callable


_LOGGER = logging.getLogger(__name__)


class ResourceTypes(Enum):
    UNKNOWN = "unknown"


class ReCyncEvent(TypedDict):
    """Hue Event message as emitted by the EventStream."""

    id: str  # UUID
    creationtime: str
    type: str  # = EventType (add, update, delete)
    # data contains a list with (partial) resource objects
    # in case of add or update this is a full or partial resource object
    # in case of delete this will include only the
    # ResourceIndentifier (type and id) of the deleted object
    data: list[dict]


class EventType(Enum):
    """Enum with possible Events."""

    CONNECTED = "connected"
    RECONNECTED = "reconnected"
    DISCONNECTED = "disconnected"

    RESOURCE_ADDED = "add"
    RESOURCE_UPDATED = "update"
    # All the rest goes here...


class EventStreamStatus(Enum):
    """Status options of EventStream."""

    CONNECTING = 0
    CONNECTED = 1
    DISCONNECTED = 2


EventCallBackType = Callable[[EventType, dict | None], None]
EventSubscriptionType = tuple[
    EventCallBackType,
    "tuple[EventType] | None",
    "tuple[ResourceTypes] | None",
]


class EventStream:
    """Holds the connection to the Cync cloud service."""

    def __init__(self, login_code) -> None:
        """Initialize instance."""
        self._login_code = login_code
        self._listeners = set()
        self._event_queue = asyncio.Queue()
        self._last_event_id = ""
        self._status = EventStreamStatus.DISCONNECTED
        self._bg_tasks: list[asyncio.Task] = []
        self._subscribers: list[EventSubscriptionType] = []
        self._reader = None
        self._writer = None

    @property
    def connected(self) -> bool:
        """Return bool if we're connected."""
        return self._status == EventStreamStatus.CONNECTED

    @property
    def status(self) -> bool:
        """Return connection status."""
        return self._status

    async def initialize(self) -> None:
        """Start listening for events.

        Starts the connection to the Hue Eventstream and collect events.
        Connection will be auto-reconnected if it gets lost.
        """
        assert len(self._bg_tasks) == 0
        self._bg_tasks.append(asyncio.create_task(self.__event_reader()))

    #        self._bg_tasks.append(asyncio.create_task(self.__event_processor()))
    #        self._bg_tasks.append(asyncio.create_task(self.__keepalive_workaround()))

    async def stop(self) -> None:
        """Stop listening for events."""
        for task in self._bg_tasks:
            task.cancel()
        self._bg_tasks = []

    def emit(self, etype: EventType, data: dict | None = None) -> None:
        """Emit event to all listeners."""
        for callback, event_filter, resource_filter in self._subscribers:
            if event_filter is not None and etype not in event_filter:
                continue
            if (
                data is not None and resource_filter is not None
                # TODOuncomment and ResourceTypes(data.get("type")) not in resource_filter
            ):
                continue
            if iscoroutinefunction(callback):
                asyncio.create_task(callback(etype, data))  # noqa: RUF006
            else:
                callback(etype, data)

    async def __event_reader(self) -> NoReturn:
        self._status = EventStreamStatus.CONNECTING

        connect_attempts = 0
        while True:
            connect_attempts += 1
            try:
                self._reader, self._writer = await self.__connect()
                self._writer.write(self._login_code)
                await self._writer.drain()

                self._status = EventStreamStatus.CONNECTED
                if connect_attempts == 1:
                    self.emit(EventType.CONNECTED)
                else:
                    self.emit(EventType.RECONNECTED)

                await self.__process()
            except Exception as e:
                _LOGGER.info("Oopsie!", exc_info=e)
                await asyncio.sleep(2)

            self.emit(EventType.DISCONNECTED)

    async def __connect(self):
        _LOGGER.info("Connecting to cloud.")
        context = ssl.create_default_context()
        try:
            return await asyncio.open_connection(
                "cm.gelighting.com", 23779, ssl=context
            )
        except ssl.CertificateError:
            _LOGGER.warning("Connection problem, disabling SSL verification")
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE

        return await asyncio.open_connection("cm.gelighting.com", 23779, ssl=context)

    async def __process(self):
        while True:
            header = await self._reader.read(5)
            if self._reader.at_eof():
                self.emit(EventType.DISCONNECTED)
                break
            packet_type = int(header[0])
            packet_length = struct.unpack(">I", header[1:5])[0]
            packet = await self._reader.read(packet_length)

            match packet_type:
                case 0x18:  # 24
                    _LOGGER.debug("PING?")
                case 0x43:  # 67
                    self.__handle_status_update(packet)
                # case 0x73:  # 115
                #     pass
                case 0x83:  # 131 State packet
                    self.__handle_toggle(packet)
                # case 0xAB:  # 171
                #     pass
                # case 0x7B:  # 123
                #     pass
                case 0xE0:  # 224 Usually 1-byte 0x03, before we get an eof
                    self.__handle_error(packet)
                case _:
                    _LOGGER.debug(
                        "Dropping packet 0x%02x (%d) length %d <%s>",
                        packet_type,
                        packet_type,
                        packet_length,
                        packet,
                    )

    def __handle_error(self, packet):
        assert len(packet) == 1

        err_code = int(packet[0])
        _LOGGER.warning("Handled error %02x %d", err_code, err_code)

    def __handle_status_update(self, packet):
        switch_id = str(struct.unpack(">I", packet[0:4])[0])
        _LOGGER.debug("Status from switch %s %d", switch_id, len(packet) % 19)

    def __handle_toggle(self, packet):
        switch_id = str(struct.unpack(">I", packet[0:4])[0])
        _LOGGER.debug("Toggle from switch %s %d", switch_id, len(packet) % 19)
