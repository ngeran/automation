import os
import yaml
from jinja2 import Environment, FileSystemLoader


def generate_config(config_file, template_file="templates/juniper_config.j2"):
    """Generates router config from YAML and Jinja2 template."""

    try:
        with open(config_file, "r") as f:
            config_data = yaml.safe_load(f)
    except FileNotFoundError:
        print(f"Error: Configuration file '{config_file}' not found.")
        return
    except yaml.YAMLError as e:
        print(f"Error parsing YAML file: {e}")
        return

    router_name = config_data.get("router_name")
    router_id = config_data.get("router_id")
    asn = config_data.get("asn")
    neighbors = config_data.get("neighbors", {})
    interfaces = config_data.get("interfaces", [])
    router_type = config_data.get("router_type", "internal")  # Default to internal BGP

    if not all([router_name, router_id, asn]):
        print("Error: router_name, router_id, and asn are required in the YAML file.")
        return

    template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template(os.path.basename(template_file))

    context = {
        "router_name": router_name,
        "router_id": router_id,
        "asn": asn,
        "neighbors": neighbors,
        "interfaces": interfaces,
        "router_type": router_type,  # Pass the router type to the template
    }

    config = template.render(context)

    output_filename = f"{router_name}_config.juniper"
    with open(output_filename, "w") as f:
        f.write(config)

    print(f"Configuration written to {output_filename}")


# Example usage (no changes needed here):
config_file = "router_config.yaml"
generate_config(config_file)
