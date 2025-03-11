import yaml
import logging
from connect_to_host import is_reachable, connect_to_device
from route_monitor import RouteMonitor

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def load_config(config_file='hosts.yaml'):
    """
    Load device configuration from a YAML file.

    Args:
        config_file (str): Path to YAML configuration file

    Returns:
        dict: Configuration data if successful, None if error occurs
    """
    try:
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
        return config
    except Exception as e:
        logger.error(f"Error loading config file {config_file}: {str(e)}")
        return None

def main():
    """
    Main function to load configuration, connect to devices, and start monitoring.
    """
    # Load configuration from YAML file
    config = load_config()
    if not config or 'devices' not in config:
        logger.error("Invalid or missing configuration")
        return

    devices = config['devices']
    monitors = []

    # Process each device in the configuration
    for device_info in devices:
        hostname = device_info.get('hostname')
        username = device_info.get('username')
        password = device_info.get('password')
        interval = device_info.get('interval', 30)

        # Validate required parameters
        if not all([hostname, username, password]):
            logger.error(f"Missing required parameters for device: {device_info}")
            continue

        # Check if device is reachable
        if not is_reachable(hostname):
            logger.warning(f"Device {hostname} is not reachable, skipping...")
            continue

        # Attempt to connect to the device
        device = connect_to_device(hostname, username, password)
        if device:
            # Create and store monitor instance for connected device
            monitor = RouteMonitor(device, interval)
            monitors.append(monitor)

    # Check if any devices were successfully connected
    if not monitors:
        logger.error("No devices successfully connected")
        return

    logger.info(f"Starting monitoring for {len(monitors)} devices...")
    try:
        # Start monitoring (currently for first device only)
        # For multiple devices, consider adding threading
        monitors[0].monitor()
    finally:
        # Cleanup: close all device connections
        for monitor in monitors:
            if monitor.device:
                monitor.device.close()
                logger.info(f"Closed connection to {monitor.device.hostname}")

if __name__ == "__main__":
    main()
