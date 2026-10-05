# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Executor de PROCESSUS partage pour les calculs CPU-intensifs du
domaine logs (parsing de fichiers volumineux pour Statistiques/Voir et
Traiter IP) — PAS un simple thread.

Bug reel mesure (2026-10-04, retour utilisateur : "l'ecran n'est pas
gele mais... se degele et regele", persistant malgre un premier
correctif `run_worker(thread=True)`) : un calcul CPU-bound en PUR PYTHON
se dispute le GIL avec la boucle d'evenements asyncio/Textual MEME dans
un thread separe — un thread ne contourne le GIL que pour les appels qui
le relachent explicitement (I/O, extensions C). Mesure directe sur un
access.log synthetique de 300 000 lignes : jusqu'a 1.2 SECONDE de
latence d'un simple `pilot.pause()` pendant les ~49s du calcul — c'est
exactement le symptome "gele/degele/regele" rapporte, pas une
supposition. Seul un VRAI processus separe echappe entierement au GIL du
processus principal (Textual) : c'est ce que fournit ce module, consomme
via `loop.run_in_executor(STATS_PROCESS_POOL, func)` dans un worker
Textual ASYNCHRONE (jamais `thread=True`) — voir screens/
access_log_stats_screen.py et screens/process_ip_screen.py.

AMORCAGE EAGER AJOUTE (2026-10-04, meme retour utilisateur persistant
malgre le passage en ProcessPoolExecutor — "toujours rien ne s'affiche")
: `multiprocessing` demarre par defaut en "forkserver" sur cette machine
(Python 3.14) — un processus auxiliaire DEDIE, cree UNE SEULE FOIS en
forkant le processus principal au moment du PREMIER `submit()`, qui sert
ensuite tous les calculs en forkant depuis LUI-MEME (jamais a nouveau
depuis le processus principal). Probleme reel : sans amorcage explicite,
ce premier fork n'a lieu qu'au premier clic utilisateur — a ce moment,
le VRAI driver Textual (LinuxDriver, lecture clavier brute sur un vrai
terminal) a deja demarre son propre thread de lecture ; forker un
processus multi-thread a cet instant precis est un terrain CLASSIQUE de
deadlock Python documente (le processus forke n'herite QUE du thread
appelant, tout mutex/etat detenu par un AUTRE thread au moment du fork
reste fige pour toujours dans l'enfant). Invisible sous le pilote de
test headless de Textual (aucun thread clavier reel la-bas, d'ou des
tests automatises passant alors que l'usage reel restait bloque).
Corrige en forcant ce premier fork ICI, a l'IMPORT de ce module — donc
tres tot, pendant la construction de l'arbre d'ecrans (home.py), TOUJOURS
avant `App.run()`/le demarrage du driver reel : plus aucun fork n'a
ensuite besoin de se reproduire depuis le processus principal durant
toute la session.

`max_workers=2` : largement suffisant pour ce TUI mono-utilisateur
(au plus Statistiques + Voir et Traiter IP en meme temps), jamais besoin
de paralleliser davantage. Arret propre via `atexit` — les processus du
pool ne doivent jamais survivre au process principal."""
from __future__ import annotations

import atexit
from concurrent.futures import ProcessPoolExecutor

STATS_PROCESS_POOL = ProcessPoolExecutor(max_workers=2)
STATS_PROCESS_POOL.submit(int).result()
"""Amorce le forkserver/pool MAINTENANT (voir note ci-dessus) — jamais
supprimer cet appel pour "simplifier", c'est le correctif lui-meme, pas
un effet de bord."""
atexit.register(STATS_PROCESS_POOL.shutdown, cancel_futures=True)
