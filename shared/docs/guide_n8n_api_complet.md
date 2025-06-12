# 🎯 GUIDE COMPLET - n8n + API Scraper

## 🚀 **ARCHITECTURE MISE À JOUR**

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│    n8n Workflow │────│  API Flask       │────│ Scraper Python  │
│   (Orchestration)│    │ (Port 5555)      │    │ (Vraies Offres) │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         │              ┌─────────┴─────────┐            │
         │              │                   │            │
         v              v                   v            v
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  Classification │    │   Pôle Emploi    │    │      APEC       │
│   IA Mistral    │    │   (Vraies URLs)  │    │  (Simulation)   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

---

## 📋 **ÉTAPES D'INSTALLATION**

### **1. Préparation des Composants**

#### ✅ **A. Vérifier que Docker n8n fonctionne**
```bash
# Vérifier que n8n est démarré
docker ps | grep n8n

# Si pas démarré, relancer
docker-compose up -d
```

#### ✅ **B. Démarrer l'API Flask**
```bash
# Dans le terminal PowerShell
cd C:\programmation\Projets_python\plateformes_Freelance
python api_scraper_pour_n8n.py
```

**Vous devez voir :**
```
🚀 Démarrage API Scraper pour n8n
📡 Endpoints disponibles:
   - GET  /health : Vérification santé
   - POST /scrape-offres : Scraping complet
   - POST /scrape-pole-emploi : Pôle Emploi seul
   - GET  /test-offres : Données de test
🌐 Accès: http://localhost:5555
```

#### ✅ **C. Tester l'API**
```bash
# Dans un NOUVEAU terminal
python test_api_n8n.py
```

---

### **2. Configuration n8n**

#### ✅ **A. Accéder à n8n**
- Ouvrir : http://localhost:5678
- Se connecter avec vos credentials

#### ✅ **B. Vérifier le credential Mistral**
1. Aller dans **Settings** → **Credentials**
2. Vérifier que **"Mistral Cloud API"** existe
3. Si pas présent, créer avec :
   - **API Key** : `fe8GdBIIBwYk8Dj1GvclASPE3j0Zbt95`

#### ✅ **C. Importer le workflow**
1. Aller dans **Workflows**
2. Cliquer **Import from File**
3. Sélectionner `workflow_n8n_corrige_final.json`
4. Vérifier que tous les nœuds sont bien configurés

---

### **3. Test du Workflow**

#### ✅ **A. Test Manuel**
1. Dans n8n, ouvrir le workflow importé
2. Cliquer sur **"Execute Workflow"**
3. Surveiller l'exécution nœud par nœud

#### ✅ **B. Vérification des Étapes**
- **Déclencheur** : Doit passer immédiatement
- **Test API Santé** : Doit retourner `"status": "healthy"`
- **Collecte Offres** : Doit récupérer les offres depuis l'API
- **Classification IA** : Doit analyser chaque offre avec Mistral
- **Rapport Final** : Doit afficher un rapport complet

---

## 🔧 **RÉSOLUTION DE PROBLÈMES**

### **❌ Problème : "Connection refused localhost:5555"**
**Solution :**
1. Vérifier que l'API Flask est démarrée
2. Redémarrer l'API : `python api_scraper_pour_n8n.py`

### **❌ Problème : "Mistral API Error 401"**
**Solution :**
1. Vérifier la clé API dans n8n credentials
2. Utiliser : `fe8GdBIIBwYk8Dj1GvclASPE3j0Zbt95`

### **❌ Problème : "No data in SplitOut node"**
**Solution :**
1. Vérifier que l'API retourne `{"offres": [...]}`
2. Tester l'API avec : `python test_api_n8n.py`

---

## 🎯 **UTILISATION QUOTIDIENNE**

### **Mode Automatique (Recommandé)**
1. **Démarrer l'API** : `python api_scraper_pour_n8n.py`
2. **Activer le workflow** dans n8n (bouton vert "Active")
3. Le workflow s'exécutera automatiquement à 9h chaque jour

### **Mode Manuel**
1. Démarrer l'API
2. Dans n8n, cliquer **"Execute Workflow"**
3. Consulter les résultats dans les logs de chaque nœud

---

## 📊 **ANALYSE DES RÉSULTATS**

### **Dans n8n :**
- **Nœud "Formatage Rapport"** : Rapport complet formaté
- **Nœud "Agrégation Finale"** : Données JSON détaillées

### **Structure du Rapport :**
```
🎯 RAPPORT AGENT ALTERNANCE CYBERSÉCURITÉ
📊 STATISTIQUES GLOBALES:
✅ Offres valides: X
❌ Offres invalides: Y
💯 Taux validation: Z%

🏢 TOP ENTREPRISES:
1. Entreprise A - X offres - Score: Y/100

🎯 OFFRES VALIDES DÉTAILLÉES:
1. Titre de l'offre
   🏢 Entreprise
   📍 Localisation
   ⭐ Score: XX/100
   🔗 URL
   💭 IA: Justification
```

---

## 🔄 **ÉVOLUTIONS FUTURES**

### **Phase 1 ✅ : Base Fonctionnelle**
- [x] API Flask opérationnelle
- [x] Workflow n8n stable
- [x] Classification IA Mistral
- [x] Vraies offres Pôle Emploi

### **Phase 2 🚀 : Améliorations**
- [ ] Génération Excel dans n8n
- [ ] Notifications email automatiques
- [ ] Filtrage géographique avancé
- [ ] Intégration Indeed/LinkedIn

### **Phase 3 🎯 : Optimisations**
- [ ] Base de données pour historique
- [ ] Interface web de consultation
- [ ] Alertes temps réel
- [ ] Machine learning pour améliorer le filtrage

---

## ⚙️ **COMMANDES UTILES**

```bash
# Démarrer l'API
python api_scraper_pour_n8n.py

# Tester l'API
python test_api_n8n.py

# Tester le pipeline Python direct (sans n8n)
python pipeline_complet_offres_reelles.py

# Démarrer n8n
docker-compose up -d

# Voir les logs n8n
docker-compose logs -f n8n

# Arrêter tout
docker-compose down
```

---

## 🎉 **FÉLICITATIONS !**

Vous disposez maintenant d'un **agent IA automatique** qui :

1. ✅ **Collecte de vraies offres** depuis Pôle Emploi
2. ✅ **Analyse intelligente** avec Mistral IA
3. ✅ **Orchestration n8n** pour automatisation
4. ✅ **Rapports détaillés** formatés
5. ✅ **Exécution quotidienne** automatique

**🚀 Votre agent travaille pour vous 24h/24 !**