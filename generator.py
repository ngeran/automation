from flask import Flask, request, jsonify
import yaml
from jinja2 import Environment, FileSystemLoader
from jnpr.junos import Device  # Import PyEZ

app = Flask(__name__)

# Jinja2 environment
env = Environment(loader=FileSystemLoader("templates"))


@app.route("/generate-bgp-config", methods=["POST"])
def generate_bgp_config():
    try:
        data = request.get_json()

        with open("data/bgp.yml", "w") as f:
            yaml.dump(data, f)

        with open("data/bgp.yml", "r") as f:  # Read the yaml file
            yaml_data = yaml.safe_load(f)

        bgp_template = env.get_template("bgp.j2")
        bgp_config = bgp_template.render(data=yaml_data)

        # Juniper PyEZ configuration (replace with your details)
        with Device(host="your_router_ip", user="your_username", password="your_password") as dev:
            dev.open()  # Open connection
            dev.load(config_str=bgp_config, format="set")  # Load the config
            dev.commit()  # Commit changes

        return jsonify({"message": "BGP Configuration applied successfully!"}), 200

    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"message": f"An error occurred: {e}"}), 500  # Return error status code


if __name__ == "__main__":
    app.run(debug=True)
