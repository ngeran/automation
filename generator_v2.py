from flask import Flask, render_template, request
import yaml
from jinja2 import Environment, FileSystemLoader
from jnpr.junos import Device  # Import PyEZ

app = Flask(__name__)

# Data (can be loaded from a YAML file later)
interfaces = ["loopback", "management", "1g", "10g", "100g"]
protocols = ["bgp", "ospf"]

# Jinja2 environment
env = Environment(loader=FileSystemLoader("templates"))


@app.route("/", methods=["GET"])
def index():
    return render_template("form.html", interfaces=interfaces, protocols=protocols)


@app.route("/submit", methods=["POST"])
def submit():
    selected_interfaces = request.form.getlist("interface")
    selected_protocols = request.form.getlist("protocol")

    # Prepare data for YAML and Jinja2
    data = {
        "interfaces": selected_interfaces,
        "protocols": {
            proto: proto in selected_protocols for proto in protocols
        },  # Make protocols a dict for easy checking in template
    }

    # Save to YAML
    with open("data/config.yaml", "w") as f:
        yaml.dump(data, f)

    # Render Jinja2 templates
    interface_template = env.get_template("interface.j2")
    interface_config = interface_template.render(interfaces=selected_interfaces)

    protocol_template = env.get_template("protocol.j2")
    protocol_config = protocol_template.render(protocols=data["protocols"])

    # Combine configurations (you might want better logic here)
    final_config = interface_config + "\n" + protocol_config

    # Juniper PyEZ configuration (replace with your details)
    try:
        with Device(host="your_router_ip", user="your_username", password="your_password") as dev:
            dev.open()  # Open connection
            dev.load(config_str=final_config, format="set")  # Load the config
            dev.commit()  # Commit changes
            return "Configuration applied successfully!"
    except Exception as e:
        return f"Error: {e}"


if __name__ == "__main__":
    app.run(debug=True)
