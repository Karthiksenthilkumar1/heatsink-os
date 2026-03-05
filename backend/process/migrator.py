import psutil
import logging

logger = logging.getLogger(__name__)

class Migrator:
    """
    Handles process affinity changes to migrate workloads between CPU cores.
    """
    def __init__(self):
        # List of critical process names that should not be touched
        self.ignored_processes = [
            "System", "Idle", "Registry", "smss.exe", "csrss.exe", 
            "wininit.exe", "services.exe", "lsass.exe", "svchost.exe"
        ]

    def is_safe_to_migrate(self, pid):
        """
        Checks if a process is safe to migrate.
        """
        if pid <= 4:
            return False
        try:
            proc = psutil.Process(pid)
            if proc.name() in self.ignored_processes:
                return False
            # Check if process is running as System or other high-privilege account
            # (Simplified check for now)
            return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return False

    def migrate(self, pid, to_core):
        """
        Sets process affinity to the specified core.
        """
        if not self.is_safe_to_migrate(pid):
            logger.warning(f"Skipping migration for PID {pid}: Not safe or inaccessible.")
            return False

        try:
            proc = psutil.Process(pid)
            current_affinity = proc.cpu_affinity()
            
            # If it's already only on that core, no need to migrate
            if current_affinity == [to_core]:
                return False

            # affinity expects a list of core IDs
            proc.cpu_affinity([to_core])
            logger.info(f"Successfully migrated PID {pid} ({proc.name()}) to Core {to_core}")
            return True
        except Exception as e:
            logger.error(f"Failed to migrate PID {pid} to Core {to_core}: {e}")
            return False

if __name__ == "__main__":
    migrator = Migrator()
    # Try to migrate current process as a test (if safe)
    import os
    migrator.migrate(os.getpid(), 0)
