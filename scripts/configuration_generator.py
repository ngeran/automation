# generator.py
# This script generates network device configurations by combining YAML data with Jinja2 templates.
# It allows users to select from a dynamic list of configuration types (e.g., BGP, OSPF) defined in a YAML file,
# checks for matching data files, and produces a text file output for use in other scripts (e.g., apply_config.py).

import yaml  # Used to parse YAML files for data and template lists
from jinja2 import Environment, FileSystemLoader  # Jinja2 for templating configuration files
import os  # For checking file existence

def load_templates_list(file_path="../data/templates_list.yml"):
    """Load the list of available configuration options from a YAML file."""
    # Purpose: Reads templates/templates_list.yml to get a dynamic list of configuration types
    # (e.g., bgp_config, ospf_config) with their descriptions.
    try:
        with open(file_path, "r") as file:
            templates_data = yaml.safe_load(file)  # Safely load YAML content
        return templates_data["configurations"]  # Return the list under 'configurations' key
    except FileNotFoundError:
        # Handle case where the templates list file is missing
        print(f"Error: {file_path} not found in data directory.")
        return []
    except yaml.YAMLError as yaml_syntax_error:
        # Handle invalid YAML syntax in the file
        print(f"Error: Invalid YAML file format in {file_path} - {yaml_syntax_error}")
        return []

def get_user_selection(configurations):
    """Prompt the user to choose a configuration type from the available list."""
    # Purpose: Displays the list of configurations (e.g., '1: bgp_config - Configure BGP routing')
    # and returns the user's selected configuration name (e.g., 'bgp_config').
    if not configurations:
        # If no configurations are loaded, exit early
        print("No configurations available. Exiting.")
        return None

    # Show the numbered list of options with descriptions
    print("\nAvailable device configuration options:")
    for idx, config in enumerate(configurations, 1):
        print(f"{idx}: {config['description']}")

    # Loop until a valid selection is made
    while True:
        choice = input("\nSelect a configuration by number: ").strip()
        try:
            choice_idx = int(choice) - 1  # Convert input to zero-based index
            if 0 <= choice_idx < len(configurations):
                return configurations[choice_idx]["template_data"]  # Return the chosen config name
            print(f"Please enter a number between 1 and {len(configurations)}.")
        except ValueError:
            # Handle non-numeric input
            print("Invalid input. Please enter a number.")

def check_data_exists(config_name, data_dir="../data"):
    """Verify that the YAML data file for the selected configuration exists."""
    # Purpose: Ensures the data file (e.g., data/bgp_config.yml) is present before proceeding.
    data_file = f"{data_dir}/{config_name}.yml"  # Construct the expected file path
    if os.path.exists(data_file):
        return data_file  # Return the path if file exists
    # If the file is missing, notify the user and return None
    print(f"Error: Data file {data_file} not found.")
    return None

def generate_config(config_name, data_file, templates_dir="../templates", output_dir="../output"):
    """Generate a configuration file by merging YAML data with a Jinja2 template."""
    # Purpose: Takes a config name (e.g., 'bgp_config'), loads its data (bgp_config.yml) and
    # template (bgp_config.j2), renders them together, and saves the result (bgp_config.txt).
    template_file = f"{config_name}.j2"  # Template file in templates/ directory
    output_file = f"{output_dir}/{config_name}.txt"  # Output file in output/ directory

    try:
        # Step 1: Load the YAML data file
        with open(data_file, "r") as yaml_input:
            data = yaml.safe_load(yaml_input)  # Parse YAML into a Python dictionary

        # Step 2: Set up Jinja2 environment and load the template
        env = Environment(loader=FileSystemLoader(templates_dir))  # Look for templates in templates/
        template = env.get_template(template_file)  # Load the specific .j2 file

        # Step 3: Render the template with the YAML data
        config_output = template.render(data)  # Combine data and template into a string

        # Step 4: Save the rendered configuration to a text file
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        with open(output_file, "w") as config_file:
            config_file.write(config_output)

        # Notify user of success
        print(f"\nConfiguration generated successfully and saved to {output_file}")

        # Step 5: Display the generated configuration for verification
        with open(output_file, "r") as generated_file:
            print("\nGenerated Configuration:")
            print(generated_file.read())

        return output_file

    except FileNotFoundError as e:
        # Handle missing template or data files
        print(f"Error: Could not find file - {e}")
    except yaml.YAMLError as e:
        # Handle invalid YAML syntax in the data file
        print(f"Error: Invalid YAML format - {e}")
    except Exception as e:
        # Catch any other unexpected errors
        print(f"Error: Something went wrong - {e}")

def generate_configuration():
    """Main function to orchestrate the configuration generation process."""
    # Step 1: Load the list of available configurations
    configurations = load_templates_list()
    if not configurations:
        return  None # Exit if loading fails

    # Step 2: Get the user's configuration choice
    config_name = get_user_selection(configurations)
    if not config_name:
        return  None # Exit if no valid selection

    # Step 3: Check for the corresponding data file
    data_file = check_data_exists(config_name)
    if not data_file:
        return None # Exit if data file is missing

    # Step 4: Generate and save the configuration file path
    return generate_config(config_name, data_file)

if __name__ == "__main__":
    # Entry point: Run the script only if executed directly (not imported)
    generate_configuration()
