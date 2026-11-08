# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Cas d'usage « Verifier les mises a jour » (Aide → Contact et support, et `omega-log version --check`)."""
from __future__ import annotations

from omega_log.domain.updates.release_check import UpdateCheck, compare_with_published
from omega_log.ports.release_source_port import ReleaseSourcePort


def check_for_update(source: ReleaseSourcePort, installed: str) -> UpdateCheck:
    return compare_with_published(installed, source.fetch_sha_list())
