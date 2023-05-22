"""Module for transforming sensor descriptions into entity descriptions."""

import yaml
from dataclasses import dataclass
from enum import Enum

device_class_to_enum = {
    "power": "SensorDeviceClass.POWER",
    "apparent_power": "SensorDeviceClass.APPARENT_POWER",
    "reactive_power": "SensorDeviceClass.REACTIVE_POWER",
    "temperature": "SensorDeviceClass.TEMPERATURE",
    "current": "SensorDeviceClass.CURRENT",
    "voltage": "SensorDeviceClass.VOLTAGE",
    "energy": "SensorDeviceClass.ENERGY",
    "frequency": "SensorDeviceClass.FREQUENCY",
    "duration": "SensorDeviceClass.DURATION",
}


class SensorDeviceClass(Enum):
    """Enumeration for sensor device classes."""

    POWER = "power"
    TEMPERATURE = "temperature"
    CURRENT = "current"
    VOLTAGE = "voltage"
    FREQUENCY = "frequency"


unit_to_enum = {
    "W": "UnitOfPower.WATT",
    "°C": "UnitOfTemperature.CELSIUS",
    "A": "UnitOfElectricCurrent.AMPERE",
    "V": "UnitOfElectricPotential.VOLT",
    "kW": "UnitOfPower.KILO_WATT",
    "kWh": "UnitOfEnergy.KILO_WATT_HOUR",
    "VA": "UnitOfApparentPower.VOLT_AMPERE",
    "var": "UnitOfPower.POWER_VOLT_AMPERE_REACTIVE",
    "kVAh": "",
    "kvarh": "",
    "kOhm": "",
    "s": "UnitOfTime.SECONDS",
    "Hz": "UnitOfFrequency.HERTZ",
    "%": "PERCENTAGE",
    "°": "DEGREE",
}


class UnitOfMeasurement(Enum):
    """Enumeration for units of measurement."""

    WATT = "W"
    CELSIUS = "°C"
    AMPERE = "A"
    VOLT = "V"


state_to_enum = {
    "measurement": "MEASUREMENT",
    "total": "TOTAL",
    "total_increasing": "TOTAL_INCREASING",
}


class SensorStateClass(Enum):
    """Enumeration for sensor state classes."""

    MEASUREMENT = "measurement"


@dataclass
class SmaSensorEntityDescription:
    """Data class for Sma sensor entity descriptions."""

    key: str
    name: str
    device_class: SensorDeviceClass
    native_unit_of_measurement: UnitOfMeasurement
    state_class: SensorStateClass
    entity_registry_enabled_default: bool
    icon: str


# Map of units to icons
unit_to_icon = {
    "W": "mdi:home-lightning-bolt-outline",
    "°C": "mdi:thermometer",
    "A": "mdi:flash",
    "V": "mdi:flash-outline",
    # Add other units here
}

# Open and read the YAML file
with open("input_data.yaml", "r") as f:
    input_data_list = yaml.safe_load(f)

descdict = []
for input_data in input_data_list:
    device_class = (
        device_class_to_enum[input_data.get("device_class", "")]
        if input_data.get("device_class")
        else None
    )
    unit_of_measurement = (
        unit_to_enum[input_data.get("unit_of_measurement")]
        if input_data.get("unit_of_measurement")
        else None
    )
    state_class = (
        state_to_enum[input_data.get("state_class", "")]
        if input_data.get("state_class")
        else None
    )
    icon = (
        unit_to_icon.get(
            input_data.get("unit_of_measurement"), input_data.get("icon", "")
        )
        if input_data.get("unit_of_measurement")
        else input_data.get("icon", "")
    )

    # Create SmaSensorEntityDescription
    description = SmaSensorEntityDescription(
        key=input_data["state_topic"],
        name=input_data["name"],
        device_class=device_class,
        native_unit_of_measurement=unit_of_measurement,
        state_class=state_class,
        entity_registry_enabled_default=False,
        icon=icon,
    )
    descdict.append(description)

for description in descdict:
    with open("output.txt", "a") as f:
        f.write("openwbSensorEntityDescription(\n")
        f.write(f'    key="{description.key}",\n')
        f.write(f'    name="{description.name}",\n')
        f.write(f"    device_class={description.device_class},\n")
        f.write(
            f"    native_unit_of_measurement={description.native_unit_of_measurement},\n"
        )
        f.write(f"    state_class=SensorStateClass.{description.state_class},\n")
        f.write("    entity_registry_enabled_default=False,\n")
        # If you have a function for value_fn, add here. If not, remove this line.
        f.write("    value_fn=lambda x: round(float(x)),\n")
        f.write(f'    icon="{description.icon}",\n')
        f.write("),\n")
