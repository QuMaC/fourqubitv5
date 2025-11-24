"""
SGMA Signal Generator SCPI Driver
Simple driver for connecting to and controlling SGMA signal generators

Usage:
    # Initialize by nickname (no scanning needed)
    q1q2 = SGMAGenerator('Q1Q2')
    bfqubit = SGMAGenerator('BFqubit')

    # Control frequency and power
    q1q2.set_frequency(4.7e9)  # 4.7 GHz
    q1q2.set_power(-10)  # -10 dBm

    # Query values
    freq = q1q2.get_frequency()
    power = q1q2.get_power()

    # Disconnect when done
    q1q2.disconnect()
"""

import pyvisa
import time
import logging
from typing import Optional, List, Dict, Any

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SGMAGenerator:
    """Individual SGMA generator with control utilities"""

    # Nickname to IP mapping - stored in the class
    GENERATOR_MAP = {
        'Q1Q2': '192.168.0.104',
        'Q5Q6': '192.168.0.119',
        'RR1RR2': '192.168.0.105',
        'Q3Q4': '192.168.0.111',
        'RR5RR6': '192.168.0.106',
        'RR3RR4': '192.168.0.200',
        'BFqubit': '192.168.0.113',
        'Stark': '192.168.0.127',
    }

    # Resource patterns to try
    RESOURCE_PATTERNS = [
        'TCPIP0::{ip}::INSTR',
        'TCPIP0::{ip}::5025::SOCKET',
        'TCPIP0::{ip}::hislip0::INSTR',
    ]

    def __init__(self, nickname: str):
        """
        Initialize SGMA generator by nickname

        Args:
            nickname: Generator nickname (e.g., 'Q1Q2', 'BFqubit', etc.)
        """
        if nickname not in self.GENERATOR_MAP:
            raise ValueError(f"Unknown nickname '{nickname}'. Available: {list(self.GENERATOR_MAP.keys())}")

        self.nickname = nickname
        self.ip = self.GENERATOR_MAP[nickname]
        self.device = None
        self.resource = None
        self.idn = None
        self.rm = None

        # Auto-connect on initialization
        self._connect()

    def _connect(self):
        """Internal method to connect to the device"""
        try:
            self.rm = pyvisa.ResourceManager()

            # Try different resource patterns
            for pattern_template in self.RESOURCE_PATTERNS:
                pattern = pattern_template.format(ip=self.ip)
                try:
                    self.device = self.rm.open_resource(pattern, open_timeout=2000)
                    self.device.timeout = 5000

                    # Test connection
                    self.idn = self.device.query('*IDN?').strip()
                    self.resource = pattern
                    logger.info(f"[{self.nickname}] Connected at {self.ip}")
                    return

                except Exception as e:
                    if self.device:
                        try:
                            self.device.close()
                        except:
                            pass
                    continue

            raise ConnectionError(f"Could not connect to {self.nickname} at {self.ip}")

        except Exception as e:
            logger.error(f"[{self.nickname}] Failed to connect: {e}")
            raise

    def set_frequency(self, frequency: float) -> bool:
        """Set frequency in Hz"""
        try:
            self.device.write(f'FREQ {frequency}')
            logger.info(f"[{self.nickname}] Set frequency to {frequency/1e9:.6f} GHz")
            return True
        except Exception as e:
            logger.error(f"[{self.nickname}] Error setting frequency: {e}")
            return False

    def get_frequency(self) -> Optional[float]:
        """Get current frequency in Hz"""
        if not self.device:
            logger.error(f"[{self.nickname}] Not connected")
            return None

        try:
            result = self.device.query('FREQ?')
            freq = float(result.strip())
            logger.info(f"[{self.nickname}] Current frequency: {freq/1e9:.6f} GHz")
            return freq
        except Exception as e:
            logger.error(f"[{self.nickname}] Error getting frequency: {e}")
            return None

    def set_power(self, power_dbm: float) -> bool:
        """Set output power in dBm"""
        if not self.device:
            logger.error(f"[{self.nickname}] Not connected")
            return False

        try:
            self.device.write(f'POW {power_dbm}')
            logger.info(f"[{self.nickname}] Set power to {power_dbm} dBm")
            return True
        except Exception as e:
            logger.error(f"[{self.nickname}] Error setting power: {e}")
            return False

    def get_power(self) -> Optional[float]:
        """Get current output power in dBm"""
        if not self.device:
            logger.error(f"[{self.nickname}] Not connected")
            return None

        try:
            result = self.device.query('POW?')
            power = float(result.strip())
            logger.info(f"[{self.nickname}] Current power: {power} dBm")
            return power
        except Exception as e:
            logger.error(f"[{self.nickname}] Error getting power: {e}")
            return None

    def disconnect(self):
        """Disconnect from device"""
        if self.device:
            try:
                self.device.close()
                logger.info(f"[{self.nickname}] Disconnected")
            except Exception as e:
                logger.error(f"[{self.nickname}] Error disconnecting: {e}")
            finally:
                self.device = None

    def __repr__(self):
        """String representation"""
        status = "connected" if self.device else "disconnected"
        return f"SGMAGenerator('{self.nickname}', {self.ip}, {status})"

    @classmethod
    def list_available(cls) -> List[str]:
        """List all available generator nicknames"""
        return list(cls.GENERATOR_MAP.keys())

class SGMASCPIDriver:
    """
    SGMA Signal Generator Driver
    Manages multiple SGMA generators by nickname
    """

    def __init__(self):
        self.generators = {}  # Dictionary: nickname -> SGMAGenerator

    def __getitem__(self, nickname: str) -> SGMAGenerator:
        """
        Access generator by nickname (e.g., driver['Q1Q2'])
        Auto-creates and connects if not already present
        """
        if nickname not in self.generators:
            # Auto-create and connect
            self.generators[nickname] = SGMAGenerator(nickname)
        return self.generators[nickname]

    def add_generator(self, nickname: str) -> SGMAGenerator:
        """
        Explicitly add a generator by nickname
        Returns the SGMAGenerator instance
        """
        if nickname not in self.generators:
            self.generators[nickname] = SGMAGenerator(nickname)
        return self.generators[nickname]

    def list_generators(self) -> List[str]:
        """Get list of currently connected generator nicknames"""
        return list(self.generators.keys())

    def disconnect_all(self):
        """Disconnect from all generators"""
        for nickname, generator in self.generators.items():
            generator.disconnect()
        self.generators.clear()
        logger.info("All generators disconnected")

    @staticmethod
    def list_available() -> List[str]:
        """List all available generator nicknames"""
        return SGMAGenerator.list_available()

def main():
    """Main test function"""
    logger.info("Available generators: " + str(SGMAGenerator.list_available()))

    # Method 1: Direct initialization (recommended for single generators)
    logger.info("\n=== Method 1: Direct Initialization ===")
    try:
        q1q2 = SGMAGenerator('Q1Q2')

        # Query current values
        freq = q1q2.get_frequency()
        power = q1q2.get_power()

        # Disconnect
        q1q2.disconnect()
    except Exception as e:
        logger.error(f"Method 1 failed: {e}")

    # Method 2: Using driver (recommended for multiple generators)
    logger.info("\n=== Method 2: Using Driver ===")
    try:
        driver = SGMASCPIDriver()

        # Auto-connects on first access
        driver['Q1Q2'].get_frequency()
        driver['BFqubit'].get_frequency()

        logger.info(f"Connected generators: {driver.list_generators()}")

        # Disconnect all
        driver.disconnect_all()
    except Exception as e:
        logger.error(f"Method 2 failed: {e}")

    logger.info("\nDone!")

if __name__ == "__main__":
    main()
