""" Config Flow for YouTube Search Component """
import aiohttp
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers import config_validation as cv
from .const import DOMAIN

YOUTUBE_API_URL = (
    "https://www.googleapis.com/youtube/v3/videos?id=Ks-_Mh1QhMc&part=id,snippet&key={}"
)


class YouTubeFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            api_key = user_input.get("api_key")

            success = await self.test_youtube_api_key(api_key)
            if success:
                await self.async_set_unique_id(user_input["api_key"][:7])
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title="YouTube Search",
                    data={"api_key": api_key},
                )

            errors[
                "api_key"
            ] = "Failed to connect to YouTube API with the provided API key."

        return self.async_show_form(
            step_id="user",
            data_schema=self.schema,
            errors=errors,
        )

    async def test_youtube_api_key(self, api_key):
        url = YOUTUBE_API_URL.format(api_key)
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                response_data = await response.json()

                if response.status != 200 or "error" in response_data:
                    return False

                return True

    @property
    def schema(self):
        return vol.Schema({vol.Required("api_key"): cv.string})
