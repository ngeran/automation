# scripts/configuration_generator.py
# Purpose: Generates Juniper device configurations using YAML data and Jinja2 templates.

import yaml
from jinja2 import Environment, FileSystemLoader
import os
import logging

logger = logging.getLogger(__name__)  # Use logger configured in main.py

def load_templates_list(file_path="./data/templates_list.yml"):
    """Load available configuration templates from a YAML file."""
    try:
        with open(file_path, "r") as file:
            templates_data = yaml.safe_load(file)
        return templates_data["configurations"]
    except FileNotFoundError as e:
        logger.error(f"Template list file not found: {e}")
        raise
    except yaml.YAMLError as e:
        logger.error(f"Invalid YAML in {file_path}: {e}")
        raise

def get_user_selection(configurations):
    """Prompt user to select a configuration type."""
    if not configurations:
        logger.warning("No configurations available.")
        return None

    print("\nAvailable device configuration options:")
    for idx, config in enumerate(configurations, 1):
        print(f"{idx}: {config['description']}")

    while True:
        choice = input("\nSelect a configuration by number: ").strip()
        try:
            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(configurations):
                return configurations[choice_idx]["template_data"]
            print(f"Please enter a number between 1 and {len(configurations)}.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def check_data_exists(config_name, data_dir="./data"):
    """Verify the YAML data file exists."""
    data_file = f"{data_dir}/{config_name}.yml"
    if os.path.exists(data_file):
        return data_file
    logger.error(f"Data file not found: {data_file}")
    raise FileNotFoundError(f"Data file {data_file} not found")

def generate_config(config_name, data_file, templates_dir="./templates", output_dir="./generated_configurations"):
    """Generate a config file by merging YAML data with a Jinja2 template."""
    template_file = f"{config_name}.j2"
    output_file = f"{output_dir}/{config_name}.txt"

    try:
        with open(data_file, "r") as yaml_input:
            data = yaml.safe_load(yaml_input)

        env = Environment(loader=FileSystemLoader(templates_dir))
        template = env.get_template(template_file)
        config_output = template.render(data)

        os.makedirs(output_dir, exist_ok=True)
        with open(output_file, "w") as config_file:
            config_file.write(config_output)

        logger.info(f"Configuration generated: {output_file}")
        with open(output_file, "r") as generated_file:
            logger.debug(f"Generated config content:\n{generated_file.read()}")
        return output_file

    except FileNotFoundError as e:
        logger.error(f"File not found during config generation: {e}")
        raise
    except yaml.YAMLError as e:
        logger.error(f"Invalid YAML format: {e}")
        raise
    except Exception as e:
        logger.error(f"Config generation failed: {e}")
        raise

def generate_configuration():
    """Orchestrate configuration generation."""
    try:
        configurations = load_templates_list()
        config_name = get_user_selection(configurations)
        if not config_name:
            return None
        data_file = check_data_exists(config_name)
        return generate_config(config_name, data_file)
    except Exception as e:
        logger.error(f"Configuration generation failed: {e}")
        return None
