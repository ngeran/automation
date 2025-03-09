# scripts/configure_host.py
# Purpose: Applies configurations to Juniper devices with validation and rollback.

import os
import re
import logging
from jnpr.junos.utils.config import Config

logger = logging.getLogger(__name__)

def validate_config_format(config_text):
    """Validate if the config is in Juniper 'set' format."""
    set_pattern = re.compile(r'^\s*set\s+', re.IGNORECASE | re.MULTILINE)
    if set_pattern.search(config_text):
        return True
    logger.error("Config lacks valid 'set' commands")
    return False

def apply_configuration(dev, config_file):
    """Apply a configuration to a Juniper device with rollback on failure."""
    if not os.path.exists(config_file):
        logger.error(f"Config file not found: {config_file}")
        raise FileNotFoundError(f"Config file {config_file} not found")

    try:
        with open(config_file, "r") as f:
            config_text = f.read()

        if not validate_config_format(config_text):
            raise ValueError("Invalid configuration format")

        with Config(dev, mode='exclusive') as cu:
            cu.load(config_text, format="set")
            logger.info(f"Configuration loaded on {dev.hostname or dev.host}")
            cu.commit_check()
            cu.commit()
            logger.info(f"Configuration committed on {dev.hostname or dev.host}")

        return True

    except Exception as e:
        logger.error(f"Configuration failed on {dev.hostname or dev.host}: {e}")
        try:
            with Config(dev, mode='exclusive') as cu:
                cu.rollback()
                logger.info(f"Rolled back changes on {dev.hostname or dev.host}")
        except Exception as rollback_e:
            logger.error(f"Rollback failed on {dev.hostname or dev.host}: {rollback_e}")
        raise

def apply_config_to_all(devices, config_file):
    """Apply config to all devices with detailed steps."""
    if not config_file:
        logger.error("No configuration file provided")
        return

    from scripts.connect_to_host import connect_to_device, disconnect_from_device
    from scripts.backup_host import backup_config

    for device in devices:
        host = device.get("host")
        user = device.get("user")
        password = device.get("password")

        if not all([host, user, password]):
            logger.warning(f"Skipping {host}: Missing credentials")
            print("-" * 50)
            continue

        try:
            print(f"\nStep 2: Connecting to {host}...")
            dev = connect_to_device(host, user, password)
            if not dev:
                continue

            print(f"Step 3: Backing up configuration for {host}...")
            backup_file = backup_config(dev)
            if not backup_file:
                disconnect_from_device(dev)
                continue

            print(f"Step 4: Applying configuration to {host}...")
            apply_configuration(dev, config_file)
            disconnect_from_device(dev)

        except Exception as e:
            logger.error(f"Processing failed for {host}: {e}")
            if 'dev' in locals():
                disconnect_from_device(dev)
        finally:
            print("-" * 50)
