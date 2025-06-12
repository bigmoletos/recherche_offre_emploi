# Problèmes Résolus - API Mistral N8N

## 🔥 PROBLÈMES PRINCIPAUX ET SOLUTIONS

### 1. Erreur 422 - "Field required: messages"

**CAUSE:** Configuration HTTP Request incorrecte

**SOLUTION:** Utiliser `contentType: "raw"` et `body: "={{ $json.payload_json_string }}"`

### 2. Toutes les offres classées INVALIDE

**CAUSE:** Logique de classification défaillante
```javascript
// MAUVAIS
if (contentUpper.includes('VALIDE') && !contentUpper.includes('INVALIDE'))
```

**SOLUTION:** Patterns précis
```javascript
// BON
const validExact = /CLASSIFICATION:\s*VALIDE/i.test(content);
const invalidExact = /CLASSIFICATION:\s*INVALIDE/i.test(content);
```

### 3. Erreurs de validation incorrectes

**CAUSE:** Logique `isValid` non mise à jour

**SOLUTION:**
```javascript
validation.isValid = validation.errors.length === 0;
```

## 🚀 WORKFLOWS RECOMMANDÉS

1. **`workflow_mistral_422_fix.json`** - Pour déboguer l'erreur 422
2. **`workflow_mistral_production_corrige.json`** - Version corrigée qui fonctionne
3. **`workflow_mistral_avec_gestion_erreurs.json`** - Gestion complète d'erreurs

## ✅ CHECKLIST RAPIDE

- [ ] Content-Type: "raw" dans HTTP Request
- [ ] Payload JSON stringifié correctement
- [ ] Patterns de classification précis
- [ ] validation.isValid correctement mis à jour
- [ ] Headers Authorization et Content-Type
- [ ] onError: "continueErrorOutput"