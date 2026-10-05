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

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, VerticalScroll
from textual.widgets import Button, Collapsible, Footer, Header, Static

from omega_log.interfaces.tui.screens._base import OmegaScreen

_SHORTCUTS = (
    ("Haut / Bas", "Naviguer entre les elements d'un ecran"),
    ("Tab / Maj+Tab", "Naviguer entre les champs d'un formulaire"),
    ("Entree / Clic", "Activer le bouton ou le champ selectionne"),
    ("Echap", "Retour a l'ecran precedent (confirmation de sortie sur l'accueil)"),
    ("t", "Theme suivant (applique immediatement, sans confirmation)"),
    ("r", "Rafraichir la detection du terminal (adapte le profil d'affichage)"),
    ("a", "Cette aide, accessible depuis n'importe quel ecran"),
    ("q", "Quitter (avec confirmation)"),
)

_LNAV_SHORTCUTS = (
    ("t", "Theme suivant — intercepte avant lnav, jamais transmis"),
    ("Ctrl+C", "Marque la ligne courante et la copie (presse-papier terminal, OSC 52) — jamais transmis a lnav tel quel"),
    ("Ctrl+Q", "Quitte lnav et revient a l'application — jamais transmis a lnav"),
    ("Haut/Bas, g/G, /, m, q...", "Raccourcis propres a lnav lui-meme (navigation, recherche, marquage, vues) — voir sa documentation"),
)

_QUICKSTART = """\
1. [b]Registre des capacites[/b] : lancez un scan au premier demarrage pour
   que l'application decouvre les logs deja presents sur la machine.
2. Importez les logs qui vous interessent dans la [b]Bibliotheque[/b]
   (au detail ou en totalite depuis le Registre, ou manuellement).
3. Ouvrez-les depuis [b]Voir les logs[/b] (ou creez un [b]Favori[/b] pour
   un lancement direct la prochaine fois).
4. Pour un acces root (ex. /var/log/audit/), l'application ne tourne
   jamais en root elle-meme — elle demande une authentification sudo
   ponctuelle, UNE SEULE FOIS par log protege, au moment precis ou elle
   en a besoin.
5. [b]Voir et Traiter IP[/b] et [b]Statistiques[/b] pour l'analyse ;
   [b]Rotate[/b]/[b]Purger[/b]/[b]Exporter[/b] pour la maintenance.
"""

_SECTIONS: tuple[tuple[str, str], ...] = (
    (
        "Registre des capacites",
        """\
Detecte automatiquement les services/serveurs actifs sur la machine
(serveurs web, bases de donnees, mail, DNS, securite, omega-serv...) et
propose l'import de leurs logs connus — fonctionne meme sans aucun log
present, degrade proprement.

- [b]Scanner les services[/b] : sonde chaque capacite connue (~45 appels
  systeme en arriere-plan, jamais sur le thread d'affichage — l'ecran
  reste reactif pendant le scan). Remplit la liste de ce qui a ete
  decouvert, et separe les logs "suspects" (fichier present mais vide,
  tres probablement route vers journald plutot qu'un fichier classique).
- [b]Scanner ce dossier[/b] : scan manuel non recursif d'un chemin de
  votre choix (ex. /var/log), en complement du scan automatique.
- Selectionnez une ligne puis [b]Voir (simple/classique/lnav)[/b] pour
  un apercu immediat SANS importer, ou [b]Importer la selection[/b] /
  [b]Importer tout[/b] pour les ajouter a la Bibliotheque.
- L'etat "SUSPECT" n'est jamais bloquant : vous pouvez importer et ouvrir
  un log suspect normalement, l'application affichera simplement ce
  qu'il contient reellement (potentiellement rien).""",
    ),
    (
        "Bibliotheque",
        """\
Hub central referencant tous les logs a traiter — point de depart de
tous les autres ecrans (Voir les logs, Favoris, Voir et Traiter IP,
Statistiques, Rotate, Purger). Alimentee par le Registre (import au
detail ou en totalite) OU par ajout manuel ici — jamais l'inverse.

- [b]Ajouter[/b] : saisissez un chemin absolu et validez — aucune
  verification d'existence a l'ajout, l'etat reel (OK/SUSPECT/ABSENT)
  n'est evalue qu'a l'affichage de la liste.
- Colonne "Etat" : [b]OK[/b] (fichier present, non vide), [b]SUSPECT[/b]
  (present mais vide), [b]ABSENT[/b] (chemin introuvable — le fichier a
  pu etre supprime, rotate, ou n'a jamais existe). Un log ABSENT reste
  dans la liste (rien ne le retire automatiquement) : utile si le
  fichier reapparait (rotation logrotate externe, par exemple).
- [b]Retirer la selection[/b] : retire uniquement la reference dans la
  Bibliotheque, apres confirmation — NE TOUCHE JAMAIS au fichier reel
  sur le disque (pour ca, voir l'ecran Purger).
- [b]Rafraichir[/b] : relit l'etat de chaque entree sans tout re-scanner.""",
    ),
    (
        "Voir les logs",
        """\
Ouvre un ou plusieurs logs DEJA references dans la Bibliotheque
(aucun import manuel ici — importez depuis le Registre ou la
Bibliotheque au prealable).

- Selection par NUMEROS de ligne separes par des virgules dans le champ
  de saisie (ex. "1,3") — pas de clic multiple sur le tableau.
- Regle de compatibilite des viewers : [b]1 seul log[/b] -> les 3
  viewers sont proposes (Simple, Classique, lnav) ; [b]2 logs ou plus[/b]
  -> seul [b]lnav[/b] est compatible (fusion multi-fichiers), les deux
  autres sont refuses avec une notification explicite si vous insistez.
- Les 3 viewers sont detailles dans leur propre section ci-dessous.""",
    ),
    (
        "Favoris",
        """\
Enregistre une combinaison (log(s) + viewer) sous un nom, pour un
lancement direct sans re-selectionner chaque fois.

- Partie haute : liste des favoris existants — [b]Lancer[/b] ouvre
  directement le viewer enregistre sur les logs enregistres ;
  [b]Supprimer[/b] retire le favori (apres confirmation, ne touche
  jamais aux fichiers de log reels).
- Partie basse ("Creer un favori") : memes NUMEROS separes par des
  virgules que "Voir les logs", + un nom + le viewer souhaite (Select),
  puis [b]Enregistrer[/b].
- Aucune verification de compatibilite n'est faite a la CREATION (vous
  pouvez enregistrer 3 logs + viewer "lnav" sans probleme) — la regle
  1 log/3 viewers vs 2+/lnav uniquement, elle, s'applique normalement au
  moment du [b]Lancer[/b].
- Un favori reference des CHEMINS, pas des entrees de Bibliotheque : si
  le fichier est deplace ou supprime, le favori reste mais son
  lancement echouera comme une ouverture normale sur un chemin absent.""",
    ),
    (
        "Voir et Traiter IP",
        """\
Top 10 des adresses IP les plus actives sur une periode, et suppression
ciblee d'une IP dans un ou plusieurs logs.

- Selection des logs par numeros (comme "Voir les logs"), puis une
  periode : [b]24h / 7j / 30j / Tout[/b]. Le calcul se lance au clic sur
  une periode, jamais automatiquement.
- Le calcul s'execute en ARRIERE-PLAN dans un processus separe (jamais
  sur le thread d'affichage, meme pour un gros fichier) — un indicateur
  "Calcul en cours..." s'affiche pendant l'attente, les boutons de
  periode sont desactives jusqu'a la fin pour eviter de lancer plusieurs
  calculs en meme temps sur le meme ecran.
- Periodes courtes (24h/7j/30j) : lecture optimisee EN PARTANT DE LA FIN
  du fichier, avec arret anticipe des que les lignes deviennent trop
  anciennes — tres rapide meme sur un fichier de plusieurs centaines de
  milliers de lignes. "Tout" lit l'integralite du fichier, forcement
  plus lent sur un gros volume.
- Cliquez une ligne du tableau de resultat pour la selectionner, puis
  [b]Retirer cette IP des logs analyses[/b] (toujours avec confirmation)
  pour supprimer DEFINITIVEMENT toutes les lignes contenant cette IP,
  dans TOUS les fichiers analyses pour ce calcul.
- Logs proteges (ex. /var/log/audit) : une authentification sudo
  ponctuelle est demandee automatiquement au moment ou elle est
  necessaire (lecture ou suppression), jamais a l'avance.""",
    ),
    (
        "Statistiques (acces)",
        """\
Volume, IPs uniques, taux d'erreur, top IPs, repartition horaire sur un
ou plusieurs logs d'acces — avec export.

- Memes principes que "Voir et Traiter IP" : selection par numeros,
  periode 24h/7j/30j/Tout, calcul en arriere-plan dans un processus
  separe (boutons de periode desactives pendant le calcul), lecture
  optimisee par periode courte, elevation sudo ponctuelle automatique
  sur un log protege.
- Le resume affiche : nombre de lignes analysees, IPs uniques, taux
  d'erreur (proportion de codes HTTP 4xx/5xx sur les lignes reconnues
  comme un access log), et le detail des 10 IPs les plus actives.
- Repartition horaire : histogramme texte (24 heures) du volume de
  requetes, utile pour reperer un pic d'activite inhabituel.
- [b]Exporter JSON[/b] / [b]Exporter HTML[/b] (5 themes graphiques au
  choix) : necessite d'avoir calcule au moins une fois (choisi une
  periode) avant de pouvoir exporter — le fichier produit est horodate,
  depose dans var/exports/.""",
    ),
    (
        "Rotate",
        """\
Sauvegarde compressee d'un log et restauration depuis une archive
precedente.

- [b]Sauvegarder maintenant[/b] : numero du log (un seul a la fois) +
  nombre de rotations a conserver (champ "Rotations a conserver", 7 par
  defaut) — au-dela de ce nombre, les archives les plus anciennes sont
  supprimees automatiquement a chaque nouvelle sauvegarde (retention
  automatique, jamais d'accumulation illimitee).
- Liste "Archives disponibles" : toutes les sauvegardes existantes,
  triees des plus recentes aux plus anciennes, avec taille et date.
- [b]Restaurer[/b] : selectionnez une archive dans la liste, choisissez
  le mode — [b]Fusion (append)[/b] ajoute le contenu de l'archive a la
  fin du fichier actuel ; [b]Ecrasement (overwrite)[/b] remplace
  entierement le contenu actuel par celui de l'archive. Une sauvegarde
  de securite du fichier cible est prise automatiquement AVANT toute
  restauration, pour pouvoir annuler en cas d'erreur.
- [b]Supprimer l'archive[/b] : suppression definitive d'une sauvegarde
  (apres confirmation) — ne touche jamais au log source.
- Log protege : elevation sudo ponctuelle automatique si necessaire,
  pour la sauvegarde comme pour la restauration.""",
    ),
    (
        "Purger",
        """\
Deux actions DISTINCTES et toutes deux irreversibles sans confirmation
prealable — a ne jamais confondre :

- [b]Vider le contenu[/b] : TRONQUE le(s) fichier(s) EN PLACE (le
  fichier continue d'exister, vide). Methode sure pour un log encore
  activement ecrit par un service qui le garde ouvert (contrairement a
  une suppression, qui casserait le descripteur de fichier du service
  tant qu'il n'est pas redemarre).
- [b]Supprimer le(s) fichier(s)[/b] : efface COMPLETEMENT le(s)
  fichier(s) du disque — plus aucune trace, le fichier disparait aussi
  de la Bibliotheque.
- Les deux actions acceptent une selection MULTIPLE par numeros separes
  par des virgules, et demandent TOUJOURS confirmation avant d'agir
  (la liste exacte des fichiers concernes est affichee dans la boite de
  confirmation).
- Pensez a [b]Rotate -> Sauvegarder maintenant[/b] avant de purger si
  vous voulez garder une trace du contenu actuel.""",
    ),
    (
        "Exporter",
        """\
Export de la liste des ARCHIVES (sauvegardes Rotate) en JSON ou en HTML
a theme — distinct de l'export des statistiques (present directement
dans l'ecran Statistiques).

- [b]Rafraichir[/b] : relit la liste des archives presentes sur le
  disque (utile si vous venez de sauvegarder ou de supprimer une archive
  depuis l'ecran Rotate).
- [b]Exporter JSON[/b] : structure brute (nom, taille en octets, date de
  creation) de chaque archive listee.
- [b]Exporter HTML[/b] : meme contenu, mis en forme avec le theme
  graphique choisi dans le Select au-dessus (5 themes disponibles,
  memes palettes que l'export des Statistiques).
- Le fichier produit est horodate et depose dans var/exports/ (le meme
  dossier que les exports de Statistiques).""",
    ),
    (
        "Options",
        """\
Reglages de l'application elle-meme (pas des logs traites).

- [b]Theme[/b] : 10 themes disponibles, applique IMMEDIATEMENT a la
  selection, sans confirmation ni redemarrage (equivalent a appuyer
  plusieurs fois sur la touche [b]t[/b]).
- [b]Profil de rendu[/b] : force un niveau d'adaptation au terminal
  (complet/standard/reduit/mono) au lieu de la detection automatique —
  nécessite un REDEMARRAGE de l'application pour prendre effet
  ("Automatique" restaure la detection normale).
- [b]Vider le dossier exports[/b] / [b]Vider le dossier screenshots[/b] :
  supprime definitivement TOUS les fichiers de ces dossiers applicatifs
  (apres confirmation) — n'affecte jamais les logs surveilles ni leurs
  archives Rotate.""",
    ),
)

_VIEWERS = """\
[b]1. Simple[/b] — suivi en direct avec parsing generique (horodatage,
niveau, IP, service detecte) + mini-tableau de statistiques a cote
(IPs uniques, taux d'erreur, top IP). Pour un access log HTTP reconnu
(format Combined/Common), deux colonnes supplementaires apparaissent
automatiquement : [b]Code[/b] (statut HTTP, colore 2xx vert/3xx cyan/
4xx jaune/5xx rouge) et [b]Timeout[/b] (latence si le format source la
fournit, colore selon le seuil) — ces colonnes affichent "-" pour tout
ce qui n'est pas un format HTTP reconnu (auth.log, syslog, fail2ban...).

[b]2. Classique[/b] — affiche les dernieres lignes BRUTES du fichier
(aucun parsing, aucune coloration), avec un bouton [b]Suivre en
direct[/b] pour basculer en mode tail -f. Le plus simple et le plus
fiable quel que soit le format du fichier.

[b]3. lnav[/b] — encapsule le programme externe `lnav` dans un terminal
dedie (pty), pour une fusion et une analyse croisee de PLUSIEURS
fichiers a la fois (merge automatique par horodatage). Necessite que
`lnav` soit installe sur le systeme (sudo pacman -S lnav / sudo apt
install lnav) — sans lui, ce viewer est propose mais refuse de se
lancer avec un message explicite. Raccourcis specifiques pendant une
session lnav :"""

_GLOSSARY = """\
[b]Elevation sudo ponctuelle[/b] — l'application ne tourne JAMAIS en
root par defaut. Quand une action rencontre reellement une permission
refusee (ex. /var/log/audit/, lisible seulement par root), une
authentification sudo est demandee A CE moment precis, dans le
terminal reel (l'interface se suspend brievement) — jamais a l'avance,
jamais pour des actions qui n'en ont pas besoin. Une fois authentifie
pour un ecran donne, les actions suivantes sur ce meme ecran reutilisent
l'autorisation sans redemander.

[b]Etats SUSPECT / ABSENT / OK[/b] — SUSPECT : fichier present mais
vide (tres souvent un service qui route en realite vers journald plutot
que vers un fichier classique). ABSENT : chemin introuvable au moment de
l'affichage (supprime, pas encore cree, ou chemin errone). OK : fichier
present et non vide. Ces etats sont INFORMATIFS, jamais bloquants —
vous pouvez toujours ouvrir, exporter ou purger un log quel que soit son
etat affiche.

[b]Selection par numeros[/b] — convention commune a la majorite des
ecrans (Voir les logs, Favoris, Voir et Traiter IP, Statistiques,
Rotate, Purger) : le tableau affiche un numero par ligne, et vous
saisissez les numeros voulus separes par des virgules (ex. "1,3,4")
dans le champ de saisie plutot que de cliquer dans le tableau.

[b]Dossier var/[/b] — tout l'etat propre a l'application (bibliotheque,
favoris, theme choisi, archives de sauvegarde, exports, journal
applicatif) vit dans ./var/, relatif au dossier ou vous lancez
l'application (ou $OMEGA_LOG_VAR_DIR si defini) — jamais dans votre
dossier personnel. Ce dossier est entierement local a la machine, ne
contient aucun des LOGS SURVEILLES eux-memes (seulement des references
vers leurs chemins)."""


class HelpScreen(OmegaScreen):
    """Reference statique, accessible depuis n'importe quel ecran (touche `a`)."""

    def compose(self) -> ComposeResult:
        yield Header()
        with VerticalScroll(classes="omega-panel"):
            yield Static("AIDE", classes="omega-title")

            yield Static("Raccourcis clavier", classes="omega-subtitle")
            for key, description in _SHORTCUTS:
                yield Static(f"{key:<16} {description}")
            yield Static("")

            with Collapsible(title="Demarrage rapide", collapsed=False):
                yield Static(_QUICKSTART)

            yield Static("Fonctions, ecran par ecran", classes="omega-subtitle")
            for title, description in _SECTIONS:
                with Collapsible(title=title, collapsed=True):
                    yield Static(description)

            with Collapsible(title="Les 3 viewers (Simple / Classique / lnav)", collapsed=True):
                yield Static(_VIEWERS)
                for key, description in _LNAV_SHORTCUTS:
                    yield Static(f"  {key:<24} {description}")

            with Collapsible(title="Concepts et glossaire", collapsed=True):
                yield Static(_GLOSSARY)

            with Horizontal(classes="omega-actions"), Container(classes="omega-btn-frame"):
                yield Button("Retour", id="back")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "back":
            self.dismiss()
