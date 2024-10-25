import platform
import uuid
import subprocess
import re
import logging
import hashlib
import socket
import os
from typing import Dict, Optional, List
from pathlib import Path

logger = logging.getLogger(__name__)

class ExtendedHostIdentifier:
    @staticmethod
    def get_windows_identifiers() -> Dict[str, str]:
        """Get Windows-specific identifiers"""
        identifiers = {}
        try:
            # Get Windows Product ID
            output = subprocess.check_output("wmic os get SerialNumber").decode()
            product_id = output.strip().split("\n")[1].strip()
            identifiers["windows_product_id"] = product_id

            # Get BIOS Serial
            output = subprocess.check_output("wmic bios get SerialNumber").decode()
            bios_serial = output.strip().split("\n")[1].strip()
            identifiers["bios_serial"] = bios_serial

            # Get Motherboard Serial
            output = subprocess.check_output("wmic baseboard get SerialNumber").decode()
            mb_serial = output.strip().split("\n")[1].strip()
            identifiers["motherboard_serial"] = mb_serial

        except Exception as e:
            logger.error(f"Error getting Windows identifiers: {e}")

        return identifiers

    @staticmethod
    def get_linux_identifiers() -> Dict[str, str]:
        """Get Linux-specific identifiers"""
        identifiers = {}
        try:
            # Get Machine ID
            if os.path.exists("/etc/machine-id"):
                with open("/etc/machine-id", "r") as f:
                    identifiers["machine_id"] = f.read().strip()

            # Get DMIDECODE information
            if os.access("/usr/sbin/dmidecode", os.X_OK):
                # System UUID
                output = subprocess.check_output(["sudo", "dmidecode", "-s", "system-uuid"]).decode()
                identifiers["system_uuid"] = output.strip()

                # BIOS Serial
                output = subprocess.check_output(["sudo", "dmidecode", "-s", "bios-serial-number"]).decode()
                identifiers["bios_serial"] = output.strip()

            # Get network interfaces
            if os.path.exists("/sys/class/net"):
                interfaces = []
                for interface in os.listdir("/sys/class/net"):
                    if interface != "lo":  # Skip loopback
                        with open(f"/sys/class/net/{interface}/address", "r") as f:
                            interfaces.append(f.read().strip())
                identifiers["network_interfaces"] = ",".join(interfaces)

        except Exception as e:
            logger.error(f"Error getting Linux identifiers: {e}")

        return identifiers

    @staticmethod
    def get_macos_identifiers() -> Dict[str, str]:
        """Get macOS-specific identifiers"""
        identifiers = {}
        try:
            # Get Hardware UUID
            output = subprocess.check_output(["system_profiler", "SPHardwareDataType"]).decode()
            for line in output.split("\n"):
                if "Hardware UUID" in line:
                    identifiers["hardware_uuid"] = line.split(":")[1].strip()
                elif "Serial Number" in line:
                    identifiers["system_serial"] = line.split(":")[1].strip()

            # Get Board ID
            output = subprocess.check_output(["ioreg", "-l"]).decode()
            board_id_match = re.search(r'board-id".*<"(.+)">', output)
            if board_id_match:
                identifiers["board_id"] = board_id_match.group(1)

        except Exception as e:
            logger.error(f"Error getting macOS identifiers: {e}")

        return identifiers

    @classmethod
    def generate_machine_fingerprint(cls) -> str:
        """Generate a unique machine fingerprint"""
        identifiers = cls.get_host_identifiers()
        fingerprint_str = "|".join(f"{k}:{v}" for k, v in sorted(identifiers.items()))
        return hashlib.sha256(fingerprint_str.encode()).hexdigest()

    @classmethod
    def get_host_identifiers(cls) -> Dict[str, str]:
        """Get all available host identifiers"""
        identifiers = {
            "hostname": platform.node(),
            "os": platform.system(),
            "os_version": platform.version(),
            "machine_id": str(uuid.getnode()),
            "platform": platform.platform(),
            "processor": platform.processor(),
            "architecture": platform.machine()
        }

        # Get platform-specific identifiers
        if platform.system() == "Windows":
            identifiers.update(cls.get_windows_identifiers())
        elif platform.system() == "Linux":
            identifiers.update(cls.get_linux_identifiers())
        elif platform.system() == "Darwin":  # macOS
            identifiers.update(cls.get_macos_identifiers())

        # Add network interfaces
        identifiers.update(cls.get_network_info())

        return identifiers

    @staticmethod
    def get_network_info() -> Dict[str, str]:
        """Get network interface information"""
        network_info = {}
        try:
            # Get all IP addresses
            hostname = socket.gethostname()
            ip_addresses = socket.gethostbyname_ex(hostname)[2]
            network_info["ip_addresses"] = ",".join(ip_addresses)

            # Get default interface
            if platform.system() != "Windows":
                output = subprocess.check_output(["ip", "route", "get", "1.1.1.1"]).decode()
                default_interface = re.search(r'dev (\w+)', output).group(1)
                network_info["default_interface"] = default_interface

        except Exception as e:
            logger.error(f"Error getting network info: {e}")

        return network_info
