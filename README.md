# CakeFlow


project/
│
├── app/
│ ├── main.py
│ ├── ui/
│ │ ├── login_window.py
│ │ ├── main_window.py
│ │ └── clients_window.py
│ │
│ ├── services/
│ │ ├── auth_service.py
│ │ ├── client_service.py
│ │ ├── commande_service.py
│ │
│ ├── repositories/
│ │ ├── user_repo.py
│ │ ├── client_repo.py
│ │ ├── commande_repo.py
│ │
│ ├── db/
│ │ ├── connection.py
│ │ └── init_db.py
│ │
│ └── utils/
│ ├── security.py (bcrypt)
│ └── helpers.py
│
└── requirements.txt