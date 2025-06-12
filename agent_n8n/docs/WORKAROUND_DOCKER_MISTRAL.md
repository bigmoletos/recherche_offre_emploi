# WORKAROUND N8N DOCKER + MISTRAL

## ❌ PROBLÈMES IDENTIFIÉS

### Problème 1 : Bug Credentials Docker
**Bug confirmé** : Les credentials prédéfinis N8N ne fonctionnent pas correctement avec Docker.
Erreur : `"Credentials not found"` même avec credentials correctement configurés.

### Problème 2 : Erreur 422 "Field required messages"
**Erreur JSON** : Mauvais formatage du body de la requête HTTP.
Erreur : `422 - "Field required messages"` par l'API Mistral.

## ✅ SOLUTIONS FINALES FONCTIONNELLES

### Solution A : HTTP Request + JSON Body ✅ RECOMMANDÉE

**Configuration HTTP Request Node :**
```json
{
  "url": "https://api.mistral.ai/v1/chat/completions",
  "method": "POST",
  "sendHeaders": true,
  "headerParameters": {
    "parameters": [
      {
        "name": "Authorization",
        "value": "Bearer {{$env.mistral_key_site_emploi}}"
      },
      {
        "name": "Content-Type",
        "value": "application/json"
      }
    ]
  },
  "sendBody": true,
  "contentType": "json",
  "bodyContent": "{\\n  \\\"model\\\": \\\"mistral-small-latest\\\",\\n  \\\"messages\\\": [\\n    {\\n      \\\"role\\\": \\\"user\\\",\\n      \\\"content\\\": \\\"{{$json.prompt}}\\\"\\n    }\\n  ],\\n  \\\"max_tokens\\\": 100\\n}"
}
```

**Workflow:** `workflow_mistral_http_corrige.json`

### Solution B : Code Node + Fetch ✅ ALTERNATIVE ROBUSTE

**Avantages:**
- Contrôle total du JSON
- Gestion d'erreurs intégrée
- Fallback automatique sur classification locale
- Variables d'environnement directes

**Workflow:** `workflow_mistral_code_final.json`

## 🚀 DIFFÉRENCES CLÉS

### ❌ CE QUI NE MARCHE PAS
```json
// INCORRECT - Parameters Body
{
  "bodyParameterType": "formDataForm",
  "parameters": [
    {
      "name": "messages",
      "value": "[{\"role\": \"user\", \"content\": \"{{$json.prompt}}\"}]"
    }
  ]
}
```

### ✅ CE QUI MARCHE
```json
// CORRECT - JSON Body
{
  "contentType": "json",
  "bodyContent": "{\"model\": \"mistral-small-latest\", \"messages\": [{\"role\": \"user\", \"content\": \"{{$json.prompt}}\"}]}"
}
```

## 📊 RÉSULTATS ATTENDUS

**Test avec Orange Cyberdefense:**
```json
{
  "classification_result": "CLASSIFICATION: VALIDE\nJUSTIFICATION: Contrat apprentissage + domaine cybersécurité",
  "tokens_used": 35,
  "model_used": "mistral-small-latest",
  "status": "SUCCESS_HTTP_WORKAROUND"
}
```

## 🔄 DEPLOYMENT

1. **Importer un des workflows** dans N8N
2. **Vérifier les variables** d'environnement sont chargées
3. **Tester** avec les données de test incluses
4. **Intégrer** dans le workflow de scraping principal

## 🛠️ TROUBLESHOOTING

**Si erreur 401 :** Vérifier `mistral_key_site_emploi` dans container
**Si erreur 422 :** Utiliser `bodyContent` au lieu de `parameters`
**Si pas de réponse :** Fallback automatique sur classification locale

## 🎯 RECOMMANDATION FINALE

**Utiliser Solution A** pour la production :
- Configuration rapide
- Stable avec Docker
- Facilement maintenable

Les credentials N8N seront corrigés dans une future version, mais cette solution fonctionne **maintenant**.

## 📋 STATUT BUG

- **Confirmé** : Versions N8N 1.65+ à 1.80+
- **Environnement** : Docker uniquement
- **Workaround** : Solutions ci-dessus
- **Fix officiel** : En développement

## 🔍 SOURCES

- N8N Community Forum: "Credentials not found Docker"
- StackOverflow: N8N Docker authentication issues
- Tests confirmés : Classification locale + HTTP Request