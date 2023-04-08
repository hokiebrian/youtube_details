import asyncio
import json
import logging
from aiohttp import ClientSession
from homeassistant.helpers.entity import Entity
from homeassistant.const import CONF_API_KEY
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    sensor = YouTubeSearchSensor(config_entry)
    async_add_entities([sensor], True)
    
class YouTubeSearchSensor(Entity):

    _LOGGER = logging.getLogger(__name__)

    def __init__(self, config_entry):
        self.api_key = config_entry.data[CONF_API_KEY]
        self._state = None
        self._attributes = {}

    async def async_added_to_hass(self):
        self.hass.services.async_register(DOMAIN, "search_video", self.search_video)

    async def async_will_remove_from_hass(self):
        self.hass.services.async_remove(DOMAIN, "search_video")

    async def search_video(self, call):
        video_title = call.data.get("video_title")
        url_search = 'https://www.googleapis.com/youtube/v3/search?part=snippet&type=video&maxResults=1&q={}&key={}'.format(video_title, self.api_key)
        url_video_details = 'https://www.googleapis.com/youtube/v3/videos?part=snippet,statistics&id={}&key={}'

        async with ClientSession() as session:
            async with session.get(url_search) as response_search:
                search_data = await response_search.json()
                if 'items' not in search_data:
                    self._state = "No Results Found"
                    self._attributes = {}
                    self.async_write_ha_state()
                    self._LOGGER.error(f"Search Error{video_title}")
                    return

                video_id = search_data['items'][0]['id']['videoId']
                self._LOGGER.debug(f"Search {video_title} results {video_id}")

            async with session.get(url_video_details.format(video_id, self.api_key)) as response_video_details:
                video_details_data = await response_video_details.json()
                if 'items' not in video_details_data:
                    self._state = None
                    self._attributes = {}
                    self.async_write_ha_state()
                    self._LOGGER.error(f"No Data Found for {video_id}")
                    return

                response_video_details = video_details_data['items'][0]
                self._LOGGER.debug(f"Search {video_id} results {response_video_details}")

            self._state = video_id
            self._attributes = response_video_details
            self.async_write_ha_state()

    @property
    def name(self):
        return "YouTube Search"

    @property
    def state(self):
        return self._state
    
    @property
    def unique_id(self):
        return f"YouTubeSearch{self.api_key[:7]}"

    @property
    def extra_state_attributes(self):
        return self._attributes
