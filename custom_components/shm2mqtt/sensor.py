"""The shm2mqtt component for reading SHM2 data via MQTT"""
from __future__ import annotations

import copy
import logging

from homeassistant.components import mqtt
from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import async_get as async_get_dev_reg
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import slugify

from .common import Shm2BaseEntity

# Import global values.
from .const import (
    MQTT_ROOT_TOPIC,
    SERIAL,
    SENSORS_SHM2,
    Shm2SensorEntityDescription,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, config: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up sensors for SHM2"""

    integrationUniqueID = config.unique_id
    mqttRoot = config.data[MQTT_ROOT_TOPIC]
    serial = config.data[SERIAL]

    sensorList = []
    # Create all global sensors.
    global_sensors = copy.deepcopy(SENSORS_SHM2)
    for description in global_sensors:
        description.mqttTopicCurrentValue = f"{mqttRoot}/{serial}/{description.key}"
        _LOGGER.debug("mqttTopic: %s", description.mqttTopicCurrentValue)
        sensorList.append(
            Shm2Sensor(
                uniqueID=integrationUniqueID,
                description=description,
                device_friendly_name=integrationUniqueID,
                mqtt_root=mqttRoot,
            )
        )
    async_add_entities(sensorList)


class Shm2Sensor(Shm2BaseEntity, SensorEntity):
    """Representation of an SHM2 sensor that is updated via MQTT"""

    entity_description: Shm2SensorEntityDescription

    def __init__(
        self,
        uniqueID: str | None,
        device_friendly_name: str,
        mqtt_root: str,
        description: Shm2SensorEntityDescription,
    ) -> None:
        """Initialize the sensor and the SHM2 device"""
        super().__init__(
            device_friendly_name=device_friendly_name,
            mqtt_root=mqtt_root,
        )

        self.entity_description = description
        self._attr_unique_id = slugify(f"{uniqueID}-{description.name}")
        self.entity_id = f"sensor.{uniqueID}-{description.name}"
        self._attr_name = description.name

    async def async_added_to_hass(self) -> None:
        """Subscribe to MQTT events"""

        @callback
        def message_received(message):
            """Handle new MQTT messages"""
            self._attr_native_value = message.payload

            # Convert data if a conversion function is defined
            if self.entity_description.value_fn is not None:
                self._attr_native_value = self.entity_description.value_fn(
                    self._attr_native_value
                )

            # Map values as defined in the value map dict.
            if self.entity_description.valueMap is not None:
                try:
                    self._attr_native_value = self.entity_description.valueMap.get(
                        int(self._attr_native_value)
                    )
                except ValueError:
                    self._attr_native_value = self._attr_native_value

            # If MQTT message contains version --> set sw_version of the device
            elif "version" in self.entity_id:
                device_registry = async_get_dev_reg(self.hass)
                device = device_registry.async_get_device(
                    self.device_info.get("identifiers")
                )
                device_registry.async_update_device(
                    device.id, sw_version=message.payload
                )
                # device_registry.async_update_device

            # Update entity state with value published on MQTT.
            self.async_write_ha_state()

        # Subscribe to MQTT topic and connect callack message
        await mqtt.async_subscribe(
            self.hass,
            self.entity_description.mqttTopicCurrentValue,
            message_received,
            1,
        )
