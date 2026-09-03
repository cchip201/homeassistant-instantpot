from __future__ import annotations
from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.core import callback
from homeassistant.helpers.entity import DeviceInfo

from .const import DOMAIN, CONF_DEVICE_ID, CONF_MODEL_ID
from .api import NotificationsManager


async def async_setup_entry(hass, entry, async_add_entities):
    data = hass.data[DOMAIN][entry.entry_id]
    notif: NotificationsManager = data["notifications"]
    device_id: str = entry.data[CONF_DEVICE_ID]
    model_id: str = entry.data.get(CONF_MODEL_ID, "Instant Pot")

    async_add_entities([InstantPotCookingSensor(device_id, model_id, notif)])


class InstantPotCookingSensor(BinarySensorEntity):
    """On while the appliance is running any program.

    Captured 2026-09-02 during a live Keep Warm: device_state is
    kitchenos:DeviceState:Running while active, :Ready when idle.
    """

    _attr_has_entity_name = True
    _attr_name = "Cooking"
    _attr_device_class = BinarySensorDeviceClass.RUNNING
    _attr_icon = "mdi:pot-steam"

    def __init__(self, device_id: str, model_id: str, notif: NotificationsManager):
        self._device_id = device_id
        self._model_id = model_id
        self._notif = notif
        self._remove_listener = None
        self._state = None
        self._attr_unique_id = f"{DOMAIN}_{device_id}_cooking"

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self._device_id)},
            manufacturer="Instant Brands",
            model=self._model_id,
            name=f"Instant Pot ({self._device_id})",
        )

    @property
    def is_on(self):
        if not self.available or not self._state:
            return None
        dev_state = self._state.get("device_state") or ""
        return dev_state.split(":")[-1] == "Running"

    @property
    def available(self) -> bool:
        return self._notif.is_available(self._device_id)

    async def async_added_to_hass(self):
        @callback
        def _on_update(state: dict):
            self._state = state
            self.async_write_ha_state()

        self._remove_listener = self._notif.add_listener(self._device_id, _on_update)

    async def async_will_remove_from_hass(self):
        if self._remove_listener:
            self._remove_listener()
            self._remove_listener = None
