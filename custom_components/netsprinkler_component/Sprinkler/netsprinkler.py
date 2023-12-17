import datetime
import aiohttp

from ..const import LOGGER
from .valve import Valve
from .schedule import Schedule

class NETSprinkler():
    def __init__(self, url, opts) -> None:
        LOGGER.info(f'[NETSprinkler] ctor.. url : {url}')
        self.url = url
        self.opts = opts
        self._http_client = None
        self._state = {}
        self._valves = {}
        self._schedules= {}
        self._current_draw = 0
        self._enabled = True
        self.last_reboot_time = ''

    @property
    def valves(self):
        """return valves"""
        return self._valves

    @property
    def schedules(self):
        """"return schedules"""
        return self._schedules

    @property
    def state(self):
        return self._state

    @property
    def hardware_version_name(self):
        return 'NETSprinkler'
    @property
    def firmware_version_name(self):
        return 'Pi'
    @property
    def hardware_type_name(self):
        return 'AC'
    @property
    def firmware_minor_version(self):
        return '1.0.0'

    @property
    def current_draw(self):
        return self._current_draw

    @property
    def device_time(self):
        return self._timestamp_to_utc(self._device_time)

    @property
    def enabled(self):
        return self._enabled

    async def enable(self):
        self._enabled = True

    async def disable(self):
        self._enabled = False
        logPrefix = '[NETSprinkler:disable]'
        LOGGER.debug(f'{logPrefix} Start disabling ')
        if self._http_client is None:
            self.session_start()

    async def refresh(self):
        logPrefix = '[netsprinkler:refresh]'
        self._content = self._state =  await self._refresh_state()
        self._last_refresh_time = int(round(datetime.datetime.now().timestamp()))
        self._device_time = self._content['deviceTime']

        for i, _ in enumerate(self._content['valves']):
            #LOGGER.info(f'{logPrefix} enumerate {i}')
            if i not in self._valves:
                self._valves[i] = Valve(self, i)

        for i, _ in enumerate(self._content['schedules']):
            #LOGGER.info(f'{logPrefix} enumerate schedule {i}')
            if i not in self._schedules:
                self._schedules[i] = Schedule(self, i)

        return True

    async def enable_valve(self, id):
        logPrefix = '[NETSprinkler:enable_valve]'
        LOGGER.debug(f'{logPrefix} Start enabling valve')
        data = {
            "valveId" : id,
            "enableValve": True
        }
        return await self.callEnableValveWithData(data)

    async def callEnableValveWithData(self, data):
        logPrefix = '[NETSprinkler:callEnableValveWithData]'
        if self._http_client is None:
            self.session_start()

        timeout = aiohttp.ClientTimeout(total=60)
        headers = {"Accept": "*/*", "Connection": "keep-alive", "Content-Type":"application/json"}
        url = f'{self.url}/api/Valve/EnableValve'
        LOGGER.debug(f'{logPrefix} Start making call to "{url}"')

        try:
            async with self._http_client.post(
                    url, timeout=timeout, headers=headers,json=data
                ) as resp:
                    LOGGER.debug(f'{logPrefix} call finished and returned data {resp}')
                    content = await resp.json(
                        encoding="UTF-8", content_type="application/json"
                    )
                    LOGGER.info(f'{logPrefix} result : {content}')
                    return content
        except aiohttp.ClientConnectionError as exc:
            raise ValueError("Cannot connect to controller") from exc
        except ConnectionError as exc:
            raise ValueError("Cannot connect to controller") from exc

    async def disable_valve(self, id):
        logPrefix = '[NETSprinkler:disable_valve]'
        LOGGER.debug(f'{logPrefix} Start disabling valve')
        data = {
            "valveId" : id,
            "enableValve": False
        }
        return await self.callEnableValveWithData(data)

    async def set_schedule_name(self, name, id):
        logPrefix = '[NETSprinkler:set_schedule_name]'
        LOGGER.debug(f'{logPrefix} Start setting schedule name of id {id}')
        data = {
            "scheduleId": id,
            "name": name
        }
        if self._http_client is None:
            self.session_start()

        timeout = aiohttp.ClientTimeout(total=60)
        headers = {"Accept": "*/*", "Connection": "keep-alive", "Content-Type":"application/json"}
        url = f'{self.url}/api/Scheduler/SetName'
        LOGGER.debug(f'{logPrefix} Start making call to "{url}"')

        try:
            async with self._http_client.post(
                    url, timeout=timeout, headers=headers,json=data
                ) as resp:
                    LOGGER.debug(f'{logPrefix} call finished and returned data {resp}')
                    content = await resp.json(
                        encoding="UTF-8", content_type="application/json"
                    )
                    LOGGER.info(f'{logPrefix} result : {content}')
                    return content
        except aiohttp.ClientConnectionError as exc:
            raise ValueError("Cannot connect to controller") from exc
        except ConnectionError as exc:
            raise ValueError("Cannot connect to controller") from exc



    def _timestamp_to_utc(self, timestamp):
        if timestamp is None:
            return None
        offset = 0 #(self._get_option("tz") - 48) * 15 * 60
        return timestamp if timestamp == 0 else timestamp - offset

    def session_start(self):
        LOGGER.debug(f'[NETSprinkler:session_start] start client and http client')
        client = aiohttp.ClientSession()
        self._http_client = client

    async def session_close(self):
        if self._http_client is not None and "session" not in self._opts:
            await self._http_client.close()
            self._http_client = None

    async def _refresh_state(self):
        logPrefix = '[NETSprinkler:_refresh_state]'
        LOGGER.debug(f'{logPrefix} Start refreshing data from sprinkler')
        if self._http_client is None:
            self.session_start()

        timeout = aiohttp.ClientTimeout(total=60)
        headers = {"Accept": "*/*", "Connection": "keep-alive", "Content-Type":"application/json"}

        auth = None
        verify_ssl = None

        url = f'{self.url}/api/Settings/all'
        LOGGER.debug(f'{logPrefix} Start making call to "{url}"')
        try:
            async with self._http_client.get(
                    url, timeout=timeout, headers=headers, verify_ssl=verify_ssl, auth=auth
                ) as resp:
                    LOGGER.debug(f'{logPrefix} call finished and returned data {resp}')
                    content = await resp.json(
                        encoding="UTF-8", content_type="application/json"
                    )
                    LOGGER.info(f'{logPrefix} result : {content}')

                    # if len(content) == 1:
                    #     if "result" in content:
                    #         if content["result"] == 2:
                    #             raise OpenSprinklerAuthError("Invalid password")
                    #         elif content["result"] > 2:
                    #             raise OpenSprinklerApiError(
                    #                 f"Error code: {content['result']}", content["result"]
                    #             )
                    #     elif "fwv" in content:x
                    #         raise OpenSprinklerAuthError("Invalid password")
                    return content
        except aiohttp.ClientConnectionError as exc:
            raise ValueError("Cannot connect to controller") from exc
        except ConnectionError as exc:
            raise ValueError("Cannot connect to controller") from exc