from __future__ import annotations
from homeassistant.components.button import ButtonEntity
from homeassistant.helpers.entity import DeviceInfo

from .const import DOMAIN, CONF_DEVICE_ID, CONF_MODEL_ID


async def async_setup_entry(hass, entry, async_add_entities):
    data = hass.data[DOMAIN][entry.entry_id]
    client = data["client"]
    device_id: str = entry.data[CONF_DEVICE_ID]
    model_id: str = entry.data.get(CONF_MODEL_ID, "Instant Pot")

    async_add_entities([InstantPotCancelButton(device_id, model_id, client)])


class InstantPotCancelButton(ButtonEntity):
    """Cancel the current program — same call as the instantpot_fresco.cancel service."""

    _attr_has_entity_name = True
    _attr_name = "Cancel"
    _attr_icon = "mdi:stop-circle-outline"

    def __init__(self, device_id: str, model_id: str, client):
        self._device_id = device_id
        self._model_id = model_id
        self._client = client
        self._attr_unique_id = f"{DOMAIN}_{device_id}_cancel"

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self._device_id)},
            manufacturer="Instant Brands",
            model=self._model_id,
            name=f"Instant Pot ({self._device_id})",
        )

    async def async_press(self) -> None:
        await self._client.execute("kitchenos:Command:Cancel")
