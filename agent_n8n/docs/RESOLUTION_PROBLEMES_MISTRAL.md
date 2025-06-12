# Guide de Résolution - Problèmes API Mistral dans N8N

## 🚨 **Problèmes Identifiés et Solutions**

### 1. **Erreur 422 - "Field required: messages"**

#### 🔍 **Cause**
L'erreur 422 indique que le champ `messages` est manquant dans le payload envoyé à l'API Mistral.

#### ✅ **Solutions**

**Solution A : Configuration HTTP Request avec JSON Body brut**
```json
{
  "parameters": {
    "method": "POST",
    "url": "https://api.mistral.ai/v1/chat/completions",
    "sendHeaders": true,
    "headerParameters": {
      "parameters": [
        {
          "name": "Authorization",
          "value": "Bearer YOUR_API_KEY"
        },
        {
          "name": "Content-Type",
          "value": "application/json"
        }
      ]
    },
    "sendBody": true,
    "contentType": "raw",
    "body": "={{ $json.payload_json_string }}",
    "options": {}
  }
}
```

**Solution B : Préparation explicite du payload**
```javascript
// Dans le nœud Code précédent
const payload = {
  "model": "mistral-large-latest",
  "messages": [
    {
      "role": "system",
      "content": "Tu es un expert RH."
    },
    {
      "role": "user",
      "content": "Analyse cette offre..."
    }
  ],
  "temperature": 0.1,
  "max_tokens": 200
};

return {
  json: {
    ...otherData,
    payload_json_string: JSON.stringify(payload)
  }
};
```

### 2. **Classification Incorrecte - Tous les résultats sont INVALIDE**

#### 🔍 **Cause**
La logique de classification est défaillante. Le code original :
```javascript
if (contentUpper.includes('VALIDE') && !contentUpper.includes('INVALIDE')) {
  classification = 'VALIDE';
} else if (contentUpper.includes('INVALIDE')) {
  classification = 'INVALIDE';
}
```

**Problème** : Si Mistral répond "Cette offre n'est pas valide", le code détecte "VALIDE" mais classe incorrectement.

#### ✅ **Solution Corrigée**

```javascript
// Classification avec patterns précis
const validPatterns = [
  /\*\*CLASSIFICATION\*\*:\s*VALIDE/i,
  /CLASSIFICATION:\s*VALIDE/i,
  /RÉPONSE:\s*VALIDE/i
];

const invalidPatterns = [
  /\*\*CLASSIFICATION\*\*:\s*INVALIDE/i,
  /CLASSIFICATION:\s*INVALIDE/i,
  /RÉPONSE:\s*INVALIDE/i
];

const hasValidPattern = validPatterns.some(pattern => pattern.test(content));
const hasInvalidPattern = invalidPatterns.some(pattern => pattern.test(content));

if (hasValidPattern && !hasInvalidPattern) {
  classification = 'VALIDE';
  confidence = 0.95;
} else if (hasInvalidPattern) {
  classification = 'INVALIDE';
  confidence = 0.95;
} else {
  // Fallback plus intelligent
  classification = 'INCERTAIN';
  confidence = 0.3;
}
```

### 3. **Erreur de Validation dans le Workflow de Gestion d'Erreurs**

#### 🔍 **Cause**
Le workflow marque des données valides comme "ERREUR_VALIDATION" à cause d'une logique de validation trop stricte.

#### ✅ **Solution**

**Problème dans le code :**
```javascript
// MAUVAIS : isValid reste true mais passe par la branche erreur
if (validationResult.errors.length > 0) {
  validationResult.isValid = false; // ⚠️ Correctif manquant
}
```

**Correction :**
```javascript
// Validation corrigée
function validateJobOffer(data) {
  const validation = {
    isValid: true,
    errors: [],
    warnings: [],
    correctedData: { ...data }
  };

  // Vérifications
  const requiredFields = ['id', 'title', 'company', 'description'];
  requiredFields.forEach(field => {
    if (!data[field] || data[field].trim() === '') {
      validation.errors.push(`${field} manquant`);
    }
  });

  // IMPORTANT : Mettre à jour isValid
  validation.isValid = validation.errors.length === 0;

  return validation;
}
```

### 4. **Prompt Trop Complexe - Réponses Incohérentes**

#### 🔍 **Cause**
Le prompt est trop long et complexe, causant des réponses variables de Mistral.

#### ✅ **Solution Simplifiée**

**Avant (trop complexe) :**
```javascript
const prompt = `Tu es un expert RH spécialisé en cybersécurité et contrats d'alternance...
[Long prompt avec beaucoup de critères]`;
```

**Après (simplifié) :**
```javascript
const prompt = `ANALYSE CETTE OFFRE D'EMPLOI :

TITRE: ${offre.title}
TYPE: ${offre.contract_type}
DESCRIPTION: ${offre.description}

CRITÈRES DE VALIDATION :
1. CONTRAT = apprentissage OU alternance OU contrat pro
2. DOMAINE = cybersécurité OU sécurité informatique

RÉPONDS UNIQUEMENT PAR :
- CLASSIFICATION: VALIDE (si les 2 critères sont remplis)
- CLASSIFICATION: INVALIDE (sinon)
- JUSTIFICATION: [explique pourquoi]`;
```

## 🔧 **Workflows Recommandés**

### 1. **Pour Débogage : `workflow_mistral_422_fix.json`**
- Teste spécifiquement l'erreur 422
- Validation complète du payload
- Diagnostics détaillés

### 2. **Pour Production : `workflow_mistral_production_corrige.json`**
- Classification corrigée
- Gestion d'erreurs robuste
- Métriques de performance

### 3. **Pour Gestion Complète : `workflow_mistral_avec_gestion_erreurs.json`**
- Validation des données en entrée
- Gestion de tous types d'erreurs
- Récupération automatique

## 📊 **Checklist de Validation**

### ✅ **Avant de Lancer un Workflow**

1. **Validation du Payload API**
   - [ ] Champ `model` présent
   - [ ] Champ `messages` présent et array
   - [ ] Chaque message a `role` et `content`
   - [ ] Headers HTTP corrects

2. **Configuration N8N**
   - [ ] Content-Type: `raw` ou `json`
   - [ ] Headers Authorization et Content-Type
   - [ ] Timeout suffisant (30s minimum)
   - [ ] `onError: "continueErrorOutput"` activé

3. **Logique de Classification**
   - [ ] Patterns de recherche précis
   - [ ] Fallback intelligent
   - [ ] Logging détaillé pour débogage

4. **Gestion d'Erreurs**
   - [ ] Try-catch dans les nœuds Code
   - [ ] Validation des données d'entrée
   - [ ] Nœuds d'erreur connectés

## 🎯 **Tests de Validation**

```javascript
// Script de test pour valider la configuration
const testPayload = {
  "model": "mistral-large-latest",
  "messages": [
    {
      "role": "user",
      "content": "Test simple"
    }
  ],
  "max_tokens": 50
};

// Validation
console.log('✅ Model:', testPayload.model ? 'OK' : 'MANQUANT');
console.log('✅ Messages:', Array.isArray(testPayload.messages) ? 'OK' : 'INVALIDE');
console.log('✅ JSON valide:', JSON.stringify(testPayload) ? 'OK' : 'ERREUR');
```

## 🚀 **Utilisation Recommandée**

1. **Commencez par** `workflow_mistral_422_fix.json` pour tester la connexion API
2. **Passez à** `workflow_mistral_production_corrige.json` pour la classification
3. **Utilisez** `workflow_mistral_avec_gestion_erreurs.json` pour la production avec gestion complète

## 📝 **Debugging Tips**

### Console Logs Utiles
```javascript
console.log('📋 Payload envoyé:', JSON.stringify(payload, null, 2));
console.log('📥 Réponse reçue:', JSON.stringify(response, null, 2));
console.log('🔍 Content analysé:', content.substring(0, 200));
console.log('✅ Patterns trouvés:', { validPattern, invalidPattern });
```

### Variables de Debug
```javascript
const debug = {
  timestamp: new Date().toISOString(),
  payload_size: JSON.stringify(payload).length,
  response_size: content.length,
  patterns_detected: {
    valid: validPatterns.filter(p => p.test(content)).length,
    invalid: invalidPatterns.filter(p => p.test(content)).length
  }
};
```

Ce guide devrait résoudre tous les problèmes principaux rencontrés avec l'API Mistral dans N8N.