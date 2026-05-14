# Foundry Monitor Mirror

![Aperçu de l'application](MonitorMirror_rAW2VknqMV.png)

**Foundry Monitor Mirror** est un utilitaire Windows haute performance conçu pour projeter un second moniteur dans une fenêtre tout en conservant le contrôle de la souris. 

Cet outil est idéal pour les sessions de jeu de rôle sur table utilisant **Foundry VTT** (ou tout autre VTT) en personne, particulièrement lorsque vous utilisez un téléviseur comme surface de jeu et que vous êtes positionné à l'envers ou sur le côté par rapport à l'écran.

## Fonctionnalités

- **Capture Haute Performance** : Utilise `DXCAM` (DXGI) pour une latence quasi nulle et un support fluide jusqu'à 60 FPS.
- **Optimisation des Ressources** : Rendu optimisé via QPainter pour minimiser l'usage du CPU et de la RAM, même en haute résolution.
- **Repli Automatique** : Bascule automatiquement vers `MSS` si la capture matérielle accélérée n'est pas disponible.
- **Contrôle de la Souris** : Transmet les clics gauches, clics droits et glissements vers le moniteur cible.
- **Miroir du Curseur** : Affiche la position de votre souris en temps réel dans la fenêtre miroir de manière fluide.
- **Logs de Débogage** : Console intégrée et compteur FPS pour surveiller les performances.

## Instructions d'Installation

### 1. Prérequis
- Windows 10 ou 11.
- Python 3.10 ou supérieur.
- Un GPU supportant DXGI (la plupart des GPU modernes Intel/NVIDIA/AMD).

### 2. Installer les Dépendances
Ouvrez votre terminal et lancez :
```bash
pip install -r requirements.txt
```

### 3. Lancer depuis les Sources
```bash
python monitor_mirror.py
```

### 4. Compiler l'Exécutable
Pour créer un `.exe` autonome (généré dans le dossier `dist`) :
```bash
python build_exe.py
```

## Dépannage

- **Privilèges Administrateur** : Si vous devez contrôler des applications lancées en tant qu'administrateur (comme le Gestionnaire des tâches), vous devez lancer `MonitorMirror.exe` en tant qu'administrateur.
- **Écran Noir / Blocage à l'initialisation** : Vérifiez les logs dans la console. L'application tente d'itérer sur les périphériques GPU disponibles. En cas d'échec total, elle repassera en mode de compatibilité `MSS`.
- **Performances** : Si vous n'atteignez pas 60 FPS, vérifiez que vous êtes bien en mode "DXCAM" dans le titre de la fenêtre.
