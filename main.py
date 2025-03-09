# main.py
# Purpose: Orchestrates configuration generation and application by combining modular scripts.
#          Runs from the root directory and imports scripts from the 'scripts/' directory.

# Import functions from scripts in the scripts/ directory
from scripts.configuration_generator import generate_configuration
from scripts.connect_to_host import apply_config_to_all

def main():
    """
    Main function to generate a configuration and apply it to devices.

    Steps:
        1. Generate the configuration file using configuration_generator.
        2. Apply the configuration to all devices using connect_to_host.
    """
    # Step 1: Generate the configuration
    config_file = generate_configuration()
    if not config_file:
        print("Configuration generation failed. Exiting.")
        return

    # Step 2: Apply the configuration to all devices
    apply_config_to_all(config_file)

if __name__ == "__main__":
    # Entry point: Run the script only if executed directly
    main()
