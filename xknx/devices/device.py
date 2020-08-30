"""
Device is the base class for all implemented devices (e.g. Lights/Switches/Sensors).

It provides basis functionality for reading the state from the KNX bus.
"""
from xknx.telegram import TelegramType


class Device:
    """Base class for devices."""

    # Unique ID is the new internal key. However to be backwards compatible, we
    # have to allow also setting up Devices only by name, which we then take over
    # as the unique ID internally.
    # We expect one value to be always provided.
    def __init__(
        self, xknx, unique_id: str = None, name: str = None, device_updated_cb=None
    ):
        """Initialize Device class."""
        if unique_id is None and name is None:
            raise Exception("Either unique_id or name has to be provided!")

        self.unique_id = unique_id
        self.name = name

        # Fallback logic for backwards compatibility:
        # If there is no name provided, use the unique_id
        # If there is no unique_id provided, use the name
        if name is None and unique_id is not None:
            self.name = unique_id
        elif unique_id is None and name is not None:
            self.unique_id = name

        self.xknx = xknx
        self.device_updated_cbs = []
        if device_updated_cb is not None:
            self.register_device_updated_cb(device_updated_cb)

        self.xknx.devices.add(self)

    def _iter_remote_values(self):
        """Iterate the devices RemoteValue classes."""
        raise NotImplementedError("_iter_remote_values has to be implemented")
        # yield self.remote_value
        # or
        # yield from (<list all used RemoteValue instances>)

    def register_device_updated_cb(self, device_updated_cb):
        """Register device updated callback."""
        self.device_updated_cbs.append(device_updated_cb)

    def unregister_device_updated_cb(self, device_updated_cb):
        """Unregister device updated callback."""
        self.device_updated_cbs.remove(device_updated_cb)

    async def after_update(self):
        """Execute callbacks after internal state has been changed."""
        for device_updated_cb in self.device_updated_cbs:
            # pylint: disable=not-callable
            await device_updated_cb(self)

    async def sync(self, wait_for_result=False):
        """Read states of device from KNX bus."""
        for remote_value in self._iter_remote_values():
            await remote_value.read_state(wait_for_result=wait_for_result)

    async def process(self, telegram):
        """Process incoming telegram."""
        if telegram.telegramtype == TelegramType.GROUP_WRITE:
            await self.process_group_write(telegram)
        elif telegram.telegramtype == TelegramType.GROUP_RESPONSE:
            await self.process_group_response(telegram)
        elif telegram.telegramtype == TelegramType.GROUP_READ:
            await self.process_group_read(telegram)

    async def process_group_read(self, telegram):
        """Process incoming GroupValueRead telegrams."""
        # The dafault is, that devices dont answer to group reads

    async def process_group_response(self, telegram):
        """Process incoming GroupValueResponse telegrams."""
        # Per default mapped to group write.
        await self.process_group_write(telegram)

    async def process_group_write(self, telegram):
        """Process incoming GroupValueWrite telegrams."""
        # The dafault is, that devices dont process group writes

    def get_name(self):
        """Return name of device."""
        return self.name

    def get_unique_id(self):
        """Return unique ID of device."""
        return self.unique_id

    def has_group_address(self, group_address):
        """Test if device has given group address."""
        for remote_value in self._iter_remote_values():
            if remote_value.has_group_address(group_address):
                return True
        return False

    async def do(self, action):
        """Execute 'do' commands."""
        # pylint: disable=invalid-name
        self.xknx.logger.info(
            "'do()' not implemented for action '%s' of %s",
            action,
            self.__class__.__name__,
        )

    def __eq__(self, other):
        """Compare for quality."""
        return self.__dict__ == other.__dict__
