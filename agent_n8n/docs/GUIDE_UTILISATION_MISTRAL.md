# 🚀 GUIDE D'UTILISATION - CLASSIFICATION MISTRAL DANS N8N DOCKER

## 📁 TYPES DE FICHIERS CRÉÉS

### 1. **Fichiers `.js` (Code JavaScript)**
- `classification_mistral_native_fetch.js`
- **Usage** : Code à **copier-coller** dans un nœud "Code" de N8N
- **Pourquoi** : Contournement des bugs des nœuds HTTP Request en Docker N8N

### 2. **Fichiers `.json` (Workflows N8N)**
- `workflow_mistral_production_complet.json`
- **Usage** : **Importer directement** dans N8N via l'interface
- **Contenu** : Workflow complet avec le code JS intégré

## 🔧 MÉTHODES D'UTILISATION

### ✅ **MÉTHODE 1 : Import du workflow complet (RECOMMANDÉE)**

1. **Télécharger le fichier JSON** :
   ```
   workflow_mistral_production_complet.json
   ```

2. **Dans N8N Docker** :
   - Cliquer sur "+" pour créer un nouveau workflow
   - Cliquer sur les 3 points (...) → "Import from file"
   - Sélectionner le fichier `.json`
   - Le workflow s'importe avec tout le code JS intégré

3. **Tester** :
   - Cliquer sur "Execute Workflow"
   - Vérifier les logs dans la console

### ✅ **MÉTHODE 2 : Créer manuellement avec le code JS**

1. **Créer un nouveau workflow** dans N8N

2. **Ajouter les nœuds** :
   - Start
   - Set (données test)
   - **Code** (crucial)
   - IF (condition)
   - Set (branches true/false)

3. **Dans le nœud "Code"** :
   - Ouvrir `classification_mistral_native_fetch.js`
   - **Copier tout le contenu**
   - **Coller dans le champ "JavaScript Code"**

4. **Connecter les nœuds** et tester

## 🎯 STRUCTURE DU WORKFLOW

```
Start → Données Test → [Code Mistral] → Condition → Traitement
                           ↓
                    Appel API Mistral
                    avec fetch natif
```

## ⚙️ CONFIGURATION REQUISE

### 🔑 **Clé API Mistral**
```javascript
// Dans le code JS, ligne 6-7 :
const config = {
  apiKey: process.env.MISTRAL_API_KEY || 'fe8GdBIIBwYk8Dj1GvclASPE3j0Zbt95',
  // ...
```

**Options** :
1. **Variable d'environnement** : `MISTRAL_API_KEY` dans Docker
2. **Hardcodée** : Remplacer par votre clé dans le code

### 🐳 **Docker N8N Variables**
```bash
# Dans docker-compose.yml ou .env
MISTRAL_API_KEY=fe8GdBIIBwYk8Dj1GvclASPE3j0Zbt95
```

## 🛠️ DÉPANNAGE

### ❌ **Erreur "Cannot find module 'node-fetch'"**
✅ **Solution** : Utiliser `workflow_mistral_production_complet.json` qui utilise fetch natif

### ❌ **Erreur 401 Unauthorized**
✅ **Solution** : Vérifier que la clé API est correcte
```javascript
// Test dans le navigateur :
fetch('https://api.mistral.ai/v1/models', {
  headers: { 'Authorization': 'Bearer VOTRE_CLE' }
})
```

### ❌ **Erreur `{"":""}` avec HTTP Request**
✅ **Solution** : Utiliser **uniquement** le nœud "Code", pas HTTP Request

### ❌ **Pas de logs dans la console**
✅ **Solution** :
- Ouvrir les DevTools (F12)
- Onglet "Console"
- Exécuter le workflow

## 📊 FORMAT DE SORTIE

```json
{
  "title": "Alternant Cybersécurité",
  "company": "TechSec Solutions",
  "description": "...",
  "mistral_response": "VALIDE",
  "classification": "VALIDE",
  "is_valid": true,
  "confidence": 0.9,
  "model_used": "mistral-small-latest",
  "usage": { "total_tokens": 150 },
  "processed_at": "2024-01-15T10:30:00.000Z",
  "method": "native_fetch_production"
}
```

## 🚀 ÉTAPES RAPIDES (5 MINUTES)

1. **Télécharger** : `workflow_mistral_production_complet.json`
2. **N8N** → Nouveau workflow → Import → Fichier JSON
3. **Vérifier** la clé API dans le nœud "Code"
4. **Exécuter** → Voir les résultats

## 🔍 LOGS DE DÉBOGAGE

Le code produit des logs détaillés :
```
🤖 === CLASSIFICATION MISTRAL: Alternant Cybersécurité ===
🏢 Entreprise: TechSec Solutions
📦 Payload Mistral préparé
✅ fetch global disponible
🌐 Appel API Mistral avec fetch natif...
📊 Status HTTP: 200
✅ === MISTRAL SUCCESS ===
📝 Réponse brute: VALIDE
🎯 Classification finale: VALIDE
```

## 📚 FICHIERS DE RÉFÉRENCE

- `workflow_mistral_production_complet.json` → **Import direct**
- `classification_mistral_native_fetch.js` → **Code source**
- `SOLUTION_FINALE_DOCKER.md` → **Documentation complète**

---

**✨ Le fichier JSON est prêt à l'emploi - Import et test en 2 minutes ! ✨**