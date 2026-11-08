# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Ecran Aide : reference statique des raccourcis et fonctions de
l'application. Adapte du patron help_screen.py du reste de la suite
omega- — memes raccourcis, contenu propre a LOG pour les fonctions (mis
a jour au fil des phases, voir plan_omega_log.md).

ENRICHI (2026-10-04, demande explicite utilisateur : "enrichir l'AIDE
pour chaque menu et fonction, utilisation, guide, sois exhaustif") : le
reste de la suite omega- garde volontairement cette aide compacte (une
phrase par ecran), mais LOG a ici reellement plus d'ecrans/regles de
compatibilite a expliquer (viewers, elevation sudo ponctuelle, selection
par numeros...) — une seule section "Fonctions" condensee ne suffisait
plus. Passage a une section PAR ECRAN (une par entree du menu principal,
dans le meme ordre que home.py::_COLUMN_1/_COLUMN_2, plus les 3 viewers
et un glossaire) sous forme de `Collapsible` : contenu exhaustif sans
transformer l'ecran en mur de texte illisible — chaque section se replie,
une seule depliee par defaut (Demarrage rapide, la plus utile en premier
usage)."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from omega_lib.theme.policies import DEFAULT_EXPORT_THEME, EXPORT_PALETTES
from textual.app import ComposeResult
from textual.containers import Center, Container, Horizontal, VerticalScroll
from textual.widgets import Button, Collapsible, Footer, Header, Select, Static

from omega_log.infrastructure.exporters.html_exporter import export_help_html
from omega_log.interfaces.tui.screens._base import OmegaScreen
from omega_log.interfaces.tui.screens.contact_support_screen import ContactSupportScreen
from omega_log.shared.i18n import LANGUAGE, N_, _, translating_as

if TYPE_CHECKING:
    from omega_log.app.dependency_container import DependencyContainer

_SHORTCUTS = (
    (N_("Haut / Bas"), N_("Naviguer entre les éléments d'un écran")),
    (N_("Tab / Maj+Tab"), N_("Naviguer entre les champs d'un formulaire")),
    (N_("Entrée / Clic"), N_("Activer le bouton ou le champ sélectionné")),
    (N_("Échap"), N_("Retour à l'écran précédent (confirmation de sortie sur l'accueil)")),
    ("t", N_("Thème suivant (appliqué immédiatement, sans confirmation)")),
    ("r", N_("Rafraîchir la détection du terminal (adapte le profil d'affichage)")),
    ("a", N_("Cette aide, accessible depuis n'importe quel écran")),
    ("q", N_("Quitter (avec confirmation)")),
)

_LNAV_SHORTCUTS = (
    ("t", N_("Thème suivant — intercepté avant lnav, jamais transmis")),
    (N_("Ctrl+C"), N_("Marque la ligne courante et la copie (presse-papier terminal, OSC 52) — "
                 "jamais transmis à lnav tel quel")),
    (N_("Ctrl+Q"), N_("Quitte lnav et revient à l'application — jamais transmis à lnav")),
    (N_("Haut/Bas, g/G, /, m, q..."), N_("Raccourcis propres à lnav lui-même (navigation, "
                                    "recherche, marquage, vues) — voir sa documentation")),
)

_QUICKSTART = N_("1. [b]Registre des capacités[/b] : lancez un scan au premier démarrage pour\n "
                "  que l'application découvre les logs déjà présents sur la machine.\n2. "
                "Importez les logs qui vous intéressent dans la [b]Bibliothèque[/b]\n   (au "
                "détail ou en totalité depuis le Registre, ou manuellement).\n3. Ouvrez-les "
                "depuis [b]Voir les logs[/b] (ou créez un [b]Favori[/b] pour\n   un lancement "
                "direct la prochaine fois).\n4. Pour un accès root (ex. /var/log/audit/), "
                "l'application ne tourne\n   jamais en root elle-même — elle demande une "
                "authentification sudo\n   ponctuelle, UNE SEULE FOIS par log protégé, au "
                "moment précis où elle\n   en a besoin.\n5. [b]Voir et Traiter IP[/b] et "
                "[b]Statistiques[/b] pour l'analyse ;\n   "
                "[b]Rotate[/b]/[b]Purger[/b]/[b]Exporter[/b] pour la maintenance.\n")

_SECTIONS: tuple[tuple[str, str], ...] = (
    (
        N_("Registre des capacités"),
        N_("Détecte automatiquement les services/serveurs actifs sur la machine\n(serveurs web, "
          "bases de données, mail, DNS, sécurité, omega-serv...) et\npropose l'import de leurs "
          "logs connus — fonctionne même sans aucun log\nprésent, dégrade proprement.\n\n- "
          "[b]Scanner les services[/b] : sonde chaque capacité connue (~45 appels\n  système "
          "en arrière-plan, jamais sur le thread d'affichage — l'écran\n  reste réactif "
          "pendant le scan). Remplit la liste de ce qui a été\n  découvert, et sépare les logs "
          "\"suspects\" (fichier présent mais vide,\n  très probablement routé vers journald "
          "plutôt qu'un fichier classique).\n- [b]Scanner ce dossier[/b] : scan manuel non "
          "récursif d'un chemin de\n  votre choix (ex. /var/log), en complément du scan "
          "automatique.\n- Sélectionnez une ligne puis [b]Voir (simple/classique/lnav)[/b] "
          "pour\n  un aperçu immédiat SANS importer, ou [b]Importer la sélection[/b] /\n  "
          "[b]Importer tout[/b] pour les ajouter à la Bibliothèque.\n- L'état \"SUSPECT\" "
          "n'est jamais bloquant : vous pouvez importer et ouvrir\n  un log suspect "
          "normalement, l'application affichera simplement ce\n  qu'il contient réellement "
          "(potentiellement rien)."),
    ),
    (
        N_("Bibliothèque"),
        N_("Hub central référençant tous les logs à traiter — point de départ de\ntous les "
          "autres écrans (Voir les logs, Favoris, Voir et Traiter IP,\nStatistiques, Rotate, "
          "Purger). Alimentée par le Registre (import au\ndétail ou en totalité) OU par ajout "
          "manuel ici — jamais l'inverse.\n\n- [b]Ajouter[/b] : saisissez un chemin absolu et "
          "validez — aucune\n  vérification d'existence à l'ajout, l'état réel "
          "(OK/SUSPECT/ABSENT)\n  n'est évalué qu'à l'affichage de la liste.\n- Colonne "
          "\"État\" : [b]OK[/b] (fichier présent, non vide), [b]SUSPECT[/b]\n  (présent mais "
          "vide), [b]ABSENT[/b] (chemin introuvable — le fichier a\n  pu être supprimé, "
          "déplacé par une rotation, ou n'a jamais existé). Un log\n  ABSENT reste dans la "
          "liste (rien ne le retire automatiquement) : utile\n  si le fichier réapparaît "
          "(rotation logrotate externe, par exemple).\n- [b]Retirer la sélection[/b] : retire "
          "uniquement la référence dans la\n  Bibliothèque, après confirmation — NE TOUCHE "
          "JAMAIS au fichier réel\n  sur le disque (pour ça, voir l'écran Purger).\n- "
          "[b]Rafraîchir[/b] : relit l'état de chaque entrée sans tout re-scanner.\n- Colonnes "
          ": [b]#[/b] (numéro à cliquer ou à saisir dans les autres\n  écrans), Chemin, "
          "Service, Accès, Taille, [b]Modifié[/b] (dernière\n  écriture ; pour une copie SSH, "
          "date de la dernière récupération), État.\n- [b]Ajouter les logs connus "
          "d'Omega-Serv[/b] : cherche les installations\n  omega-serv de la machine (alias "
          "`serv` de ~/.bashrc et ~/.zshrc,\n  registre des instances "
          "~/.config/omega-serv/instances.json, services\n  systemd) et ajoute leurs logs "
          "access et error, les alertes WAF si le\n  WAF est actif, et les 2 logs magnet si le "
          "magnet l'est aussi. Lecture\n  seule, uniquement au clic ; un log déjà présent est "
          "remplacé, jamais\n  dupliqué. Une instance supplémentaire apparaît en "
          "\"omega-serv:<nom>\".\n- [b]Sources distantes (SSH)[/b] : définissez une source "
          "(label, hôte,\n  chemin distant, utilisateur/port/clé facultatifs) puis "
          "[b]Récupérer\n  maintenant[/b] : une COPIE du log est rapatriée par scp dans\n  "
          "var/remote/ et ajoutée à la Bibliothèque (Accès \"ssh\"). Ce n'est pas\n  une "
          "lecture en direct : chaque récupération remplace la copie\n  précédente. Aucun mot "
          "de passe n'est demandé ni stocké,\n  l'authentification reste celle de votre "
          "configuration SSH."),
    ),
    (
        N_("Voir les logs"),
        N_("Ouvre un ou plusieurs logs DÉJÀ référencés dans la Bibliothèque\n(aucun import "
          "manuel ici — importez depuis le Registre ou la\nBibliothèque au préalable).\n\n- "
          "Sélection au clic : un simple clic choisit la ligne ; double-clic\n  ou Entrée "
          "ajoute ou retire son numéro dans le champ (plusieurs logs,\n  ex. \"1,3\"). Le "
          "champ, s'il est rempli, a priorité.\n- Règle de compatibilité des viewers : [b]1 "
          "seul log[/b] -> les 3\n  viewers sont proposés (Simple, Classique, lnav) ; [b]2 "
          "logs ou plus[/b]\n  -> seul [b]lnav[/b] est compatible (fusion multi-fichiers), les "
          "deux\n  autres sont refusés avec une notification explicite si vous insistez.\n- "
          "Les 3 viewers sont détaillés dans leur propre section ci-dessous."),
    ),
    (
        N_("Favoris"),
        N_("Enregistre une combinaison (log(s) + viewer) sous un nom, pour un\nlancement direct "
          "sans re-sélectionner chaque fois.\n\n- Partie haute : liste des favoris existants — "
          "[b]Lancer[/b] ouvre\n  directement le viewer enregistré sur les logs enregistrés "
          ";\n  [b]Supprimer[/b] retire le favori (après confirmation, ne touche\n  jamais aux "
          "fichiers de log réels).\n- Partie basse (\"Créer un favori\") : mêmes NUMÉROS "
          "séparés par des\n  virgules que \"Voir les logs\", + un nom + le viewer souhaité "
          "(Select),\n  puis [b]Enregistrer[/b].\n- Aucune vérification de compatibilité n'est "
          "faite à la CRÉATION (vous\n  pouvez enregistrer 3 logs + viewer \"lnav\" sans "
          "problème) — la règle\n  1 log/3 viewers vs 2+/lnav uniquement, elle, s'applique "
          "normalement au\n  moment du [b]Lancer[/b].\n- Un favori référence des CHEMINS, pas "
          "des entrées de Bibliothèque : si\n  le fichier est déplacé ou supprimé, le favori "
          "reste mais son\n  lancement échouera comme une ouverture normale sur un chemin "
          "absent."),
    ),
    (
        N_("Voir et Traiter IP"),
        N_("Top 10 des adresses IP les plus actives sur une période, et suppression\nciblée "
          "d'une IP dans un ou plusieurs logs.\n\n- Sélection des logs par numéros (comme "
          "\"Voir les logs\"), puis une\n  période : [b]24h / 7j / 30j / Tout[/b]. Le calcul "
          "se lance au clic sur\n  une période, jamais automatiquement.\n- Le calcul s'exécute "
          "en ARRIÈRE-PLAN dans un processus séparé (jamais\n  sur le thread d'affichage, même "
          "pour un gros fichier) — un indicateur\n  \"Calcul en cours...\" s'affiche pendant "
          "l'attente, les boutons de\n  période sont désactivés jusqu'à la fin pour éviter de "
          "lancer plusieurs\n  calculs en même temps sur le même écran.\n- Périodes courtes "
          "(24h/7j/30j) : lecture optimisée EN PARTANT DE LA FIN\n  du fichier, avec arrêt "
          "anticipé dès que les lignes deviennent trop\n  anciennes — très rapide même sur un "
          "fichier de plusieurs centaines de\n  milliers de lignes. \"Tout\" lit l'intégralité "
          "du fichier, forcément\n  plus lent sur un gros volume.\n- Cliquez une ligne du "
          "tableau de résultat pour la sélectionner, puis\n  [b]Retirer cette IP des logs "
          "analysés[/b] (toujours avec confirmation)\n  pour supprimer DÉFINITIVEMENT toutes "
          "les lignes contenant cette IP,\n  dans TOUS les fichiers analysés pour ce "
          "calcul.\n- Logs protégés (ex. /var/log/audit) : une authentification sudo\n  "
          "ponctuelle est demandée automatiquement au moment où elle est\n  nécessaire "
          "(lecture ou suppression), jamais à l'avance."),
    ),
    (
        N_("Voir et Traiter IP : chercher une IP précise"),
        N_("Sans attendre qu'une IP apparaisse dans le top : saisissez-la (IPv4 ou\nIPv6) dans « Ou cherchez une "
          "IP précise », puis [b]Rechercher cette IP[/b]\nou Entrée.\n\n- Ses lignes sont comptées dans chaque log "
          "sélectionné, fichier entier,\n  avec le total et le détail par log.\n- Ce sont exactement les lignes que "
          "le retrait supprimerait : si l'IP\n  est présente, elle est déjà sélectionnée, [b]Retirer cette IP[/b] "
          "est\n  actif, et elle est recomptée après le retrait.\n- Une IP n'est jamais confondue avec une IP plus "
          "longue (1.1.1.1 et\n  1.1.1.11), et une IPv6 terminée par « :: » est bien trouvée."),
    ),
    (
        N_("Statistiques (accès)"),
        N_("Volume, IPs uniques, taux d'erreur, top IPs, répartition horaire sur un\nou "
          "plusieurs logs d'accès — avec export.\n\n- Mêmes principes que \"Voir et Traiter "
          "IP\" : sélection par numéros,\n  période 24h/7j/30j/Tout, calcul en arrière-plan "
          "dans un processus\n  séparé (boutons de période désactivés pendant le calcul), "
          "lecture\n  optimisée par période courte, élévation sudo ponctuelle automatique\n  "
          "sur un log protégé.\n- Le rapport affiché (présentation du rapport d'omega-fire) : "
          "une\n  [b]synthèse[/b] (lignes analysées, requêtes HTTP, IPs uniques, taux\n  "
          "d'erreur, volume transféré, heure de pointe, période couverte), les\n  [b]statuts "
          "HTTP[/b] en jauges (2xx/3xx/4xx/5xx, refus 403 et 429), les\n  [b]top IP[/b], "
          "[b]chemins demandés[/b] et [b]chemins en 404[/b] (avec la\n  part en erreur), la "
          "[b]répartition horaire[/b] (24 jauges, heure de\n  pointe en couleur d'alerte) et "
          "la [b]tendance par jour[/b] (7 j / 30 j).\n- Une valeur que le log ne fournit pas "
          "s'affiche \"-\" (jamais estimée) ;\n  pour un log non HTTP (auth.log, syslog...), "
          "statuts et chemins sont\n  absents et le taux d'erreur compte les lignes de niveau "
          "erreur.\n- [b]Exporter JSON[/b] / [b]Exporter HTML[/b] (5 thèmes graphiques au\n  "
          "choix) : le même rapport, avec cartes, histogramme horaire et jauges.\n  Nécessite "
          "d'avoir calculé au moins une fois (choisi une période) avant\n  de pouvoir exporter "
          "— le fichier produit est horodaté,\n  déposé dans var/exports/."),
    ),
    (
        N_("Rotate"),
        N_("Sauvegarde compressée d'un log et restauration depuis une archive\nprécédente.\n\n- "
          "[b]Sauvegarder maintenant[/b] : numéro du log (un seul à la fois) +\n  nombre de "
          "rotations à conserver (champ \"Rotations à conserver\", 7 par\n  défaut) — au-delà "
          "de ce nombre, les archives les plus anciennes sont\n  supprimées automatiquement à "
          "chaque nouvelle sauvegarde (rétention\n  automatique, jamais d'accumulation "
          "illimitée).\n- Liste \"Archives disponibles\" : toutes les sauvegardes "
          "existantes,\n  triées des plus récentes aux plus anciennes, avec taille et date.\n- "
          "[b]Restaurer[/b] : sélectionnez une archive dans la liste, choisissez\n  le mode — "
          "[b]Fusion (append)[/b] ajoute le contenu de l'archive à la\n  fin du fichier actuel "
          "; [b]Écrasement (overwrite)[/b] remplace\n  entièrement le contenu actuel par celui "
          "de l'archive. Une sauvegarde\n  de sécurité du fichier cible est prise "
          "automatiquement AVANT toute\n  restauration, pour pouvoir annuler en cas "
          "d'erreur.\n- [b]Supprimer l'archive[/b] : suppression définitive d'une sauvegarde\n "
          " (après confirmation) — ne touche jamais au log source.\n- Log protégé : élévation "
          "sudo ponctuelle automatique si nécessaire,\n  pour la sauvegarde comme pour la "
          "restauration."),
    ),
    (
        N_("Sauvegardes planifiées"),
        N_("Rotate → [b]Sauvegardes planifiées[/b] : un log de la Bibliothèque est\nsauvegardé automatiquement "
          "tous les jours, toutes les semaines ou tous\nles mois, avec le nombre de sauvegardes conservées.\n\n- La "
          "première sauvegarde planifiée installe une tâche quotidienne :\n  timer systemd (mot de passe sudo "
          "demandé), sinon une ligne de votre\n  crontab (OpenRC, runit), sinon la ligne à ajouter vous-même est\n  "
          "affichée. La dernière supprimée retire la tâche.\n- Chaque nuit, [b]omega-log rotate run-automations[/b] "
          "sauvegarde, sous\n  votre compte (jamais root), chaque log arrivé à échéance ; le tableau\n  montre la "
          "dernière et la prochaine exécution.\n- Un log protégé (/var/log/...) ne peut pas être sauvegardé la nuit\n  "
          "sans mot de passe : l'échec est noté, Santé des logs le signale."),
    ),
    (
        N_("Purger"),
        N_("Deux actions DISTINCTES et toutes deux irréversibles sans confirmation\npréalable — "
          "à ne jamais confondre :\n\n- [b]Vider le contenu[/b] : TRONQUE le(s) fichier(s) EN "
          "PLACE (le\n  fichier continue d'exister, vide). Méthode sûre pour un log encore\n  "
          "activement écrit par un service qui le garde ouvert (contrairement à\n  une "
          "suppression, qui casserait le descripteur de fichier du service\n  tant qu'il n'est "
          "pas redémarré).\n- [b]Supprimer le(s) fichier(s)[/b] : efface COMPLÈTEMENT le(s)\n  "
          "fichier(s) du disque — plus aucune trace, le fichier disparaît aussi\n  de la "
          "Bibliothèque.\n- Les deux actions acceptent une sélection MULTIPLE par numéros "
          "séparés\n  par des virgules, et demandent TOUJOURS confirmation avant d'agir\n  (la "
          "liste exacte des fichiers concernés est affichée dans la boîte de\n  "
          "confirmation).\n- Pensez à [b]Rotate -> Sauvegarder maintenant[/b] avant de purger "
          "si\n  vous voulez garder une trace du contenu actuel."),
    ),
    (
        N_("Exporter"),
        N_("Export de la liste des ARCHIVES (sauvegardes Rotate) en JSON ou en HTML\nà thème — "
          "distinct de l'export des statistiques (présent directement\ndans l'écran "
          "Statistiques).\n\n- [b]Rafraîchir[/b] : relit la liste des archives présentes sur "
          "le\n  disque (utile si vous venez de sauvegarder ou de supprimer une archive\n  "
          "depuis l'écran Rotate).\n- [b]Exporter JSON[/b] : structure brute (nom, taille en "
          "octets, date de\n  création) de chaque archive listée.\n- [b]Exporter HTML[/b] : "
          "même contenu, mis en forme avec le thème\n  graphique choisi dans le Select "
          "au-dessus (5 thèmes disponibles,\n  mêmes palettes que l'export des "
          "Statistiques).\n- Le fichier produit est horodaté et déposé dans var/exports/ (le "
          "même\n  dossier que les exports de Statistiques)."),
    ),
    (
        N_("Santé des logs"),
        N_("Contrôle en lecture seule des logs de la Bibliothèque, du disque qui les\nporte, des sauvegardes et des "
          "sauvegardes planifiées. Chaque log reçoit\nun niveau : OK, Info, Attention ou Problème, avec le geste à "
          "faire.\n\n- Contrôles : fichier absent ou lien cassé, illisible par votre compte,\n  inscriptible par "
          "tout le monde, log muet depuis plus de 7 jours, vide,\n  dates non reconnues ou dans le futur, octets nuls, "
          "gros log sans règle\n  logrotate, doublon ; disque (jours avant d'être plein) ; sauvegardes\n  planifiées "
          "en échec ou en retard.\n- [b]Analyser avec sudo[/b] : lit le début et la fin des logs illisibles.\n- "
          "[b]Corriger les droits[/b] / [b]Corriger avec sudo[/b] : retire l'écriture\n  pour tout le monde (chmod "
          "o-w), après confirmation.\n- [b]Exporter JSON / HTML / TXT[/b] : le rapport, dans la langue des\n  exports, "
          "déposé dans var/exports/."),
    ),
    (
        N_("Options"),
        N_("Réglages de l'application elle-même (pas des logs traités).\n\n- [b]Thème[/b] : 10 "
          "thèmes disponibles, appliqué IMMÉDIATEMENT à la\n  sélection, sans confirmation ni "
          "redémarrage (équivalent à appuyer\n  plusieurs fois sur la touche [b]t[/b]).\n- "
          "[b]Profil de rendu[/b] : force un niveau d'adaptation au terminal\n  "
          "(complet/standard/réduit/mono) au lieu de la détection automatique —\n  nécessite "
          "un REDÉMARRAGE de l'application pour prendre effet\n  (\"Automatique\" restaure la "
          "détection normale).\n- [b]Vider le dossier exports[/b] / [b]Vider le dossier "
          "screenshots[/b] :\n  supprime définitivement TOUS les fichiers de ces dossiers "
          "applicatifs\n  (après confirmation) — n'affecte jamais les logs surveillés ni "
          "leurs\n  archives Rotate."),
    ),
    (
        N_("Version et mises à jour"),
        N_("La version d'omega-log est affichée dans la barre de titre.\n\n- Aide → Contact et support → "
          "[b]Vérifier les mises à jour[/b] : compare\n  votre version à la liste des versions publiées sur le site. "
          "Seulement\n  sur votre clic, rien n'est envoyé.\n- Si une version plus récente existe, [b]Voir les nouveautés[/b] "
          "ouvre\n  son résumé dans votre navigateur.\n- En ligne de commande : omega-log version --check."),
    ),
    (
        N_("Aide, export et contact"),
        N_("- [b]Exporter l'aide en HTML[/b] : toute cette aide dans un fichier\n  HTML "
          "horodaté (thème au choix, comme les autres exports), déposé dans\n  "
          "var/exports/.\n- [b]Contact et support[/b] : payer un café (PayPal), se déclarer\n  "
          "utilisateur anonyme, contacter le support (mail et formulaire du site).\n  Les "
          "adresses sont toujours affichées en clair : sans session graphique\n  (SSH), "
          "recopiez-les dans votre navigateur.\n- [b]Se déclarer utilisateur (anonyme)[/b] : "
          "volontaire, une seule fois,\n  au clic. Le message exact est affiché avant l'envoi "
          ": une clé tirée au\n  hasard, le logiciel (omega-log), sa version et, facultatifs, "
          "un\n  continent et un pays. [b]Ne plus me déclarer[/b] supprime l'entrée à la\n  "
          "réception et efface la clé locale."),
    ),
)

_VIEWERS = N_("[b]1. Simple[/b] — suivi en direct avec parsing générique (horodatage,\nniveau, "
             "IP, service détecté). Le tableau garde tout le tampon (500\nlignes, 200 chargées "
             "à l'ouverture) avec ascenseurs vertical et\nhorizontal ; il suit les nouvelles "
             "lignes seulement si vous êtes déjà en\nbas. À gauche, un tableau de bord qui "
             "défile (identique à omega-serv) :\nrendement, bande passante, statuts HTTP (dont "
             "refus 403 et 429), IPs\nuniques et top 5 IP, chemins les plus demandes et "
             "chemins en 404, santé\net tampon. Une valeur que le log ne fournit pas s'affiche "
             "\"-\", jamais\nestimée. Pour un access log HTTP reconnu\n(format "
             "Combined/Common), deux colonnes supplémentaires apparaissent\nautomatiquement : "
             "[b]Code[/b] (statut HTTP, coloré 2xx vert/3xx cyan/\n4xx jaune/5xx rouge) et "
             "[b]Timeout[/b] (latence si le format source la\nfournit, coloré selon le seuil) "
             "— ces colonnes affichent \"-\" pour tout\nce qui n'est pas un format HTTP "
             "reconnu (auth.log, syslog, fail2ban...).\n\n[b]2. Classique[/b] — affiche les "
             "dernières lignes BRUTES du fichier\n(aucun parsing, aucune coloration), avec un "
             "bouton [b]Suivre en\ndirect[/b] pour basculer en mode tail -f. Le plus simple et "
             "le plus\nfiable quel que soit le format du fichier.\n\n[b]3. lnav[/b] — "
             "encapsule le programme externe `lnav` dans un terminal\ndédié (pty), pour une "
             "fusion et une analyse croisée de PLUSIEURS\nfichiers à la fois (merge "
             "automatique par horodatage). Nécessite que\n`lnav` soit installé sur le système "
             "(sudo pacman -S lnav / sudo apt\ninstall lnav) — sans lui, ce viewer est proposé "
             "mais refuse de se\nlancer avec un message explicite. Raccourcis spécifiques "
             "pendant une\nsession lnav :")

_GLOSSARY = N_("[b]Élévation sudo ponctuelle[/b] — l'application ne tourne JAMAIS en\nroot par "
              "défaut. Quand une action rencontre réellement une permission\nrefusée (ex. "
              "/var/log/audit/, lisible seulement par root), une\nauthentification sudo est "
              "demandée À CE moment précis, dans le\nterminal réel (l'interface se suspend "
              "brièvement) — jamais à l'avance,\njamais pour des actions qui n'en ont pas "
              "besoin. Une fois authentifié\npour un écran donné, les actions suivantes sur ce "
              "même écran réutilisent\nl'autorisation sans redemander.\n\n[b]États SUSPECT / "
              "ABSENT / OK[/b] — SUSPECT : fichier présent mais\nvide (très souvent un service "
              "qui route en réalité vers journald plutôt\nque vers un fichier classique). "
              "ABSENT : chemin introuvable au moment de\nl'affichage (supprimé, pas encore "
              "créé, ou chemin erroné). OK : fichier\nprésent et non vide. Ces états sont "
              "INFORMATIFS, jamais bloquants —\nvous pouvez toujours ouvrir, exporter ou "
              "purger un log quel que soit son\nétat affiché.\n\n[b]Sélection des logs[/b] — "
              "convention commune (Voir les logs, Favoris,\nVoir et Traiter IP, Statistiques, "
              "Rotate, Purger) : le tableau affiche\nun numéro par ligne. Simple clic : la "
              "ligne surlignée suffit. Double-clic\nou Entrée : ajoute ou retire son numéro "
              "dans le champ (ex. \"1,3,4\").\nVous pouvez aussi saisir les numéros à la main "
              "; le champ, s'il est\nrempli, a priorité.\n\n[b]Dossier var/[/b] — tout l'état "
              "propre à l'application (bibliothèque,\nfavoris, thème choisi, archives de "
              "sauvegarde, exports, journal\napplicatif) vit dans ./var/, relatif au dossier "
              "où vous lancez\nl'application (ou $OMEGA_LOG_VAR_DIR si défini) — jamais dans "
              "votre\ndossier personnel. Ce dossier est entièrement local à la machine, "
              "ne\ncontient aucun des LOGS SURVEILLÉS eux-mêmes (seulement des "
              "références\nvers leurs chemins).")


def help_export_content() -> tuple[list[dict], list[dict]]:
    """Tout le contenu de l'aide, dans l'ordre de l'ecran, pour l'export HTML."""
    shortcut_tables = [
        {"title": _("Raccourcis clavier"), "rows": _pairs(_SHORTCUTS)},
        {"title": _("Raccourcis pendant une session lnav"), "rows": _pairs(_LNAV_SHORTCUTS)},
    ]
    sections = [
        {"title": _("Démarrage rapide"), "body": _(_QUICKSTART)},
        *({"title": _(title), "body": _(body)} for title, body in _SECTIONS),
        {"title": _("Les 3 viewers (Simple / Classique / lnav)"), "body": _(_VIEWERS)},
        {"title": _("Concepts et glossaire"), "body": _(_GLOSSARY)},
    ]
    return shortcut_tables, sections


def _pairs(rows: tuple[tuple[str, str], ...]) -> list[tuple[str, str]]:
    return [(_(key), _(description)) for key, description in rows]


class HelpScreen(OmegaScreen):
    """Reference statique, accessible depuis n'importe quel ecran (touche `a`). Reprise d'omega-serv
    (2026-11-06) : export HTML de toute l'aide (theme au choix) et bouton « Contact et support »."""

    def __init__(self, *, container: DependencyContainer) -> None:
        super().__init__()
        self._container = container

    def compose(self) -> ComposeResult:
        yield Header()
        with VerticalScroll(classes="omega-panel"):
            with Center():
                yield Static(_("AIDE"), classes="omega-title")
            with Horizontal(classes="omega-actions"):
                with Container(classes="omega-btn-frame"):
                    yield Button(_("Exporter l'aide en HTML"), id="export-html", variant="primary")
                with Container(classes="omega-btn-frame"):
                    yield Button(_("Contact et support"), id="contact-support")
            yield Select(
                [(name, name) for name in EXPORT_PALETTES], value=DEFAULT_EXPORT_THEME, allow_blank=False,
                id="export-theme-select",
            )
            yield Static(_("Raccourcis clavier"), classes="omega-subtitle")
            for key, description in _SHORTCUTS:
                yield Static(_("{key:<16} {description}").format(key=_(key), description=_(description)))
            yield Static("")

            with Collapsible(title=_("Démarrage rapide"), collapsed=False):
                yield Static(_(_QUICKSTART))

            yield Static(_("Fonctions, écran par écran"), classes="omega-subtitle")
            for title, description in _SECTIONS:
                with Collapsible(title=_(title), collapsed=True):
                    yield Static(_(description))

            with Collapsible(title=_("Les 3 viewers (Simple / Classique / lnav)"), collapsed=True):
                yield Static(_(_VIEWERS))
                for key, description in _LNAV_SHORTCUTS:
                    yield Static(_("  {key:<24} {description}").format(key=_(key), description=_(description)))

            with Collapsible(title=_("Concepts et glossaire"), collapsed=True):
                yield Static(_(_GLOSSARY))

        with Center(), Horizontal(classes="omega-actions omega-fixed-actions"), Container(classes="omega-btn-frame"):
            yield Button(_("Retour"), id="back")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "back":
            self.dismiss()
        elif event.button.id == "contact-support":
            self.app.push_screen(ContactSupportScreen(container=self._container))
        elif event.button.id == "export-html":
            self._export_html()

    def _export_html(self) -> None:
        theme_name = str(self.query_one("#export-theme-select", Select).value)
        with translating_as(LANGUAGE.export_state(self._container.settings_store)):
            shortcut_tables, sections = help_export_content()
            content = export_help_html(shortcut_tables, sections, self._container.app_version, theme_name)
        export_dir = self._container.default_exports_dir
        export_dir.mkdir(parents=True, exist_ok=True)
        path = export_dir / f"aide-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}.html"
        path.write_text(content, encoding="utf-8")
        self.app.notify(_("Export écrit : {path}").format(path=path))
