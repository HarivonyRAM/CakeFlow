# CakeFlow - Délice et Douceur chez A

Application de gestion de pâtisserie développée avec PyQt5.

## Structure du projet

```
project/
│
├── app/
│   ├── main.py                    # Point d'entrée
│   │
│   ├── ui/
│   │   ├── Login.ui               # Page de connexion (Qt Designer)
│   │   ├── Dashboard.ui           # Dashboard principal (Qt Designer)
│   │   ├── widgets/
│   │   │   ├── Sidebar.ui         # Barre latérale
│   │   │   ├── Header.ui          # En-tête
│   │   │   └── Card.ui            # Carte statistique
│   │   │
│   │   ├── resources.qrc          # Fichier de ressources Qt
│   │   ├── style.qss              # Feuille de style globale
│   │   │
│   │   ├── login_window.py        # Logique du login
│   │   ├── main_window.py         # Logique du dashboard
│   │   └── clients_window.py      # Gestion des clients
│   │
│   ├── services/
│   │   ├── auth_service.py
│   │   ├── client_service.py
│   │   └── commande_service.py
│   │
│   ├── repositories/
│   │   ├── user_repo.py
│   │   ├── client_repo.py
│   │   └── commande_repo.py
│   │
│   ├── db/
│   │   ├── connection.py
│   │   └── init_db.py
│   │
│   └── utils/
│       ├── security.py (bcrypt)
│       └── helpers.py
│
├── assets/
│   ├── images/
│   │   ├── login_cake.jpg
│   │   ├── logo.png
│   │   └── background.png
│   │
│   ├── icons/
│   │   ├── user.svg
│   │   ├── lock.svg
│   │   ├── eye.svg
│   │   ├── login.svg
│   │   └── cake.svg
│   │
│   └── fonts/
│
└── requirements.txt
```

## Couleurs du thème

| Couleur | Hex | Usage |
|---------|-----|-------|
| Primary | `#e91e90` | Boutons, accents, éléments actifs |
| Secondary | `#c2185b` | Titres, hover, dégradés |
| Background | `#fff5f7` | Fond principal |
| Accent | `#fce4ec` | Cartes, badges, fond léger |
| Text | `#333333` | Texte principal |
| Text Light | `#999999` | Texte secondaire |
| Border | `#f0c0d0` | Bordures des inputs |

## Utilisation

### Ouvrir Login.ui dans Qt Designer
```bash
designer app/ui/Login.ui
```

### Lancer l'application
```bash
python app/main.py
```

### Installer les dépendances
```bash
pip install -r requirements.txt
```