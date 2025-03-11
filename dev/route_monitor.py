from jnpr.junos.op.routes import RouteTable
import time
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RouteMonitor:
    def __init__(self, device, interval=30):
        """
        Initialize the Route Monitor.

        Args:
            device: Connected Junos Device object
            interval (int): Check interval in seconds (default: 30)
        """
        self.device = device  # Store the connected device object
        self.interval = interval  # Monitoring interval
        self.previous_routes = None  # Store previous routing table state

    def get_routes(self):
        """
        Fetch the current routing table from the device.

        Returns:
            list: List of route items if successful, None if error occurs
        """
        try:
            # Create RouteTable object and fetch routes
            routes = RouteTable(self.device)
            routes.get()
            return routes.items()
        except Exception as e:
            logger.error(f"Error fetching routes from {self.device.hostname}: {str(e)}")
            return None

    def compare_routes(self, current_routes):
        """
        Compare current routing table with previous state to detect changes.

        Args:
            current_routes (list): Current routing table items

        Returns:
            list: List of changes detected (additions, modifications, deletions)
        """
        # If no previous state exists, set it and return no changes
        if self.previous_routes is None:
            self.previous_routes = current_routes
            return []

        changes = []
        # Convert lists to dictionaries for easier comparison
        current_dict = dict(current_routes)
        previous_dict = dict(self.previous_routes)

        # Check for new or modified routes
        for route, attrs in current_routes:
            if route not in previous_dict:
                changes.append(f"New route added: {route} -> {attrs}")
            elif previous_dict[route] != attrs:
                changes.append(f"Route modified: {route} -> {attrs}")

        # Check for removed routes
        for route in previous_dict:
            if route not in current_dict:
                changes.append(f"Route removed: {route}")

        # Update previous state
        self.previous_routes = current_routes
        return changes

    def monitor(self):
        """
        Main monitoring loop to periodically check routing table changes.
        Runs until interrupted by user (Ctrl+C).
        """
        try:
            while True:
                # Fetch current routing table
                current_routes = self.get_routes()
                if current_routes is None:
                    logger.error("Skipping this iteration due to fetch error")
                    time.sleep(self.interval)
                    continue

                # Compare and log changes
                changes = self.compare_routes(current_routes)

                if changes:
                    logger.info(f"Routing table changes detected on {self.device.hostname}:")
                    for change in changes:
                        logger.info(change)
                else:
                    logger.info(f"No routing table changes detected on {self.device.hostname}")

                # Wait for specified interval
                time.sleep(self.interval)

        except KeyboardInterrupt:
            logger.info("Monitoring stopped by user")
        except Exception as e:
            logger.error(f"Monitoring error on {self.device.hostname}: {str(e)}")
