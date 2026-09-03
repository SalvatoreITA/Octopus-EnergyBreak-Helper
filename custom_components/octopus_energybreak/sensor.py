import logging
from datetime import timedelta
from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.util import dt as dt_util
from homeassistant.components.recorder import get_instance, history
from homeassistant.helpers.event import async_track_state_change_event
from .const import DOMAIN, EVENT_UPDATE_WINDOW, CONF_SOURCE_SENSOR

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    source_sensor = entry.data.get(CONF_SOURCE_SENSOR)
    
    # 1. Crea la Baseline
    baseline_sensor = OctopusEBBaselineSensor(hass, source_sensor)
    
    # 2. Registra tutti i sensori
    async_add_entities([
        baseline_sensor,
        OctopusEBTargetSensor(hass, baseline_sensor, "Obiettivo 1 Euro", "target_1_euro", 0.8, "mdi:piggy-bank"),
        OctopusEBTargetSensor(hass, baseline_sensor, "Obiettivo 3 Euro", "target_3_euro", 0.5, "mdi:cash-multiple"),
        OctopusEBLiveConsumptionSensor(hass, source_sensor)
    ], True)


# ==============================================================================
# SENSORE 1: BASELINE (Media Storica 10 Giorni)
# ==============================================================================
class OctopusEBBaselineSensor(SensorEntity):
    def __init__(self, hass, source_sensor):
        self.hass = hass
        self._source_sensor = source_sensor
        self._attr_name = "Baseline EnergyBreak 10gg"
        self._attr_unique_id = "octopus_eb_baseline"
        self._attr_native_unit_of_measurement = "kWh"
        self._attr_device_class = SensorDeviceClass.ENERGY
        self._attr_icon = "mdi:chart-bell-curve"
        self._state = 0.0

    async def async_added_to_hass(self):
        self.hass.bus.async_listen(EVENT_UPDATE_WINDOW, self._handle_window_update)

    async def _handle_window_update(self, event):
        await self.async_update_ha_state(force_refresh=True)

    @property
    def state(self):
        return self._state

    async def async_update(self):
        now = dt_util.now()
        days_data = []
        is_target_weekend = now.weekday() >= 5
        
        start_entity = self.hass.states.get("time.inizio_eb")
        end_entity = self.hass.states.get("time.fine_eb")
        start_time = start_entity.state if start_entity else "21:00:00"
        end_time = end_entity.state if end_entity else "22:00:00"

        def fetch_history(start_dt, end_dt):
            return history.state_changes_during_period(self.hass, start_dt, end_dt, self._source_sensor, include_start_time_state=True)

        days_checked = 1
        valid_days_found = 0

        while valid_days_found < 10 and days_checked <= 30:
            target_date = now - timedelta(days=days_checked)
            is_past_weekend = target_date.weekday() >= 5

            if is_target_weekend == is_past_weekend:
                start_dt = dt_util.parse_datetime(f"{target_date.date()} {start_time}")
                end_dt = dt_util.parse_datetime(f"{target_date.date()} {end_time}")

                if start_dt and end_dt:
                    states = await get_instance(self.hass).async_add_executor_job(fetch_history, start_dt, end_dt)
                    if self._source_sensor in states and len(states[self._source_sensor]) > 0:
                        try:
                            consumo = float(states[self._source_sensor][-1].state) - float(states[self._source_sensor][0].state)
                            if consumo >= 0:
                                days_data.append(consumo)
                        except ValueError:
                            pass
                valid_days_found += 1
            days_checked += 1

        self._state = round(sum(days_data) / len(days_data), 3) if days_data else 0.0


# ==============================================================================
# SENSORE 2 e 3: OBIETTIVI (Sconti 1€ e 3€)
# ==============================================================================
class OctopusEBTargetSensor(SensorEntity):
    def __init__(self, hass, baseline_sensor, name, object_id, multiplier, icon):
        self.hass = hass
        self._baseline_sensor = baseline_sensor
        self._attr_name = f"EnergyBreak {name}"
        self._attr_unique_id = f"octopus_eb_{object_id}"
        self._attr_native_unit_of_measurement = "kWh"
        self._attr_device_class = SensorDeviceClass.ENERGY
        self._attr_icon = icon
        self._multiplier = multiplier

    async def async_added_to_hass(self):
        self.hass.bus.async_listen(EVENT_UPDATE_WINDOW, self._handle_window_update)

    async def _handle_window_update(self, event):
        await self.async_update_ha_state(force_refresh=True)

    @property
    def state(self):
        return round(self._baseline_sensor.state * self._multiplier, 3)

# ==============================================================================
# SENSORE 4: CONSUMO IN TEMPO REALE (FIX AZZERAMENTO ISTANTANEO)
# ==============================================================================
class OctopusEBLiveConsumptionSensor(SensorEntity):
    def __init__(self, hass, source_sensor):
        self.hass = hass
        self._source_sensor = source_sensor
        self._attr_name = "EnergyBreak Consumo Live"
        self._attr_unique_id = "octopus_eb_live_consumption"
        self._attr_native_unit_of_measurement = "kWh"
        self._attr_device_class = SensorDeviceClass.ENERGY
        self._attr_icon = "mdi:lightning-bolt"
        self._state = 0.0
        
        self._reference_value = None
        self._reference_date = None

    @property
    def state(self):
        return self._state

    async def async_added_to_hass(self):
        """Si mette in ascolto del contatore e dei cambi orario sulla card."""
        # 1. Ascolta i microscatti del contatore fisico
        self.async_on_remove(
            async_track_state_change_event(
                self.hass, [self._source_sensor], self._async_source_changed
            )
        )
        # 2. NOVITÀ: Ascolta se cambi orario o data dalla plancia e scatta subito!
        self.hass.bus.async_listen(EVENT_UPDATE_WINDOW, self._handle_window_update)

    async def _handle_window_update(self, event):
        """Forza un controllo immediato quando tocchi la card."""
        self._evaluate_state(None)

    async def _async_source_changed(self, event):
        """Si attiva quando il contatore principale fa uno scatto."""
        new_state = event.data.get("new_state")
        if new_state is None or new_state.state in ["unknown", "unavailable"]:
            return
        
        try:
            current_val = float(new_state.state)
        except ValueError:
            return

        self._evaluate_state(current_val)

    def _evaluate_state(self, current_val):
        """Il cervello del sensore che calcola o azzera la barra."""
        now = dt_util.now()
        
        # Lettura entità Data
        date_entity = self.hass.states.get("date.data_eb")
        if not date_entity or date_entity.state in ["unknown", "unavailable"]:
            return
            
        try:
            target_date = dt_util.parse_date(date_entity.state)
        except ValueError:
            return

        if target_date is None:
            return

        # Lettura entità Orari
        start_entity = self.hass.states.get("time.inizio_eb")
        end_entity = self.hass.states.get("time.fine_eb")
        
        start_str = start_entity.state if start_entity else "21:00:00"
        end_str = end_entity.state if end_entity else "22:00:00"

        start_time_obj = dt_util.parse_time(start_str)
        end_time_obj = dt_util.parse_time(end_str)

        if not start_time_obj or not end_time_obj:
            return

        # Costruzione orari blindati con fuso orario
        start_dt = now.replace(
            hour=start_time_obj.hour, minute=start_time_obj.minute, 
            second=0, microsecond=0
        )
        end_dt = now.replace(
            hour=end_time_obj.hour, minute=end_time_obj.minute, 
            second=0, microsecond=0
        )

        # LOGICA DI RESET ISTANTANEO (Se sei fuori dalla fascia, pialla tutto a 0)
        if now.date() != target_date or now < start_dt or now >= end_dt:
            if self._state != 0.0 or self._reference_value is not None:
                self._state = 0.0
                self._reference_value = None
                self.async_write_ha_state()
            return

        # LOGICA DI CALCOLO (Se sei dentro la fascia, aggiorna la barra)
        if start_dt <= now < end_dt and current_val is not None:
            if self._reference_value is None or self._reference_date != now.date():
                self._reference_value = current_val
                self._reference_date = now.date()
                self._state = 0.0
            else:
                self._state = round(current_val - self._reference_value, 3)
            
            self.async_write_ha_state()