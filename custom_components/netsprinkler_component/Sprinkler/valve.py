
from ..const import (
    LOGGER
)

class Valve(object):
    def __init__(self, controller, index: int) -> None:
        LOGGER.info(f'[Valve:init] controller {type(controller)}')
        self._controller = controller
        self._index = index


    @property
    def is_master(self):
        return False

    @property
    def is_running(self):
        return False


    @property
    def index(self):
        return self._index

    @property
    def name(self):
        #LOGGER.debug(f'[Valve:name] returning name {self._controller.state["valves"][self._index]["name"]}')
        return self._controller.state['valves'][self._index]['name']

    @property
    def status(self):
        return 'idle'

    @property
    def id(self):
        return self._controller.state['valves'][self._index]['id']

    @property
    def enabled(self):
        enabled = self._controller.state['valves'][self._index]['enabled']
        #LOGGER.debug(f'[Valve:enabled] Is current valve enabled ? {enabled}')
        return enabled

    async def disable(self):
        id = self._controller.state['valves'][self._index]['id']
        LOGGER.debug(f'[Valve:disable] disabling valve {id}')
        await self._controller.disable_valve(id)

    async def enable(self):
        id = self._controller.state['valves'][self._index]['id']
        LOGGER.debug(f'[Valve:enable] enabling valve {id}')
        await self._controller.enable_valve(id)