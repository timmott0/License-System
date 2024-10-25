import platform
import uuid
import subprocess
import re
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class HostIdentifier:
    @staticmethod
    def get_mac_address() -> Optional[str]:
        """Get the MAC address of the primary network interface"""
        try:
            mac = uuid.getnode()
            return ':'.join(('%012X' % mac)[i:i+2] for i in range(0, 12, 2))
        except Exception as e:
            logger.error(f"Failed to get MAC address: {str(e)}")
            return None

    @staticmethod
    def get_disk_serial() -> Optional[str]:
        """Get disk serial number"""
        try:
            if platform.system() == "Windows":
                output = subprocess.check_output("wmic diskdrive get SerialNumber").decode()
                serial = output.strip().split("\n")[1]
                return serial.strip()
            elif platform.system() == "Linux":
                output = subprocess.check_output(["udevadm", "info", "--query=property", "--name=/dev/sda"]).decode()
                for line in output.split("\n"):
                    if "ID_SERIAL=" in line:
                        return line.split("=")[1].strip()
            elif platform.system() == "Darwin":  # macOS
                output = subprocess.check_output(["system_profiler", "SPHardwareDataType"]).decode()
                for line in output.split("\n"):
                    if "Serial Number" in line:
                        return line.split(":")[1].strip()
            return None
        except Exception as e:
            logger.error(f"Failed to get disk serial: {str(e)}")
            return None

    @staticmethod
    def get_cpu_info() -> Optional[str]:
        """Get CPU identifier"""
        try:
            if platform.system() == "Windows":
                output = subprocess.check_output("wmic cpu get ProcessorId").decode()
                cpu_id = output.strip().split("\n")[1]
                return cpu_id.strip()
            elif platform.system() == "Linux":
                with open("/proc/cpuinfo", "r") as f:
                    for line in f:
                        if "Serial" in line:
                            return line.split(":")[1].strip()
            elif platform.system() == "Darwin":
                output = subprocess.check_output(["sysctl", "-n", "machdep.cpu.brand_string"]).decode()
                return output.strip()
            return None
        except Exception as e:
            logger.error(f"Failed to get CPU info: {str(e)}")
            return None

    @classmethod
    def get_host_identifiers(cls) -> Dict[str, str]:
        """Get all available host identifiers"""
        identifiers = {
            "hostname": platform.node(),
            "os": platform.system(),
            "os_version": platform.version(),
            "machine_id": str(uuid.getnode()),
        }

        mac_address = cls.get_mac_address()
        if mac_address:
            identifiers["mac_address"] = mac_address

        disk_serial = cls.get_disk_serial()
        if disk_serial:
            identifiers["disk_serial"] = disk_serial

        cpu_info = cls.get_cpu_info()
        if cpu_info:
            identifiers["cpu_id"] = cpu_info

        return identifiers
