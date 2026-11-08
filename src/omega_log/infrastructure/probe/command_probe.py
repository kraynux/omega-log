# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Command probe.

Tests the presence and basic functionality of system commands/binaries
(shutil.which() + optional test command). Porte verbatim depuis
omega-fire (infrastructure/probe/command_probe.py)."""
import shutil
import subprocess

from omega_log.shared.i18n import _


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
            return False, _("Programme « {binary_name} » introuvable dans le PATH").format(binary_name=binary_name)

        if test_command is None:
            return True, f"Binary '{binary_name}' found at {binary_path}"

        try:
            result = subprocess.run(
                test_command, capture_output=True, text=True, timeout=self._timeout, check=False,
            )
            if result.returncode == 0:
                return True, f"Binary '{binary_name}' is functional"
            error_msg = result.stderr.strip() or _("Code de sortie {returncode}").format(returncode=result.returncode)
            return False, _("Test du programme « {binary_name} » échoué : {error_msg}").format(binary_name=binary_name, error_msg=error_msg)
        except subprocess.TimeoutExpired:
            return False, _("Test du programme « {binary_name} » : délai dépassé ({timeout} s)").format(binary_name=binary_name, timeout=self._timeout)
        except FileNotFoundError:
            return False, _("Programme « {binary_name} » disparu pendant le test").format(binary_name=binary_name)
        except OSError as e:
            return False, _("Erreur pendant le test du programme « {binary_name} » : {e}").format(binary_name=binary_name, e=e)

    def probe_command(self, binary_name: str, test_command: list[str] | None = None) -> dict:
        """Returns {present, functional, path, message}."""
        present = self.check_presence(binary_name)
        path = self.get_binary_path(binary_name)

        if not present:
            return {
                "present": False, "functional": False, "path": None,
                "message": _("Programme « {binary_name} » introuvable dans le PATH").format(binary_name=binary_name),
            }

        functional, message = self.check_functionality(binary_name, test_command)
        return {"present": True, "functional": functional, "path": path, "message": message}
