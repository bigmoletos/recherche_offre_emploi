# Solution Agent IA Recherche d'Offres d'Alternance

## 🎯 Objectif
Développer un agent IA capable de rechercher automatiquement des offres d'emploi en alternance dans le domaine cybersécurité/réseaux télécommunications, en excluant les formations et en générant un rapport Excel exploitable.

## 📊 Analyse des Options

### Option 1 : 🚀 Solution Hybride n8n + Python (RECOMMANDÉE)
**Temps de développement : 2-3 jours**

#### Avantages
- Orchestration visuelle avec n8n
- Code Python personnalisé pour le scraping complexe
- Interface de monitoring intégrée
- Évolutivité et maintenance facilitées

#### Architecture
```
[Déclencheur Cron] → [Scraper Python] → [Filtrage IA] → [Génération Excel] → [Notification]
```

#### Workflow n8n
1. **Déclencheur temporel** : Exécution automatique quotidienne
2. **Nœud Python Script** : Scripts de scraping par site
3. **LLM Claude/OpenAI** : Filtrage intelligent des offres
4. **Nœud Excel** : Génération du rapport
5. **Notification Slack/Email** : Envoi du rapport

### Option 2 : 🐍 Solution Python Pure
**Temps de développement : 3-4 jours**

#### Avantages
- Contrôle total sur la logique
- Performance optimisée
- Facilité de débogage

#### Inconvénients
- Pas d'interface de monitoring
- Maintenance plus complexe

### Option 3 : 🤖 Solution n8n Pure
**Temps de développement : 4-5 jours**

#### Avantages
- Interface visuelle complète
- Intégrations natives

#### Inconvénients
- Limité pour le scraping complexe
- Gestion d'erreurs basique

## 🛠️ Implémentation Solution Hybride

### Structure du Projet
```
agent_alternance/
├── n8n_workflows/
│   └── recherche_alternance.json
├── python_scrapers/
│   ├── base_scraper.py
│   ├── pole_emploi_scraper.py
│   ├── indeed_scraper.py
│   └── apec_scraper.py
├── ai_filters/
│   ├── classifier.py
│   └── prompt_templates.py
├── excel_generator/
│   └── report_builder.py
├── config/
│   ├── settings.py
│   └── credentials.env
├── logs/
├── outputs/
└── requirements.txt
```

### Composants Clés

#### 1. Workflow n8n Principal
```json
{
  "name": "Recherche Alternance Cybersécurité",
  "nodes": [
    {
      "type": "n8n-nodes-base.cron",
      "name": "Déclencheur Quotidien",
      "parameters": {
        "rule": {
          "hour": 9,
          "minute": 0
        }
      }
    },
    {
      "type": "n8n-nodes-base.executeCommand",
      "name": "Lancer Scraping",
      "parameters": {
        "command": "python /app/scrapers/main_scraper.py"
      }
    },
    {
      "type": "@n8n/n8n-nodes-langchain.lmChatOpenAi",
      "name": "Filtrage IA",
      "parameters": {
        "model": "gpt-4",
        "systemPrompt": "Tu es un expert en filtrage d'offres d'emploi..."
      }
    }
  ]
}
```

#### 2. Scraper Base Python
```python
class BaseScraper:
    """Classe de base pour tous les scrapers d'offres d'alternance."""

    def __init__(self, site_name: str):
        self.site_name = site_name
        self.session = requests.Session()
        self.logger = self._setup_logger()

    def scrape_offers(self, keywords: List[str]) -> List[Dict]:
        """Méthode abstraite à implémenter par chaque scraper."""
        raise NotImplementedError

    def filter_alternance_only(self, offers: List[Dict]) -> List[Dict]:
        """Filtre uniquement les offres d'alternance réelles."""
        return [offer for offer in offers if self._is_valid_alternance(offer)]

    def _is_valid_alternance(self, offer: Dict) -> bool:
        """Valide qu'une offre est bien une alternance et non une formation."""
        keywords_formation = ['formation', 'école', 'cursus', 'académie']
        title_lower = offer.get('title', '').lower()
        description_lower = offer.get('description', '').lower()

        # Exclut si contient des mots-clés de formation
        if any(keyword in title_lower for keyword in keywords_formation):
            return False

        # Doit contenir 'alternance', 'apprentissage' ou 'contrat pro'
        alternance_keywords = ['alternance', 'apprentissage', 'contrat de professionnalisation']
        return any(keyword in title_lower or keyword in description_lower
                  for keyword in alternance_keywords)
```

#### 3. Filtrage IA avec Templates
```python
ALTERNANCE_FILTER_PROMPT = """
Tu es un expert en filtrage d'offres d'emploi. Analyse cette offre et détermine si c'est :
1. Une VRAIE offre d'emploi en alternance (apprentissage/professionnalisation)
2. Une formation/école/cursus (à EXCLURE)

Critères d'exclusion :
- Formations proposées par des écoles
- Cursus académiques
- Stages non rémunérés
- Conseils d'orientation

Critères d'inclusion :
- Poste en entreprise avec contrat d'alternance
- Durée 12-24 mois
- Niveau Master 1 compatible
- Domaine cybersécurité/réseaux/télécoms

Offre à analyser :
{offer_data}

Réponds uniquement par : VALIDE ou EXCLUE + raison courte.
"""

class OfferClassifier:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

    def classify_offer(self, offer: Dict) -> Tuple[bool, str]:
        """Classifie une offre avec l'IA."""
        prompt = ALTERNANCE_FILTER_PROMPT.format(offer_data=json.dumps(offer, indent=2))

        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1
            )

            result = response.choices[0].message.content.strip()
            is_valid = result.startswith('VALIDE')
            reason = result.split(' ', 1)[1] if ' ' in result else ""

            return is_valid, reason

        except Exception as e:
            self.logger.error(f"Erreur classification IA : {e}")
            return False, "Erreur IA"
```

#### 4. Générateur Excel
```python
class ExcelReportBuilder:
    """Génère le rapport Excel final."""

    def __init__(self):
        self.workbook = openpyxl.Workbook()
        self.worksheet = self.workbook.active
        self.worksheet.title = "Offres Alternance Cybersécurité"

    def create_report(self, offers: List[Dict], filename: str):
        """Crée le rapport Excel avec mise en forme."""
        # En-têtes
        headers = ["Site", "Titre de l'offre", "Entreprise", "Localisation",
                  "Durée", "Date de début", "Lien direct"]

        for col, header in enumerate(headers, 1):
            cell = self.worksheet.cell(row=1, column=col, value=header)
            cell.font = Font(bold=True)
            cell.fill = PatternFill(start_color="366092", end_color="366092",
                                   fill_type="solid")
            cell.font = Font(color="FFFFFF", bold=True)

        # Données
        for row, offer in enumerate(offers, 2):
            self.worksheet.cell(row=row, column=1, value=offer.get('site', ''))
            self.worksheet.cell(row=row, column=2, value=offer.get('title', ''))
            self.worksheet.cell(row=row, column=3, value=offer.get('company', ''))
            self.worksheet.cell(row=row, column=4, value=offer.get('location', ''))
            self.worksheet.cell(row=row, column=5, value=offer.get('duration', ''))
            self.worksheet.cell(row=row, column=6, value=offer.get('start_date', ''))
            self.worksheet.cell(row=row, column=7, value=offer.get('url', ''))

        # Auto-ajustement des colonnes
        for column in self.worksheet.columns:
            max_length = max(len(str(cell.value or "")) for cell in column)
            self.worksheet.column_dimensions[column[0].column_letter].width = min(max_length + 2, 50)

        self.workbook.save(filename)
```

### Configuration n8n

#### Variables d'Environnement
```bash
# .env
OPENAI_API_KEY=sk-...
SERPAPI_KEY=...
GOOGLE_OAUTH_CLIENT_ID=...
GOOGLE_OAUTH_CLIENT_SECRET=...
SLACK_WEBHOOK_URL=...
PROXY_LIST=proxy1:port,proxy2:port
```

#### Nœuds n8n Spécialisés

1. **Nœud Scraping Sites** :
```json
{
  "type": "n8n-nodes-base.function",
  "name": "Scraper Manager",
  "parameters": {
    "functionCode": `
      const scrapers = ['pole_emploi', 'indeed', 'apec', 'labonnealternance'];
      const results = [];

      for (const scraper of scrapers) {
        try {
          const { execSync } = require('child_process');
          const output = execSync(\`python /app/scrapers/\${scraper}_scraper.py\`);
          const offers = JSON.parse(output.toString());
          results.push(...offers);
        } catch (error) {
          console.log(\`Erreur scraper \${scraper}: \${error.message}\`);
        }
      }

      return results.map(offer => ({ json: offer }));
    `
  }
}
```

2. **Nœud Validation IA** :
```json
{
  "type": "@n8n/n8n-nodes-langchain.lmChatOpenAi",
  "name": "Validation Offres",
  "parameters": {
    "model": "gpt-4",
    "temperature": 0.1,
    "systemPrompt": "{{ $json.filterPrompt }}",
    "userPrompt": "Analyse cette offre: {{ JSON.stringify($json.offer) }}"
  }
}
```

### Gestion des Erreurs et Monitoring

#### Logger Centralisé
```python
import logging
from datetime import datetime

class ScrapingLogger:
    def __init__(self):
        self.logger = logging.getLogger('alternance_scraper')
        handler = logging.FileHandler(f'logs/scraping_{datetime.now().strftime("%Y%m%d")}.log')
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def log_scraping_start(self, site: str):
        self.logger.info(f"Début scraping {site}")

    def log_offers_found(self, site: str, count: int):
        self.logger.info(f"{site}: {count} offres trouvées")

    def log_offers_filtered(self, site: str, before: int, after: int):
        self.logger.info(f"{site}: {before} offres → {after} après filtrage")

    def log_error(self, site: str, error: str):
        self.logger.error(f"Erreur {site}: {error}")
```

#### Notification Slack
```json
{
  "type": "n8n-nodes-base.slack",
  "name": "Notification Rapport",
  "parameters": {
    "operation": "sendMessage",
    "channel": "#alternance-bot",
    "text": "🎯 Nouveau rapport d'offres d'alternance généré !\\n\\n📊 {{ $json.totalOffers }} offres trouvées\\n📄 Rapport Excel disponible\\n🔗 Télécharger: {{ $json.reportUrl }}"
  }
}
```

## 🚀 Déploiement Rapide

### Étapes d'Implémentation (3 jours)

#### Jour 1 : Infrastructure
1. Installation n8n avec Docker
2. Configuration des credentials
3. Développement scrapers de base
4. Tests unitaires scrapers

#### Jour 2 : Intelligence et Filtrage
1. Intégration OpenAI/Claude
2. Développement filtres IA
3. Tests classification offres
4. Workflow n8n principal

#### Jour 3 : Rapport et Monitoring
1. Générateur Excel
2. Système de notification
3. Monitoring et logs
4. Tests end-to-end

### Script de Démarrage Rapide
```bash
#!/bin/bash
# setup_agent.sh

# 1. Installation environnement
docker-compose up -d n8n
pip install -r requirements.txt

# 2. Configuration
cp config/settings.example.py config/settings.py
# Éditer settings.py avec vos API keys

# 3. Import workflow n8n
curl -X POST http://localhost:5678/api/v1/workflows/import \
  -H "Content-Type: application/json" \
  -d @n8n_workflows/recherche_alternance.json

# 4. Test
python scrapers/test_runner.py

echo "✅ Agent alternance configuré !"
echo "🌐 n8n: http://localhost:5678"
echo "📊 Logs: tail -f logs/scraping_$(date +%Y%m%d).log"
```

## 📈 Évolutions Possibles

### Phase 2 : Améliorations
- Interface web de consultation
- Base de données pour historique
- Alertes personnalisées par critères
- API REST pour intégrations tierces

### Phase 3 : Intelligence Avancée
- ML pour prédiction qualité offres
- Analyse sentiment descriptions
- Matching automatique profil/offre
- Recommandations personnalisées

## 💡 Conclusion

La **solution hybride n8n + Python** offre le meilleur équilibre entre rapidité de développement, robustesse et évolutivité. Elle permet de :

- ✅ Développement en 2-3 jours
- ✅ Interface de monitoring visuelle
- ✅ Filtrage IA précis
- ✅ Rapports Excel automatisés
- ✅ Notifications temps réel
- ✅ Facilité de maintenance

Cette approche vous donnera un agent IA opérationnel rapidement, tout en conservant la flexibilité pour des évolutions futures.

<<<END>>>