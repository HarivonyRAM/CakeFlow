# CakeFlow - Délice et Douceur chez A

Application Desktop de gestion de pâtisserie développée avec PyQt5.
Développé par RAMINOMIANDRISOA Harivony

## Structure du projet

```
Cakeflow/
│
├── app/
│   ├── main.py                        # Point d'entrée de l'application
│   │
│   ├── ui/
│   │   ├── Login.ui                   # Page de connexion (Qt Designer)
│   │   ├── Login_ui.py                # Code généré depuis Login.ui
│   │   ├── Dashboard.ui              # Dashboard principal (Qt Designer)
│   │   ├── Dashboard_ui.py           # Code généré depuis Dashboard.ui
│   │   │
│   │   ├── widgets/
│   │   │   ├── Sidebar.ui            # Barre latérale (Qt Designer)
│   │   │   ├── Sidebar_ui.py         # Code généré depuis Sidebar.ui
│   │   │   ├── Header.ui             # En-tête (Qt Designer)
│   │   │   ├── Header_ui.py          # Code généré depuis Header.ui
│   │   │   ├── Card.ui               # Carte statistique (Qt Designer)
│   │   │   └── Card_ui.py            # Code généré depuis Card.ui
│   │   │
│   │   ├── resources.qrc             # Fichier de ressources Qt
│   │   ├── resources_rc.py           # Ressources compilées
│   │   ├── style.qss                 # Feuille de style globale
│   │   │
│   │   ├── login_window.py           # Logique du login
│   │   ├── main_window.py            # Logique du dashboard
│   │   ├── clients_window.py         # Gestion des clients
│   │   └── utilisateurs_page.py      # Gestion des utilisateurs et rôles
│   │
│   ├── services/
│   │   ├── auth_service.py            # Authentification
│   │   ├── client_service.py          # Logique métier clients
│   │   ├── commande_service.py        # Logique métier commandes
│   │   └── navigation_service.py      # Navigation entre les pages
│   │
│   ├── repositories/
│   │   ├── user_repo.py               # Accès données utilisateurs
│   │   ├── client_repo.py             # Accès données clients
│   │   ├── commande_repo.py           # Accès données commandes
│   │   ├── contact_repo.py            # Accès données contacts
│   │   ├── historique_repo.py         # Accès données historique
│   │   ├── paiement_repo.py           # Accès données paiements
│   │   └── produit_repo.py            # Accès données produits
│   │
│   ├── db/
│   │   ├── connection.py              # Connexion à la base de données
│   │   └── init_db.py                 # Initialisation des tables
│   │
│   └── utils/
│       ├── security.py                # Hachage des mots de passe (bcrypt)
│       └── helpers.py                 # Fonctions utilitaires
│
├── assets/
│   ├── images/
│   ├── icons/
│   └── fonts/
│
├── DDA.db                             # Base de données SQLite
├── .gitignore                         # Fichiers ignorés par Git
├── requirements.txt                   # Dépendances Python
└── README.md                          # Documentation du projet
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
