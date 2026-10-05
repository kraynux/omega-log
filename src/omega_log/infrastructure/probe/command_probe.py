# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Command probe.

Tests the presence and basic functionality of system commands/binaries
(shutil.which() + optional test command). Porte verbatim depuis
omega-fire (infrastructure/probe/command_probe.py)."""
import shutil
import subprocess


class CommandProbe:
    """Probes the presence and functionality of system commands."""

    def __init__(self, timeout_seconds: float = 5.0):
        self._timeout = timeout_seconds

    def check_presence(self, binary_name: str) -> bool:
        return shutil.which(binary_name) is not None

    def get_binary_path(self, binary_name: str) -> str | None:
        return shutil.which(binary_name)

    def check_functionality(
        self, binary_name: str, test_command: list[str] | None = None
    ) -> tuple[bool, str]:
        binary_path = self.get_binary_path(binary_name)
        if binary_path is None:
            return False, f"Binary '{binary_name}' not found in PATH"

        if test_command is None:
            return True, f"Binary '{binary_name}' found at {binary_path}"

        try:
            result = subprocess.run(
                test_command, capture_output=True, text=True, timeout=self._timeout, check=False,
            )
            if result.returncode == 0:
                return True, f"Binary '{binary_name}' is functional"
            error_msg = result.stderr.strip() or f"Exit code {result.returncode}"
            return False, f"Binary '{binary_name}' test failed: {error_msg}"
        except subprocess.TimeoutExpired:
            return False, f"Binary '{binary_name}' test timed out after {self._timeout}s"
        except FileNotFoundError:
            return False, f"Binary '{binary_name}' disappeared during test"
        except OSError as e:
            return False, f"Binary '{binary_name}' test error: {e}"

    def probe_command(self, binary_name: str, test_command: list[str] | None = None) -> dict:
        """Returns {present, functional, path, message}."""
        present = self.check_presence(binary_name)
        path = self.get_binary_path(binary_name)

        if not present:
            return {
                "present": False, "functional": False, "path": None,
                "message": f"Binary '{binary_name}' not found in PATH",
            }

        functional, message = self.check_functionality(binary_name, test_command)
        return {"present": True, "functional": functional, "path": path, "message": message}
