# GUIDE D'INTÉGRATION : Sites d'Emploi Français

## 🎯 OBJECTIF
Intégrer le scraping automatique des principales plateformes d'emploi françaises pour l'alternance en cybersécurité.

## 📋 SITES CIBLES ANALYSÉS

### 1. **France Travail** (Officiel)
- **URL** : https://www.francetravail.fr/
- **Type** : Plateforme gouvernementale
- **API** : Oui (API Emploi Store)
- **Spécificités** :
  - Filtres contrat alternance disponibles
  - Données structurées et fiables
  - Accès API gratuit après inscription

### 2. **La Bonne Alternance** (Pôle Emploi)
- **URL** : https://labonnealternance.pole-emploi.fr/
- **Type** : Spécialisé alternance
- **API** : Oui (API publique)
- **Spécificités** :
  - 100% dédié alternance
  - Géolocalisation avancée
  - Intégration avec formations

### 3. **Indeed France**
- **URL** : https://fr.indeed.com/
- **Type** : Agrégateur international
- **API** : Non (scraping HTML)
- **Spécificités** :
  - Volume important d'offres
  - Filtres alternance disponibles
  - Nécessite scraping respectueux

### 4. **APEC**
- **URL** : https://www.apec.fr/
- **Type** : Emploi cadres
- **API** : Non (scraping HTML)
- **Spécificités** :
  - Offres qualifiées pour cadres
  - Stages et alternance niveau Bac+3/5
  - Filtres par type de contrat

### 5. **Walt Community**
- **URL** : https://walt.community/
- **Type** : Communauté alternance
- **API** : Potentielle (à vérifier)
- **Spécificités** :
  - 100% alternance et apprentissage
  - Secteur cybersécurité présent
  - Plateforme moderne

## 🛠️ STRATÉGIES D'INTÉGRATION

### A. Sites avec API (Recommandé)

#### France Travail - API Emploi Store
```javascript
// Configuration API Emploi Store
const apiConfig = {
  baseUrl: 'https://api.emploi-store.fr/partenaire',
  endpoints: {
    search: '/offresdemploi/v2/offres/search',
    detail: '/offresdemploi/v2/offres/{id}'
  },
  auth: {
    clientId: 'VOTRE_CLIENT_ID',
    clientSecret: 'VOTRE_CLIENT_SECRET'
  },
  filters: {
    typeContrat: 'A1', // Apprentissage
    motsCles: 'cybersécurité OR "sécurité informatique"',
    minCreationDate: '2025-06-01T00:00:00Z'
  }
};
```

#### La Bonne Alternance - API
```javascript
// Configuration La Bonne Alternance
const lbaConfig = {
  baseUrl: 'https://labonnealternance.pole-emploi.fr/api',
  endpoints: {
    jobs: '/v1/jobs/search',
    companies: '/v1/companies'
  },
  params: {
    romes: 'M1802,M1810', // Codes ROME cybersécurité
    radius: 100,
    caller: 'n8n-scraper'
  }
};
```

### B. Sites avec Scraping HTML (Alternatif)

#### Indeed France - Scraping Respectueux
```javascript
// Configuration scraping Indeed
const indeedConfig = {
  baseUrl: 'https://fr.indeed.com',
  searchParams: {
    q: 'cybersécurité alternance',
    l: 'France',
    radius: 50,
    sort: 'date',
    fromage: 7 // 7 derniers jours
  },
  selectors: {
    jobCards: '[data-jk]',
    title: 'h2 a span',
    company: '.companyName',
    location: '.companyLocation',
    summary: '.summary'
  },
  rateLimit: {
    requestsPerMinute: 30,
    delayBetweenRequests: 2000
  }
};
```

## 🔧 IMPLÉMENTATION N8N

### Workflow 1 : Configuration Multi-Sites
```json
{
  "node": "Configuration Sites",
  "code": "// Configuration dynamique des sources",
  "outputs": [
    "Sites avec API prioritaires",
    "Sites avec scraping HTML",
    "Sites inactifs/maintenance"
  ]
}
```

### Workflow 2 : Orchestrateur Principal
```json
{
  "nodes": [
    "🔧 Scheduler (Cron)",
    "🌐 Router Sources",
    "📊 Agrégateur Résultats",
    "🤖 Classification Mistral",
    "📧 Notification Résultats"
  ]
}
```

### Workflow 3 : Scraper Spécialisé par Site
```json
{
  "workflows": [
    "scraper_france_travail.json",
    "scraper_bonne_alternance.json",
    "scraper_indeed_france.json",
    "scraper_apec.json",
    "scraper_walt_community.json"
  ]
}
```

## 📊 EXEMPLE DE DONNÉES STRUCTURÉES

```javascript
// Format unifié pour toutes les sources
const offreStandard = {
  // Identifiants
  offer_id: 'source-site-timestamp-hash',
  source_site: 'France Travail',
  source_url: 'https://...',

  // Données offre
  title: 'Contrat d\'apprentissage - Analyste Cybersécurité',
  company: 'ANSSI',
  description: 'Formation alternance...',
  contract_type: 'Contrat d\'apprentissage',
  location: 'Paris (75)',
  salary_range: '1200-1500€/mois',
  duration: '24 mois',
  start_date: '2025-09-01',

  // Métadonnées
  posted_date: '2025-06-05',
  scraped_at: '2025-06-05T14:30:00Z',
  keywords_matched: ['cybersécurité', 'alternance', 'SOC'],

  // Classification préliminaire
  preliminary_analysis: {
    is_alternance: true,
    is_cybersecurity: true,
    confidence: 0.9,
    expected_mistral_result: 'VALIDE'
  }
};
```

## ⚡ PLAN DE DÉPLOIEMENT

### Phase 1 : APIs Officielles (Priorité)
1. **France Travail API** - Inscription et configuration
2. **La Bonne Alternance API** - Test d'accès
3. **Test workflow avec données réelles**

### Phase 2 : Scraping Complémentaire
1. **Indeed France** - Scraper respectueux
2. **APEC** - Scraper sélectif
3. **Optimisation rate limiting**

### Phase 3 : Intégration Complète
1. **Walt Community** - Investigation API
2. **Workflow orchestrateur global**
3. **Monitoring et alertes**

## 🚦 CONSIDÉRATIONS TECHNIQUES

### Rate Limiting & Respect
```javascript
const rateLimits = {
  'France Travail': { requestsPerHour: 1000, burst: 50 },
  'La Bonne Alternance': { requestsPerHour: 500, burst: 25 },
  'Indeed': { requestsPerMinute: 30, burst: 5 },
  'APEC': { requestsPerMinute: 20, burst: 3 },
  'Walt': { requestsPerMinute: 60, burst: 10 }
};
```

### Gestion d'Erreurs
- **Retry automatique** avec backoff exponentiel
- **Fallback sur cache** si API indisponible
- **Alertes monitoring** sur échecs répétés
- **Mode dégradé** avec sources partielles

### Conformité Légale
- **Respect robots.txt** pour chaque site
- **User-Agent identification** approprié
- **Limitation débit** respectueuse
- **Pas de surcharge** des serveurs

## 🎯 RÉSULTATS ATTENDUS

### Métriques de Performance
- **Volume** : 50-200 offres/jour toutes sources
- **Précision** : >90% classification correcte Mistral
- **Couverture** : 5 sources principales actives
- **Fraîcheur** : Données <24h

### Qualité des Données
- **Dédoublonnage** automatique par titre+entreprise
- **Enrichissement** avec géolocalisation
- **Validation** critères alternance+cybersécurité
- **Scoring** confiance par source

---

**Prochaine étape** : Commencer par l'API France Travail (la plus fiable et officielle).

**Contact** : Besoin d'aide pour l'inscription aux APIs ou configuration spécifique ?