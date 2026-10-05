# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Core enums transverses. Trimme depuis omega-fire (core/enums.py) :
seul CapabilityStatus est reellement utilise par LOG (registre de
capacites) — BackendType/ServiceManagerType/RuleAction/ExportFormat sont
specifiques au pare-feu de FIRE et sans equivalent ici ; LogLevel existe
deja (domain/logs/models.py), pas de doublon."""
from enum import Enum


class CapabilityStatus(Enum):
    """Statut d'une capacite systeme (registre, voir core/capability.py).

    Utilise par le registre de capacites pour suivre ce qui est
    disponible, degrade, manquant, ou disqualifie sur la machine cible."""
    AVAILABLE = "available"
    DEGRADED = "degraded"
    MISSING = "missing"
    DISQUALIFIED = "disqualified"
