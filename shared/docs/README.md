# Plateforme Freelance - Architecture Microservices

Ce projet est une plateforme de gestion de CV et de profils freelances basée sur une architecture microservices. Il permet l'extraction automatique d'informations depuis des CV et la génération de fichiers Excel formatés.

## Architecture

Le projet est composé de plusieurs microservices :

### 1. Service d'Extraction de CV (`cv-extraction-service`)
- **Port**: 8000
- **Fonctionnalités**:
  - Extraction de texte depuis des fichiers PDF
  - Analyse sémantique avec l'API Mistral
  - Structuration des données en JSON
  - Validation des données avec Pydantic

### 2. Service de Génération Excel (`excel-generator-service`)
- **Port**: 8001
- **Fonctionnalités**:
  - Génération de fichiers Excel formatés
  - Gestion des différentes sections du CV
  - Formatage avancé des données
  - Stockage temporaire des fichiers

## Structure du Projet

```
plateformes_Freelance/
├── cv-extraction-service/
│   ├── src/
│   │   ├── api/          # Routes API FastAPI
│   │   ├── core/         # Configuration et utilitaires
│   │   ├── models/       # Modèles Pydantic
│   │   └── services/     # Logique métier
│   ├── tests/            # Tests unitaires
│   ├── Dockerfile
│   └── requirements.txt
│
└── excel-generator-service/
    ├── src/
    │   ├── api/          # Routes API FastAPI
    │   ├── core/         # Configuration et utilitaires
    │   ├── models/       # Modèles Pydantic
    │   └── services/     # Logique métier
    ├── tests/            # Tests unitaires
    ├── docker-compose.yml
    ├── Dockerfile
    └── requirements.txt
```

## Prérequis

- Python 3.11+
- Docker et Docker Compose
- API Key Mistral (pour le service d'extraction)

## Installation

1. Cloner le dépôt :
```bash
git clone [URL_DU_REPO]
cd plateformes_Freelance
```

2. Configurer les variables d'environnement :
```bash
# Pour le service d'extraction
cp cv-extraction-service/.env.example cv-extraction-service/.env
# Éditer .env avec vos configurations

# Pour le service de génération Excel
cp excel-generator-service/.env.example excel-generator-service/.env
# Éditer .env avec vos configurations
```

3. Lancer les services avec Docker Compose :
```bash
cd excel-generator-service
docker-compose up -d
```

## Utilisation

### Service d'Extraction de CV

1. Envoyer un CV au format PDF :
```bash
curl -X POST http://localhost:8000/api/v1/cv/extract \
  -H "Content-Type: multipart/form-data" \
  -F "file=@chemin/vers/cv.pdf"
```

2. Récupérer les données extraites :
```bash
curl http://localhost:8000/api/v1/cv/{file_id}
```

### Service de Génération Excel

1. Générer un fichier Excel :
```bash
curl -X POST http://localhost:8001/api/v1/excel/generate \
  -H "Content-Type: application/json" \
  -d @chemin/vers/donnees.json
```

2. Télécharger le fichier généré :
```bash
curl http://localhost:8001/api/v1/excel/download/{file_id} \
  -o cv_generé.xlsx
```

## Développement

### Tests

Pour exécuter les tests :
```bash
# Service d'extraction
cd cv-extraction-service
pytest

# Service de génération Excel
cd excel-generator-service
pytest
```

### Documentation API

La documentation Swagger est disponible pour chaque service :
- Service d'extraction : http://localhost:8000/docs
- Service de génération Excel : http://localhost:8001/docs

## Sécurité

- Les fichiers sont stockés temporairement et supprimés après un délai configurable
- Validation stricte des données d'entrée
- Protection CORS configurable
- Gestion des erreurs et logging

## Contribution

1. Fork le projet
2. Créer une branche (`git checkout -b feature/nouvelle-fonctionnalite`)
3. Commit les changements (`git commit -am 'Ajout d'une nouvelle fonctionnalité'`)
4. Push la branche (`git push origin feature/nouvelle-fonctionnalite`)
5. Créer une Pull Request

## Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## Contact

Pour toute question ou suggestion, n'hésitez pas à ouvrir une issue dans le dépôt GitHub.