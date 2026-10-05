# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Implementation reelle de ProcessRunnerPort — porte VERBATIM depuis
omega-serv (infrastructure/process/subprocess_runner.py) : seul point du
projet qui touche reellement `subprocess` pour l'elevation sudo (charte :
infrastructure/ est la seule couche autorisee a faire de l'I/O
processus)."""
from __future__ import annotations

import subprocess

from omega_log.ports.process_runner_port import ProcessResult


class SubprocessRunner:
    """Implementation reelle de ports.process_runner_port.ProcessRunnerPort."""

    def run(self, args: list[str], input_text: str | None = None, timeout: float | None = None) -> ProcessResult:
        try:
            result = subprocess.run(
                args,
                input=input_text,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False,
            )
        except FileNotFoundError:
            return ProcessResult(returncode=127, stdout="", stderr=f"{args[0]} : commande introuvable")
        except subprocess.TimeoutExpired:
            return ProcessResult(
                returncode=124,
                stdout="",
                stderr=f"{args[0]} : delai depasse ({timeout:.0f}s) - processus bloque, interrompu",
            )
        return ProcessResult(returncode=result.returncode, stdout=result.stdout, stderr=result.stderr)

    def run_interactive(self, args: list[str]) -> int:
        try:
            result = subprocess.run(args, check=False)
        except FileNotFoundError:
            return 127
        return result.returncode
