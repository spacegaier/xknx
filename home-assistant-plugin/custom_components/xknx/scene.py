"""Support for KNX scenes."""
from typing import Any

from homeassistant.components.scene import Scene

from xknx.devices import Scene as XknxScene

from . import DATA_XKNX


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the scenes for KNX platform."""
    entities = []
    for device in hass.data[DATA_XKNX].xknx.devices:
        if isinstance(device, XknxScene):
            entities.append(KNXScene(device))
    async_add_entities(entities)


class KNXScene(Scene):
    """Representation of a KNX scene."""

    def __init__(self, scene: XknxScene):
        """Init KNX scene."""
        self.scene = scene

    @property
    def name(self):
        """Return the name of the scene."""
        return self.scene.name

    @property
    def unique_id(self):
        """Return a unique ID of the KNX device."""
        return self.device.unique_id

    async def async_activate(self, **kwargs: Any) -> None:
        """Activate the scene."""
        await self.scene.run()
