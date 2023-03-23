from homeassistant import config_entries
from .const import DOMAIN

class YouTubeFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            await self.async_set_unique_id(user_input["api_key"])
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

    @property
    def schema(self):
        from homeassistant.helpers import config_validation as cv
        import voluptuous as vol

        return vol.Schema({vol.Required("api_key"): cv.string})
