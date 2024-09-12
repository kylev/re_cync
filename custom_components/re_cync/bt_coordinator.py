"""ReCync Hub."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.bluetooth import (
    BluetoothChange,
    BluetoothScanningMode,
    BluetoothServiceInfoBleak,
)
from homeassistant.components.bluetooth.passive_update_coordinator import (
    PassiveBluetoothDataUpdateCoordinator,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback

_LOGGER = logging.getLogger(__name__)


class ReCyncBTCoordinator(PassiveBluetoothDataUpdateCoordinator):
    """An experimental BT thingy."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the coordinator."""
        # device_id = "AA:BB:CC:DD:EE:FF"
        device_id = "34134372E6A0"
        super().__init__(hass, _LOGGER, device_id, BluetoothScanningMode.PASSIVE)

        self.data: dict[str, Any] = {}

    @callback
    def _async_handle_bluetooth_event(
        self,
        service_info: BluetoothServiceInfoBleak,
        change: BluetoothChange,
    ) -> None:
        """Handle a Bluetooth event."""
        _LOGGER.info("Bluetooth event: %s -> %s", service_info, change)
