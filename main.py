# main.py
# Purpose: Orchestrates Juniper device configuration updates with optimized error handling.

import os
import logging
from scripts.configuration_generator import generate_configuration
from scripts.connect_to_host import load_connection_data
from scripts.configure_host import apply_config_to_all

# Configure logging with directory creation
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)  # Create logs/ if it doesn’t exist
logging.basicConfig(
    filename=os.path.join(log_dir, "config_script.log"),
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def main():
    """Main function to manage Juniper device configuration updates."""
    try:
        # Step 1: Generate configuration
        print("Step 1: Generating configuration...")
        logger.info("Starting configuration generation")
        config_file = generate_configuration()
        if not config_file:
            logger.error("Configuration generation failed")
            return

        # Load devices
        devices = load_connection_data()
        logger.info(f"Loaded {len(devices)} devices")

        # Steps 2-4: Connect, backup, apply
        print("\nStep 2: Connecting to devices...")
        print("Step 3: Backing up configurations...")
        print("Step 4: Applying configurations...")
        apply_config_to_all(devices, config_file)

        logger.info("Configuration process completed successfully")
    except Exception as e:
        logger.error(f"Main process failed: {e}")

if __name__ == "__main__":
    main()
