# scripts/backup_host.py
# Purpose: Backs up Juniper device configurations to a dedicated directory.

import os
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def backup_config(dev, backup_dir="./backups"):
    """Backup the current configuration of a Juniper device."""
    try:
        config = dev.rpc.get_config(options={'format': 'set'})
        config_text = config.text

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        hostname = dev.hostname or dev.host
        backup_file = f"{backup_dir}/backup_{hostname}_{timestamp}.txt"

        os.makedirs(backup_dir, exist_ok=True)
        with open(backup_file, "w") as f:
            f.write(config_text)

        logger.info(f"Backed up config to {backup_file}")
        return backup_file
    except Exception as e:
        logger.error(f"Backup failed for {dev.hostname or dev.host}: {e}")
        raise
