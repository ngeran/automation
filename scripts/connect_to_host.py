# scripts/connect_to_host.py
# Purpose: Establishes SSH connections to Juniper SRX devices using PyEZ and applies configurations.
#          Provides reusable functions to load device data and manage connections.

from jnpr.junos import Device  # PyEZ library for Juniper device management
import yaml  # For parsing connection data from YAML
import os  # For file existence checks

def load_connection_data(file_path="../data/hosts.yml"):
    """
    Load connection details for devices from a YAML file.

    Args:
        file_path (str): Path to the connection.yml file (relative to scripts/ directory).

    Returns:
        dict: Parsed YAML data containing device connection details, or None if loading fails.
    """
    try:
        with open(file_path, "r") as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        print(f"Error: {file_path} not found.")
        return None
    except yaml.YAMLError as e:
        print(f"Error: Invalid YAML format in {file_path} - {e}")
        return None

def apply_config_to_device(host, user, password, config_file):
    """
    Apply a configuration file to a single Juniper SRX device.

    Args:
        host (str): IP address or hostname of the device.
        user (str): Username for SSH authentication.
        password (str): Password for SSH authentication.
        config_file (str): Path to the configuration file to apply.

    Returns:
        bool: True if configuration is applied successfully, False otherwise.
    """
    if not os.path.exists(config_file):
        print(f"Error: Configuration file {config_file} not found.")
        return False

    try:
        # Create PyEZ Device object and connect
        dev = Device(host=host, user=user, password=password)
        print(f"\nConnecting to {host} as {user}...")
        dev.open()
        print(f"Connected to {host} successfully!")

        # Load and apply the configuration
        with open(config_file, "r") as f:
            config_text = f.read()
        with dev.rpc.load_config(dev, config_text, format="set", action="merge"):
            print(f"Configuration applied to {host}.")

        # Commit the changes
        dev.commit()
        print(f"Changes committed on {host}.")

        # Close the connection
        dev.close()
        print(f"Connection to {host} closed.")
        return True

    except Exception as e:
        print(f"Error applying config to {host}: {e}")
        if 'dev' in locals() and dev.is_alive():
            dev.close()
        return False

def apply_config_to_all(config_file):
    """
    Apply the configuration to all devices listed in connection.yml.

    Args:
        config_file (str): Path to the configuration file to apply.
    """
    if not config_file:
        print("Error: No configuration file provided.")
        return

    # Load device connection data
    conn_data = load_connection_data()
    if not conn_data:
        return

    # Extract and validate devices list
    devices = conn_data.get("devices", [])
    if not devices or not isinstance(devices, list):
        print("Error: No valid 'devices' list found in connection.yml.")
        return

    # Apply config to each device
    for device in devices:
        host = device.get("host")
        user = device.get("user")
        password = device.get("password")

        if not all([host, user, password]):
            print("Skipping device: Missing required data (host, user, or password).")
            print("-" * 50)
            continue

        success = apply_config_to_device(host, user, password, config_file)
        print("-" * 50)
