from jinja2 import Environment, FileSystemLoader

# Define variables for rendering
local_as = 65001
group_name = "peer-group"
local_address = "192.168.1.1"
peers = [
    {"ip": "192.168.2.1", "as_number": 65002},
    {"ip": "192.168.3.1", "as_number": 65003},
]

# Set up Jinja2 enviorment and load the Template
env = Environment(loader=FileSystemLoader("templates"))
template = env.get_template("config.j2")

# Render the Configuration
config = template.render(
    local_as=local_as, group_name=group_name, local_address=local_address, peers=peers
)

# Save the rendered configuration to a file
with open("bgp_config.txt", "w") as f:
    f.write(config)
