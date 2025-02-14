import yaml
from jinja2 import Environment, FileSystemLoader

# Load YAML data
with open("bgp_data.yaml", "r") as yaml_file:
    data = yaml.safe_load(yaml_file)

# Load Jinja2 template
env = Environment(loader=FileSystemLoader("."))  # Load templates from the current directory
template = env.get_template("bgp_template.j2")

# Render configuration
bgp_config = template.render(data)

# Save the generated configuration to a file
with open("bgp_config.txt", "w") as config_file:
    config_file.write(bgp_config)

print("BGP configuration generated successfully and saved to bgp_config.txt")
