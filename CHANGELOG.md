# Changelog

Format inspiré de [Keep a Changelog](https://keepachangelog.com/).

## [1.6.0] — 2026-11-07

### Ajouté

- **Santé des logs** (menu MAINTENANCE, après Exporter), reprise d'omega-serv 2.6.0 : contrôle en lecture seule des logs de la Bibliothèque, du disque qui les porte, des sauvegardes et des sauvegardes planifiées. Fichier absent ou lien cassé, illisible par votre compte, inscriptible par tout le monde, log muet depuis plus de 7 jours, vide, dates non reconnues ou dans le futur, octets nuls, gros log sans règle logrotate, doublon ; jours avant disque plein. Chaque constat dit quoi faire. « Analyser avec sudo » lit le début et la fin des logs illisibles ; « Corriger les droits » / « Corriger avec sudo » retirent l'écriture pour tout le monde (`chmod o-w`, montré avant). Export JSON, HTML et TXT, dans la langue des exports.
- **Sauvegardes planifiées** (Rotate → « Sauvegardes planifiées ») : un log est sauvegardé automatiquement tous les jours, toutes les semaines ou tous les mois, avec le nombre de sauvegardes conservées. La première installe une tâche quotidienne (timer systemd, mot de passe sudo demandé ; sinon une ligne de votre crontab pour OpenRC/runit ; sinon la ligne à ajouter est affichée), la dernière supprimée la retire ; « Désinstaller l'exécution » la retire à la demande sans effacer les sauvegardes planifiées, « Réinstaller l'exécution » la remet. Chaque nuit, la nouvelle commande `omega-log rotate run-automations` sauvegarde, sous votre compte (jamais root), chaque log arrivé à échéance ; échec ou retard signalés dans Santé des logs.
- **Voir et Traiter IP : recherche d'une IP précise** : saisir une IP (IPv4 ou IPv6), voir son nombre de lignes dans chaque log sélectionné (fichier entier) et la retirer directement, sans attendre qu'elle apparaisse dans le top.
- **Version affichée et vérification des mises à jour** : la barre de titre montre la version (« OMEGA-LOG 1.6.0 »), lue dans `pyproject.toml` (le splash aussi, « ▒V1.60▒ »). Aide → Contact et support → « Vérifier les mises à jour » compare votre version à la liste publiée sur le site, seulement sur votre clic ; « Voir les nouveautés » ouvre le résumé. En ligne de commande : `omega-log version [--check]`.
- **Publication numérotée** : `build-release.sh` produit `omega-log-<version>.tar.gz` dans `html/download/`, avec `sha.txt` (une empreinte par version) et le résumé des nouveautés, comme omega-serv.

### Modifié

- Menu principal : le bouton « Quitter » est retiré (q, Ctrl+Q et Échap sur l'accueil quittent toujours, avec confirmation).
- Viewer Simple : panneau remonté (trois lignes de plus pour le cadre de statistiques) et une colonne vide entre les chiffres et l'ascenseur.
- Aide : quatre sections ajoutées (recherche d'une IP précise, sauvegardes planifiées, Santé des logs, version et mises à jour).
- Langues : les 16 traductions sont validées, la mention « (en test) » disparaît du choix de la langue.
- Documentation : README traduit dans les 16 autres langues (`docs/translation/<code>/README.md`, comme omega-serv), barre des 17 langues avec drapeaux ; les anciens `README.en/es/ru/zh.md` de la racine sont retirés.
- Site : page de présentation et page README dans les 17 langues (`translation/<code>/`), galerie de 79 captures à la même dimension.

### Corrigé

- Hindi : cadres, boutons et colonnes décalés (voyelles comptées pour 0 colonne au lieu de 1), correctif d'omega-serv et d'omega-fire repris d'omega-lib.
- Arabe : texte remis dans l'ordre droite-à-gauche par omega-log, le terminal ne déplace plus les cadres ni les boutons (même correctif qu'omega-serv et omega-fire).
- **Voir et Traiter IP** : « Retirer cette IP » ne retirait aucune ligne pour une IPv6 terminée par `::` (par exemple `2a03:2880:f800:15::`) ; une IP n'est plus jamais confondue avec une IP plus longue (1.1.1.1 et 1.1.1.11).
- **Logs protégés lus avec sudo** (Statistiques, Voir et Traiter IP) : la lecture sudo se fait dans le processus de l'interface, plus dans les processus de calcul, qui ne voyaient pas l'authentification quand sudoers la mémorise par processus parent (`timestamp_type=ppid`).
- **Archive** : `var/declaration.json` (votre déclaration anonyme et sa clé) était livré dans l'archive 1.5.0 ; il est maintenant exclu, comme les sources SSH et les sauvegardes planifiées.
- **Bibliothèque** : la barre de statut n'affichait qu'Échap (le curseur démarrait dans le champ de saisie, où q, t, r, a, s servent à taper) ; l'écran démarre maintenant sur la liste des logs.
- **Options** : ouvrir l'écran affichait une notification « Langue des exports » comme si on avait choisi une option ; seul un vrai changement est maintenant appliqué et annoncé.
- **Options** : le formulaire n'était plus centré (le bloc de choix de langue prenait toute la largeur).
- **lnav** : choisir lnav ouvrait un écran intermédiaire qui redemandait « Lancer lnav » ; lnav se lance maintenant directement (Voir les logs, Favoris, Registre) et l'on revient à l'écran précédent en le quittant. L'écran ne reste affiché qu'en cas d'échec, avec l'erreur et un bouton pour réessayer ; la trace complète d'un échec est écrite dans `var/app.log` (une erreur « string index out of range » vue une fois n'a pas pu être reproduite).

## [1.5.0] — 2026-11-07

### Ajouté

- Interface en 17 langues (français, anglais, espagnol, portugais (Brésil), italien, allemand, néerlandais, polonais, russe, chinois simplifié, vietnamien, thaï, indonésien, japonais, coréen, hindi et arabe) : Options → « Langue / Language », appliquée après un redémarrage de l'interface ; variable `OMEGA_LOG_LANG` pour forcer une langue le temps d'une session.
- Réglage « Langue des exports » (« Comme l'interface » par défaut) : l'aide et les rapports HTML (statistiques, archives) s'écrivent dans la langue choisie ; en arabe, le rapport HTML se lit de droite à gauche. Les exports JSON restent des données (clés et valeurs inchangées).
- Statistiques et Voir et traiter IP : calcul en flux sur plusieurs cœurs pour les gros logs, barre de progression réelle, taille et nombre de lignes estimés de la sélection, « Tout (fichier entier) » avec avertissement de durée.
- Statistiques : rapport riche à l'écran et à l'export HTML/JSON (synthèse, statuts HTTP en jauges, top IP, chemins demandés et en 404, répartition horaire, tendance par jour).
- Bibliothèque : « Ajouter les logs connus d'Omega-Serv » et « Sources distantes (SSH) ».
- Viewer Simple repris d'omega-serv (tableau de bord qui défile, 403/429, top 5 IP, chemins).
- Aide : export HTML de toute l'aide ; « Contact et support » (café, déclaration anonyme unique, support).

### Modifié

- Accents rétablis dans tous les textes français de l'interface et des rapports.
- Messages restés en anglais réécrits en français (archives, sauvegardes, sondes de programmes).
- La ligne de commande reste en français.

### Corrigé

- Pendant une analyse, le message « Échap pour revenir à tout moment » était faux : Échap arrête l'analyse. Il dit maintenant « Échap arrête l'analyse : il faudra la relancer. »
- Statistiques, Favoris, Voir et traiter IP, Sources SSH, Rotation : la liste des logs ne se réduit plus à sa ligne de titre.
- Statistiques et Voir et traiter IP : « environ N lignes » (taille de la sélection) restait en français dans les autres langues ; la phrase est maintenant traduite.
- Statistiques : « Refus 403 » et « Refus 429 » étaient coupés quand leur traduction dépasse 10 caractères (« Abgewiese… » en allemand) ; la colonne prend la largeur du plus long libellé.
- Parseur des logs d'accès plus rapide (résultats identiques).
