# scripts/connect_to_host.py
# Purpose: Manages SSH/NETCONF connections to Juniper devices using PyEZ.

from jnpr.junos import Device
import yaml
import logging

logger = logging.getLogger(__name__)

def load_connection_data(file_path="./data/hosts.yml"):
    """Load device connection details from YAML."""
    try:
        with open(file_path, "r") as file:
            data = yaml.safe_load(file)
        devices = data.get("devices", [])
        if not devices or not isinstance(devices, list):
            raise ValueError("No valid 'devices' list in '{file_path}'")
        return devices
    except FileNotFoundError as e:
        logger.error(f"Connection file not found: {e}")
        raise
    except yaml.YAMLError as e:
        logger.error(f"Invalid YAML in {file_path}: {e}")
        raise
    except ValueError as e:
        logger.error(f"Connection data invalid: {e}")
        raise

def connect_to_device(host, user, password):
    """Establish a connection to a Juniper device."""
    try:
        dev = Device(host=host, user=user, password=password)
        logger.info(f"Connecting to {host} as {user}...")
        dev.open()
        logger.info(f"Connected to {host}")
        return dev
    except Exception as e:
        logger.error(f"Failed to connect to {host}: {e}")
        raise

def disconnect_from_device(dev):
    """Close the connection to a Juniper device."""
    if dev and dev.is_alive():
        try:
            dev.close()
            logger.info(f"Disconnected from {dev.hostname or dev.host}")
        except Exception as e:
            logger.error(f"Error disconnecting from {dev.hostname or dev.host}: {e}")
