import asyncio
from xknx import XKNX, Light

async def main():
    xknx = XKNX()
    await xknx.start()

    light = Light(xknx,
                  name='TestLight2',
                  group_address_switch='1/0/12',
                  group_address_dimm='1/0/13',
                  group_address_brightness='1/0/14')

    for i in [0, 31, 63, 95, 127, 159, 191, 223, 255]:
        light.set_brightness(i)
        await asyncio.sleep(1)

    light.set_off()

    await xknx.stop()


# pylint: disable=invalid-name
loop = asyncio.get_event_loop()
loop.run_until_complete(main())
loop.close()