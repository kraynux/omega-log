# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Elevation ponctuelle (sudo) pour l'acces aux logs proteges de
/var/log — plan_omega_log.md §5.1 (revise 2026-10-03, retour utilisateur :
"omega log a besoin du service root pour aller chercher les logs qui
sont dans les dossiers var"). Meme mecanisme que omega-serv (sudo au
moment precis d'une action, jamais l'application entiere en root), mais
applique ici a des operations fichier (lecture/ecriture/troncature/
suppression) plutot qu'a des commandes systemctl."""
