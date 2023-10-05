""" YouTube Search Sensor """

import logging
from urllib.parse import quote
from aiohttp import ClientSession
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import Entity
from homeassistant.const import CONF_API_KEY
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)
YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search?part=snippet&type=video&maxResults=1&q={}&key={}"
YOUTUBE_VIDEO_DETAILS_URL = (
    "https://www.googleapis.com/youtube/v3/videos?part=snippet,statistics&id={}&key={}"
)


async def async_setup_entry(hass: HomeAssistant, config_entry, async_add_entities):
    sensor = YouTubeSearchSensor(config_entry)
    async_add_entities([sensor], True)


class YouTubeSearchSensor(Entity):
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
        video_title_encoded = quote(video_title)
        search_data = await self.fetch_data(
            YOUTUBE_SEARCH_URL.format(video_title_encoded, self.api_key)
        )
        if "items" not in search_data:
            self.update_state(
                "No Results Found", {}, f"Search Error Video Not Found {video_title}"
            )
            return

        video_id = search_data["items"][0]["id"]["videoId"]
        _LOGGER.debug("Search %s results %s", video_title, video_id)

        video_details_data = await self.fetch_data(
            YOUTUBE_VIDEO_DETAILS_URL.format(video_id, self.api_key)
        )
        if "items" not in video_details_data:
            self.update_state(None, {}, f"No Data Found for {video_id}")
            return

        response_video_details = video_details_data["items"][0]
        _LOGGER.debug("Search %s results %s", video_id, response_video_details)

        self.update_state(video_id, response_video_details)

    async def fetch_data(self, url):
        async with ClientSession() as session:
            async with session.get(url) as response:
                return await response.json()

    def update_state(self, state, attributes, log_msg=None):
        self._state = state
        self._attributes = attributes
        self.async_write_ha_state()
        if log_msg:
            _LOGGER.error(log_msg)

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
