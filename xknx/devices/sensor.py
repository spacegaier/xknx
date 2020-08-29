"""
Module for managing a sensor via KNX.

It provides functionality for

* reading the current state from KNX bus.
* watching for state updates from KNX bus.
"""
from xknx.remote_value import RemoteValueSensor

from .device import Device


class Sensor(Device):
    """Class for managing a sensor."""

    def __init__(
        self,
        xknx,
        unique_id=None,
        group_address_state=None,
        sync_state=True,
        value_type=None,
        device_updated_cb=None,
        name=None,
    ):
        """Initialize Sensor class."""
        # pylint: disable=too-many-arguments
        super().__init__(xknx, unique_id, name, device_updated_cb)

        self.sensor_value = RemoteValueSensor(
            xknx,
            group_address_state=group_address_state,
            sync_state=sync_state,
            value_type=value_type,
            device_name=self.name,
            after_update_cb=self.after_update,
        )

    def _iter_remote_values(self):
        """Iterate the devices RemoteValue classes."""
        yield self.sensor_value

    @classmethod
    def from_config(cls, xknx, unique_id, config):
        """Initialize object from configuration structure."""
        name = config.get("name")
        group_address_state = config.get("group_address_state")
        sync_state = config.get("sync_state", True)
        value_type = config.get("value_type")

        return cls(
            xknx,
            unique_id,
            name=name,
            group_address_state=group_address_state,
            sync_state=sync_state,
            value_type=value_type,
        )

    async def process_group_write(self, telegram):
        """Process incoming GROUP WRITE telegram."""
        await self.sensor_value.process(telegram)

    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return self.sensor_value.unit_of_measurement

    def ha_device_class(self):
        """Return the home assistant device class as string."""
        return self.sensor_value.ha_device_class

    def resolve_state(self):
        """Return the current state of the sensor as a human readable string."""
        return self.sensor_value.value

    def __str__(self):
        """Return object as readable string."""
        return '<Sensor name="{0}" ' 'sensor="{1}" value="{2}" unit="{3}"/>'.format(
            self.name,
            self.sensor_value.group_addr_str(),
            self.resolve_state(),
            self.unit_of_measurement(),
        )
