from homeassistant import config_entries
from .const import DOMAIN
import aiohttp

class YouTubeFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            # Validate the user input against the expected schema
            try:
                self.schema(user_input)
            except vol.Invalid as e:
                errors[e.path[0]] = str(e)

            # Test the YouTube API with the user's API key
            api_key = user_input.get("api_key")
            success = await self.test_youtube_api_key(api_key)

            if not success:
                errors["base"] = "Failed to connect to YouTube API with the provided API key."

            if not errors:
                # The user input is valid and the API test passed, create a new config entry
                await self.async_set_unique_id(user_input["api_key"][:7])
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title="YouTube Search",
                    data={"api_key": user_input["api_key"]},
                )

        return self.async_show_form(
            step_id="user",
            data_schema=self.schema,
            errors=errors,
        )

    async def test_youtube_api_key(self, api_key):
        """Test the connection to the YouTube API using the provided API key."""
        url = f"https://www.googleapis.com/youtube/v3/videos?id=Ks-_Mh1QhMc&part=id,snippet&key={api_key}"

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                response_data = await response.json()

                if response.status != 200:
                    return False
                elif "error" in response_data:
                    return False
                else:
                    return True

    @property
    def schema(self):
        from homeassistant.helpers import config_validation as cv
        import voluptuous as vol
        return vol.Schema({vol.Required("api_key"): cv.string})