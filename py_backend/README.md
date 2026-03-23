# 🐍 Clara Backend Python - FastAPI

Backend Python pour l'application Clara, basé sur FastAPI.

## 🚀 Fonctionnalités

### Core API
- **FastAPI** : Framework web moderne et rapide
- **Uvicorn** : Serveur ASGI haute performance
- **CORS** : Support multi-origines
- **Documentation** : Swagger UI et ReDoc automatiques

### Services Disponibles

#### 1. LightRAG Notebooks
- Création et gestion de notebooks RAG
- Upload et traitement de documents (PDF, TXT, MD, CSV, JSON)
- Interrogation intelligente avec LLM
- Support multi-providers (OpenAI, Ollama, etc.)

#### 2. Pandas API
- Analyse de données avec Pandas
- Agent Pandas avec LLM (Gemini)
- Manipulation de DataFrames
- Export de résultats

#### 3. États Financiers SYSCOHADA
- **Génération d'états financiers** au format liasse officielle
- **Conformité SYSCOHADA** Révisé
- **Analyse de balances comptables** multi-exercices (N, N-1, N-2)
- **Format liasse officielle** avec 2 colonnes (Exercice N et N-1)
- **Tableau des Flux de Trésorerie (TFT)** - Méthode indirecte
- **Annexes calculables** (13 notes)
- **États de contrôle** exhaustifs (16 contrôles)
- **Export Excel** vers liasse officielle vierge
- **Flexibilité multi-entreprises** avec différents plans comptables

#### 4. Échantillonnage Audit
- Calculs d'échantillonnage statistique
- Méthodes d'audit

#### 5. Export Word
- Génération de documents Word
- Templates personnalisables

#### 6. Speech Services
- **Speech-to-Text** : Transcription audio (Whisper)
- **Text-to-Speech** : Synthèse vocale (gTTS, pyttsx3, Kokoro)

#### 7. Google Drive Proxy
- Accès aux fichiers PDF Google Drive
- Proxy pour contourner les restrictions CORS

## 📋 Prérequis

- Python 3.11+
- pip ou uv (gestionnaire de paquets)

## 🔧 Installation

### 1. Cloner le repository

```bash
git clone https://github.com/sekadalle2024/Back-end-python-V0_03_03_2026.git
cd Back-end-python-V0_03_03_2026
```

### 2. Créer un environnement virtuel

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4. Installer le modèle spaCy

```bash
python -m spacy download en_core_web_sm
```

## 🚀 Démarrage

### Mode Développement

```bash
python main.py
```

L'API sera accessible sur : `http://localhost:5000`

### Mode Production

```bash
uvicorn main:app --host 0.0.0.0 --port 5000
```

## 📚 Documentation

Une fois le serveur démarré, accédez à :

- **Swagger UI** : http://localhost:5000/docs
- **ReDoc** : http://localhost:5000/redoc
- **Health Check** : http://localhost:5000/health

## 🐳 Docker

### Build

```bash
docker build -t clara-backend .
```

### Run

```bash
docker run -p 5000:5000 \
  -e HOST=0.0.0.0 \
  -e PORT=5000 \
  clara-backend
```

## ⚙️ Configuration

### Variables d'Environnement

Créez un fichier `.env` :

```env
# Serveur
HOST=0.0.0.0
PORT=5000
PYTHONUNBUFFERED=1

# OpenAI (optionnel)
OPENAI_API_KEY=sk-...

# Neo4j (optionnel - pour LightRAG)
NEO4J_URI=neo4j://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=password

# Google API (optionnel)
GOOGLE_API_KEY=...

# N8N (optionnel)
N8N_WEBHOOK_URL=https://...
```

## 📊 Endpoints Principaux

### Core
```
GET  /              → Root endpoint
GET  /health        → Health check
GET  /docs          → Documentation Swagger
GET  /redoc         → Documentation ReDoc
```

### LightRAG
```
POST /notebooks                    → Créer un notebook
GET  /notebooks                    → Lister les notebooks
POST /notebooks/{id}/documents     → Upload documents
POST /notebooks/{id}/query         → Interroger un notebook
```

### Pandas
```
POST /pandas/analyze               → Analyse de données
POST /pandas/agent                 → Agent Pandas avec LLM
```

### États Financiers
```
POST /etats-financiers/process-excel  → Générer états financiers (format liasse)
POST /export-liasse/generer            → Export vers liasse Excel officielle
```

**Fichiers clés**:
- `etats_financiers.py` - Module principal
- `etats_financiers_v2.py` - Format liasse officielle
- `generer_etats_liasse.py` - Script autonome
- `tableau_flux_tresorerie.py` - TFT
- `annexes_liasse.py` - Annexes
- `export_liasse.py` - Export Excel

## 🚀 Déploiement

### Koyeb

1. Connectez votre repository GitHub à Koyeb
2. Configurez :
   - Builder : `Dockerfile`
   - Port : `5000`
   - Instance : `nano` (gratuit) ou plus
3. Ajoutez les variables d'environnement
4. Déployez !

Voir `README_KOYEB.md` pour plus de détails.

### Autres Plateformes

Le backend peut être déployé sur :
- Render
- Railway
- Fly.io
- Heroku
- AWS/GCP/Azure

## 🧪 Tests

```bash
# Tests unitaires
pytest

# Tests avec coverage
pytest --cov=.

# Tests états financiers
cd py_backend
conda run -n claraverse_backend python test_etats_financiers.py
conda run -n claraverse_backend python test_tft_standalone.py
conda run -n claraverse_backend python test_annexes_standalone.py

# Générer états financiers format liasse
conda run -n claraverse_backend python generer_etats_liasse.py
```

## 📁 Structure du Projet

```
py_backend/
├── main.py                         # Point d'entrée FastAPI
├── Dockerfile                      # Configuration Docker
├── requirements.txt                # Dépendances Python
├── README.md                       # Ce fichier
│
├── pandas_api.py                   # API Pandas
├── pandas_agent.py                 # Agent Pandas avec LLM
├── pandas_lead.py                  # Lead Balance
│
├── etats_financiers.py             # États financiers SYSCOHADA
├── etats_financiers_v2.py          # Format liasse officielle
├── generer_etats_liasse.py         # Script autonome génération
├── tableau_flux_tresorerie.py      # TFT (méthode indirecte)
├── annexes_liasse.py               # Annexes (13 notes)
├── annexes_html.py                 # Génération HTML annexes
├── export_liasse.py                # Export Excel liasse
├── correspondances_syscohada.json  # Mapping comptes → postes
├── structure_liasse_complete.json  # Structure complète liasse
│
├── echantillonnage.py              # Échantillonnage audit
├── word_export.py                  # Export Word
├── Speech2Text.py                  # Transcription audio
├── Text2Speech.py                  # Synthèse vocale
│
├── gdrive_proxy.py                 # Proxy Google Drive
├── n8n_proxy.py                    # Proxy N8N
│
├── test_*.py                       # Tests unitaires
├── BALANCES_N_N1_N2.xlsx          # Fichier test multi-exercices
│
└── lib/                            # Bibliothèques
```

## 🤝 Contribution

Les contributions sont les bienvenues !

1. Fork le projet
2. Créez une branche (`git checkout -b feature/AmazingFeature`)
3. Commit vos changements (`git commit -m 'Add AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrez une Pull Request

## 📝 Licence

Ce projet fait partie de Clara - Assistant IA

## 🔗 Liens

- **Frontend** : [Clara Frontend](https://github.com/sekadalle2024/...)
- **Documentation** : Voir `/docs` après démarrage
- **Issues** : [GitHub Issues](https://github.com/sekadalle2024/Back-end-python-V0_03_03_2026/issues)

## 📧 Contact

Pour toute question : [Créer une issue](https://github.com/sekadalle2024/Back-end-python-V0_03_03_2026/issues)

---

**Version** : 1.0.0  
**Date** : 22 mars 2026  
**Python** : 3.11+  
**Framework** : FastAPI

## 📚 Documentation Complémentaire

### États Financiers
- `Doc_Etat_Fin/00_INDEX_COMPLET.md` - Index complet
- `GUIDE_UTILISATEUR_ETATS_LIASSE.md` - Guide utilisateur
- `FLEXIBILITE_MULTI_ENTREPRISES.md` - Guide technique
- `RECAPITULATIF_CORRECTION_FORMAT_LIASSE.md` - Récapitulatif

### Lead Balance
- `Doc_Lead_Balance/00_INDEX.md` - Index complet
- `Doc_Lead_Balance/README.md` - Documentation

### Déploiement
- `README_KOYEB.md` - Déploiement Koyeb
- `00_INDEX_DEPLOIEMENT_COMPLET.md` - Guide complet
