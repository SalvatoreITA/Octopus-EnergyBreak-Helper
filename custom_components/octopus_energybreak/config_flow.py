import voluptuous as vol
from homeassistant import config_entries
from homeassistant.components.sensor import DOMAIN as SENSOR_DOMAIN
from homeassistant.helpers import selector
from .const import DOMAIN, CONF_SOURCE_SENSOR

class OctopusEBConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1
    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="Octopus Energy Break", data=user_input)
        
        data_schema = vol.Schema({
            vol.Required(CONF_SOURCE_SENSOR): selector.EntitySelector(
                selector.EntitySelectorConfig(domain=SENSOR_DOMAIN)
            )
        })
        return self.async_show_form(step_id="user", data_schema=data_schema)