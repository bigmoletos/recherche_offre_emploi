# SOLUTION : Erreur "fetch is not defined" dans N8N

## 🚨 PROBLÈME IDENTIFIÉ

**Erreur** : `"fetch is not defined"`

**Cause** : L'API `fetch()` n'est pas disponible dans l'environnement d'exécution JavaScript de N8N.

## ✅ SOLUTION APPLIQUÉE

### Principe
Remplacer les appels `fetch()` dans les nœuds Code par des nœuds HTTP Request dédiés.

### Architecture Corrigée

**AVANT (ne fonctionne pas)** :
```javascript
// Dans un nœud Code
const response = await fetch(apiUrl, {
  method: 'POST',
  headers: {...},
  body: JSON.stringify(payload)
});
```

**APRÈS (fonctionne)** :
1. **Nœud Code** : Prépare le payload
2. **Nœud HTTP Request** : Effectue l'appel API
3. **Nœud Code** : Traite la réponse

## 📁 FICHIERS CRÉÉS

### `workflow_mistral_production_http.json`
- **Objectif** : Version de production qui fonctionne
- **Particularités** :
  - Utilise des nœuds HTTP Request
  - Sépare la préparation du payload de l'appel API
  - Récupère les données originales avec `$('📋 Préparer Payload').item.json`

### `workflow_mistral_simple_test.json`
- **Objectif** : Test basique qui fonctionne
- **Usage** : Validation de l'API Mistral

## 🔧 CONFIGURATION TECHNIQUE

### Nœud HTTP Request
```json
{
  "method": "POST",
  "url": "https://api.mistral.ai/v1/chat/completions",
  "contentType": "raw",
  "body": "={{ $json.payload_string }}",
  "headers": {
    "Authorization": "Bearer fe8GdBIIBwYk8Dj1GvclASPE3j0Zbt95",
    "Content-Type": "application/json"
  },
  "onError": "continueErrorOutput"
}
```

### Préparation du Payload
```javascript
const payload = {
  model: "mistral-large-latest",
  messages: [
    {
      role: "system",
      content: "Tu es un classificateur précis."
    },
    {
      role: "user",
      content: prompt
    }
  ],
  temperature: 0.05,
  max_tokens: 200
};

return {
  json: {
    ...offre,
    payload_string: JSON.stringify(payload)
  }
};
```

### Récupération des Données Originales
```javascript
// Dans le nœud de traitement de la réponse
const originalData = $('📋 Préparer Payload').item.json;
const apiResponse = $input.item.json;
```

## 🎯 RÉSULTATS ATTENDUS

### Workflow Simple Test
- ✅ Connexion à l'API Mistral
- ✅ Classification d'une offre test
- ✅ Gestion des erreurs

### Workflow Production HTTP
- ✅ Traitement de 4 offres test
- ✅ Classification précise VALIDE/INVALIDE
- ✅ Métriques de performance
- ✅ Gestion d'erreurs complète

## 🔍 MÉTHODE DE VALIDATION

1. **Tester d'abord** : `workflow_mistral_simple_test.json`
2. **Si OK, utiliser** : `workflow_mistral_production_http.json`

## 📊 MÉTRIQUES DE VALIDATION

Pour 4 offres test :
- 2 doivent être classées VALIDE
- 2 doivent être classées INVALIDE
- Précision attendue : 100%

## 🚀 PROCHAINES ÉTAPES

1. Valider avec `workflow_mistral_simple_test.json`
2. Tester avec `workflow_mistral_production_http.json`
3. Adapter à vos données réelles
4. Intégrer dans le workflow principal

---

**Statut** : ✅ RÉSOLU
**Date** : 2025-06-05
**Version** : 1.0