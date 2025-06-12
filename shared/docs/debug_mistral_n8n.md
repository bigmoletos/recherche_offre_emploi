# 🔧 Guide de Diagnostic - Nœud Mistral dans n8n

## Problèmes Identifiés et Solutions

### ❌ **Problème Principal : Configuration HTTP Request Incorrecte**

**Symptômes :**
- Le workflow ne s'active pas
- Message "Problem running workflow" sans détails
- Nœud Mistral en erreur (rouge)

**Causes Identifiées :**

#### 1. **Authentification Incorrecte**
```json
// ❌ INCORRECT (dans le workflow original)
"authentication": "predefinedCredentialType",
"nodeCredentialType": "mistralCloudApi"

// ✅ CORRECT
"sendHeaders": true,
"headerParameters": {
  "parameters": [
    {
      "name": "Authorization",
      "value": "Bearer {{ $credentials.mistralCloudApi.apiKey }}"
    }
  ]
}
```

#### 2. **Body Format Incorrect**
```json
// ❌ INCORRECT - Structure complexe avec bodyParameters
"bodyParameters": {
  "parameters": [
    {"name": "model", "value": "mistral-large-latest"},
    {"name": "messages", "value": "={{ JSON.stringify(...) }}"}
  ]
}

// ✅ CORRECT - JSON Body direct
"bodyContentType": "json",
"jsonBody": "={\n  \"model\": \"mistral-large-latest\",\n  \"messages\": [...]\n}"
```

#### 3. **Expression Variables Complexes**
```javascript
// ❌ PROBLÈME - Expression trop complexe
"={{ JSON.stringify([{\"role\": \"system\", \"content\": \"Tu es...\" + $json.title + \"...}]) }}"

// ✅ SOLUTION - Expression simplifiée
"content\": \"Analyse: Titre: {{ $json.title }} - Entreprise: {{ $json.company }}\""
```

## 🛠️ **Solution Recommandée**

### **Étape 1 : Importer le Workflow Corrigé**
1. Supprimer l'ancien workflow
2. Importer `workflow_n8n_mistral_corrected.json`
3. Vérifier les credentials

### **Étape 2 : Tester la Configuration**
```bash
# Test manuel via webhook
curl -X POST http://localhost:5678/webhook/test-mistral-workflow
```

### **Étape 3 : Validation Progressive**

#### Test 1 : Credential Mistral
```http
POST https://api.mistral.ai/v1/chat/completions
Authorization: Bearer VOTRE_CLE_API
Content-Type: application/json

{
  "model": "mistral-large-latest",
  "messages": [{"role": "user", "content": "Test"}],
  "max_tokens": 10
}
```

#### Test 2 : Nœud HTTP Request Seul
- Créer un workflow avec juste le nœud Mistral
- Données d'entrée fixes
- Tester l'exécution

## 🔍 **Méthodes de Diagnostic**

### 1. **Vérifier les Logs n8n**
```bash
# Dans le container Docker
docker logs n8n_container

# Ou depuis l'interface n8n
# Executions > Voir les détails de l'exécution échouée
```

### 2. **Test API Mistral Direct**
```python
# Script de test Python
import requests
import os

headers = {
    'Authorization': f'Bearer {os.getenv("MISTRAL_API_KEY")}',
    'Content-Type': 'application/json'
}

data = {
    "model": "mistral-large-latest",
    "messages": [{"role": "user", "content": "Test connexion"}],
    "max_tokens": 10
}

response = requests.post(
    'https://api.mistral.ai/v1/chat/completions',
    headers=headers,
    json=data
)

print(f"Status: {response.status_code}")
print(f"Response: {response.text}")
```

### 3. **Vérifier la Configuration Credential**
Dans n8n :
1. **Settings** > **Credentials**
2. **Mistral Cloud account** > **Test**
3. Vérifier que le test passe ✅

## 🚨 **Erreurs Courantes et Solutions**

### **Erreur 401 - Unauthorized**
```
Cause: Clé API incorrecte ou expirée
Solution: Regénérer la clé sur platform.mistral.ai
```

### **Erreur 400 - Bad Request**
```
Cause: Format JSON incorrect
Solution: Utiliser jsonBody au lieu de bodyParameters
```

### **Erreur de Parsing**
```
Cause: Expression n8n malformée {{ }}
Solution: Simplifier les expressions, éviter les JSON.stringify complexes
```

### **Timeout**
```
Cause: Requête trop longue
Solution: Réduire max_tokens, optimiser le prompt
```

## ✅ **Workflow de Test Simplifié**

Le nouveau workflow `workflow_n8n_mistral_corrected.json` inclut :

- **Données de test** : Offres fictives pour validation
- **HTTP Request simplifié** : Configuration corrigée
- **Gestion d'erreurs** : Fallback en cas d'échec
- **Debug amélioré** : Logs et traces détaillés

## 📋 **Checklist de Validation**

- [ ] Credential Mistral configuré et testé
- [ ] Workflow importé sans erreur
- [ ] Exécution manuelle réussie
- [ ] Réponses IA correctes (VALIDE/INVALIDE)
- [ ] Pas d'erreur dans les logs n8n
- [ ] Test webhook fonctionnel

## 🎯 **Prochaines Étapes**

1. **Tester le workflow corrigé**
2. **Valider la classification IA**
3. **Intégrer les scrapers Python**
4. **Ajouter la génération Excel**
5. **Déployer en production**

---

**💡 Conseil :** Toujours tester avec des données simples avant d'intégrer la logique complexe. Le nouveau workflow utilise cette approche progressive.

**🔧 Support :** En cas de problème persistant, examiner les logs Docker n8n et tester l'API Mistral directement.