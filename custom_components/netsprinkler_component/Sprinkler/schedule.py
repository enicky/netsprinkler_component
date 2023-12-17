
from ..const import (
    LOGGER
)

class Schedule:
    def __init__(self, controller, index: int) -> None:
        self._controller = controller
        self._index = index

    @property
    def name(self):
         return self._controller.state['schedules'][self._index]['name']

    @property
    def index(self):
        return self._controller.state['schedules'][self._index]['id']

    async def set_name(self, name):
        #TODO: add function in c# to change name of schedule
        id = self._controller.state['schedules'][self._index]['id']
        LOGGER.debug(f'[Schedule:set_name] setting name of "{self._index}" - {id} to {name}')
        await self._controller.set_schedule_name(name, id)
