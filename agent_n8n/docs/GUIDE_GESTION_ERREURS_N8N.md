# Guide Complet : Gestion des Erreurs et Conditions dans N8N

## 📋 Table des Matières

1. [Types d'erreurs dans N8N](#types-derreurs)
2. [Techniques de validation des données](#validation-données)
3. [Gestion des erreurs avec les nœuds](#gestion-erreurs-nœuds)
4. [Conditions et branchements](#conditions-branchements)
5. [Patterns de récupération d'erreurs](#patterns-récupération)
6. [Exemples pratiques](#exemples-pratiques)

## 🚨 Types d'erreurs dans N8N {#types-derreurs}

### 1. **Erreurs de données manquantes**
```javascript
// Validation dans un nœud Code
const requiredFields = ['title', 'description', 'company'];
const missingFields = requiredFields.filter(field => !$input.item.json[field]);

if (missingFields.length > 0) {
  throw new Error(`Champs manquants: ${missingFields.join(', ')}`);
}
```

### 2. **Erreurs de format de données**
```javascript
// Validation de type
if (typeof $input.item.json.email !== 'string' || !$input.item.json.email.includes('@')) {
  throw new Error('Email invalide');
}

// Validation de structure
if (!Array.isArray($input.item.json.keywords)) {
  $input.item.json.keywords = [];
}
```

### 3. **Erreurs d'API externes**
- 401 Unauthorized
- 422 Unprocessable Entity
- 429 Rate Limit
- 500+ Server Errors

## ✅ Techniques de validation des données {#validation-données}

### 1. **Validation préalable avec nœud Code**

```javascript
// Fonction de validation complète
function validateJobOffer(data) {
  const validation = {
    isValid: true,
    errors: [],
    warnings: [],
    correctedData: { ...data }
  };

  // Champs obligatoires
  const required = ['id', 'title', 'company', 'description'];
  required.forEach(field => {
    if (!data[field] || data[field].trim() === '') {
      validation.errors.push(`${field} est obligatoire`);
      validation.isValid = false;
    }
  });

  // Corrections automatiques
  if (!data.keywords || !Array.isArray(data.keywords)) {
    validation.correctedData.keywords = [];
    validation.warnings.push('Keywords initialisé');
  }

  // Validation métier
  const validContractTypes = ['CDI', 'CDD', 'Stage', 'Alternance'];
  if (data.contract_type && !validContractTypes.includes(data.contract_type)) {
    validation.warnings.push(`Type de contrat non standard: ${data.contract_type}`);
  }

  return validation;
}

// Utilisation
const result = validateJobOffer($input.item.json);
return { json: { ...result.correctedData, validation: result } };
```

### 2. **Validation avec nœud IF**

```json
{
  "parameters": {
    "conditions": {
      "conditions": [
        {
          "leftValue": "={{ $json.title }}",
          "rightValue": "",
          "operator": {
            "type": "string",
            "operation": "isNotEmpty"
          }
        },
        {
          "leftValue": "={{ $json.description }}",
          "rightValue": "",
          "operator": {
            "type": "string",
            "operation": "isNotEmpty"
          }
        }
      ],
      "combinator": "and"
    }
  }
}
```

## 🔧 Gestion des erreurs avec les nœuds {#gestion-erreurs-nœuds}

### 1. **Configuration "Continue on Fail"**

Dans les paramètres du nœud HTTP Request :
```json
{
  "parameters": {
    // ... autres paramètres
    "options": {
      "timeout": 30000,
      "retry": {
        "enabled": true,
        "maxRetries": 3,
        "retryInterval": 2000
      }
    }
  },
  "onError": "continueErrorOutput"
}
```

### 2. **Gestion avec Error Output**

```javascript
// Nœud de gestion d'erreur connecté au "error output"
const inputData = $input.first().json;
const error = $input.last().error;

const errorReport = {
  error_type: determineErrorType(error),
  timestamp: new Date().toISOString(),
  original_data: inputData,
  error_details: {
    message: error.message,
    httpCode: error.httpCode,
    stack: error.stack
  },
  recovery_strategy: determineRecoveryStrategy(error)
};

function determineErrorType(error) {
  if (error.httpCode === 422) return 'VALIDATION_ERROR';
  if (error.httpCode === 401) return 'AUTH_ERROR';
  if (error.httpCode === 429) return 'RATE_LIMIT';
  if (error.httpCode >= 500) return 'SERVER_ERROR';
  return 'UNKNOWN_ERROR';
}

function determineRecoveryStrategy(error) {
  switch (determineErrorType(error)) {
    case 'VALIDATION_ERROR': return 'RETRY_WITH_CORRECTED_DATA';
    case 'RATE_LIMIT': return 'RETRY_AFTER_DELAY';
    case 'SERVER_ERROR': return 'RETRY_LATER';
    default: return 'MANUAL_INTERVENTION';
  }
}

return { json: { ...inputData, error_report: errorReport } };
```

### 3. **Try-Catch dans les nœuds Code**

```javascript
// Pattern Try-Catch robuste
try {
  // Traitement principal
  const result = processData($input.item.json);

  return {
    json: {
      ...result,
      status: 'SUCCESS',
      processed_at: new Date().toISOString()
    }
  };

} catch (error) {
  console.error('Erreur de traitement:', error.message);

  return {
    json: {
      ...($input.item.json || {}),
      status: 'ERROR',
      error: {
        type: error.name,
        message: error.message,
        timestamp: new Date().toISOString()
      },
      recovery_data: generateRecoveryData(error)
    }
  };
}

function generateRecoveryData(error) {
  // Génère des données de récupération selon le type d'erreur
  return {
    can_retry: !error.message.includes('FATAL'),
    suggested_action: getSuggestedAction(error),
    fallback_available: true
  };
}
```

## 🔀 Conditions et branchements {#conditions-branchements}

### 1. **Nœud IF avec conditions multiples**

```json
{
  "parameters": {
    "conditions": {
      "options": {
        "caseSensitive": false,
        "leftValue": "",
        "typeValidation": "loose"
      },
      "conditions": [
        {
          "leftValue": "={{ $json.validation.isValid }}",
          "rightValue": true,
          "operator": {
            "type": "boolean",
            "operation": "equal"
          }
        },
        {
          "leftValue": "={{ $json.data_quality_score }}",
          "rightValue": 0.8,
          "operator": {
            "type": "number",
            "operation": "gte"
          }
        }
      ],
      "combinator": "and"
    }
  }
}
```

### 2. **Switch Node pour multiple conditions**

```json
{
  "parameters": {
    "dataType": "string",
    "value1": "={{ $json.error_type }}",
    "rules": {
      "rules": [
        {
          "value2": "VALIDATION_ERROR",
          "output": 0
        },
        {
          "value2": "AUTH_ERROR",
          "output": 1
        },
        {
          "value2": "RATE_LIMIT",
          "output": 2
        }
      ]
    },
    "fallbackOutput": 3
  }
}
```

## 🔄 Patterns de récupération d'erreurs {#patterns-récupération}

### 1. **Pattern Retry avec délai**

```javascript
// Nœud de gestion retry
const retryInfo = $input.item.json.retry_info || { attempt: 0, max_attempts: 3 };

if (retryInfo.attempt < retryInfo.max_attempts) {
  // Incrémenter le compteur
  retryInfo.attempt += 1;

  // Calculer le délai (backoff exponentiel)
  const delay = Math.pow(2, retryInfo.attempt) * 1000; // 2s, 4s, 8s

  return {
    json: {
      ...$input.item.json,
      retry_info: retryInfo,
      should_retry: true,
      retry_delay: delay,
      next_attempt_at: new Date(Date.now() + delay).toISOString()
    }
  };
} else {
  return {
    json: {
      ...$input.item.json,
      should_retry: false,
      final_error: 'Max retry attempts reached',
      needs_manual_intervention: true
    }
  };
}
```

### 2. **Pattern Fallback**

```javascript
// Stratégie de fallback pour API
const primaryResult = $input.first()?.json;
const fallbackResult = $input.last()?.json;

if (primaryResult && !primaryResult.error) {
  // Utiliser le résultat principal
  return {
    json: {
      ...primaryResult,
      source: 'PRIMARY_API',
      fallback_used: false
    }
  };
} else if (fallbackResult && !fallbackResult.error) {
  // Utiliser le fallback
  return {
    json: {
      ...fallbackResult,
      source: 'FALLBACK_API',
      fallback_used: true,
      primary_error: primaryResult?.error
    }
  };
} else {
  // Échec total
  return {
    json: {
      error: 'Both primary and fallback failed',
      primary_error: primaryResult?.error,
      fallback_error: fallbackResult?.error,
      requires_manual_review: true
    }
  };
}
```

## 💡 Exemples pratiques {#exemples-pratiques}

### 1. **Validation d'email avec correction**

```javascript
function validateAndCorrectEmail(email) {
  if (!email || typeof email !== 'string') {
    return { valid: false, corrected: null, error: 'Email manquant' };
  }

  // Nettoyage
  let cleaned = email.trim().toLowerCase();

  // Corrections communes
  const corrections = {
    'gmial.com': 'gmail.com',
    'gmai.com': 'gmail.com',
    'yahooo.com': 'yahoo.com',
    'hotmial.com': 'hotmail.com'
  };

  Object.entries(corrections).forEach(([wrong, correct]) => {
    cleaned = cleaned.replace(wrong, correct);
  });

  // Validation finale
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  const isValid = emailRegex.test(cleaned);

  return {
    valid: isValid,
    corrected: isValid ? cleaned : null,
    original: email,
    was_corrected: cleaned !== email.trim().toLowerCase(),
    error: isValid ? null : 'Format email invalide'
  };
}

// Utilisation
const emailValidation = validateAndCorrectEmail($input.item.json.email);
return {
  json: {
    ...$input.item.json,
    email: emailValidation.corrected || $input.item.json.email,
    email_validation: emailValidation
  }
};
```

### 2. **Gestion robuste d'API externe**

```javascript
// Configuration API avec gestion d'erreur complète
const apiConfig = {
  url: 'https://api.mistral.ai/v1/chat/completions',
  method: 'POST',
  headers: {
    'Authorization': 'Bearer YOUR_API_KEY',
    'Content-Type': 'application/json'
  },
  timeout: 30000,
  retry: {
    maxAttempts: 3,
    delays: [1000, 2000, 4000] // ms
  }
};

// Validation du payload avant envoi
function validateApiPayload(payload) {
  const errors = [];

  if (!payload.model) errors.push('Model requis');
  if (!payload.messages || !Array.isArray(payload.messages)) {
    errors.push('Messages requis (array)');
  }
  if (payload.messages && payload.messages.length === 0) {
    errors.push('Au moins un message requis');
  }

  payload.messages?.forEach((msg, index) => {
    if (!msg.role) errors.push(`Message ${index}: role manquant`);
    if (!msg.content) errors.push(`Message ${index}: content manquant`);
  });

  return {
    isValid: errors.length === 0,
    errors,
    sanitizedPayload: sanitizePayload(payload)
  };
}

function sanitizePayload(payload) {
  return {
    model: payload.model || 'mistral-large-latest',
    messages: (payload.messages || []).map(msg => ({
      role: msg.role,
      content: String(msg.content).substring(0, 10000) // Limite de sécurité
    })),
    temperature: Math.max(0, Math.min(2, payload.temperature || 0.7)),
    max_tokens: Math.max(1, Math.min(4000, payload.max_tokens || 1000))
  };
}
```

## 🎯 Bonnes pratiques

### 1. **Logging structuré**
```javascript
const logger = {
  info: (message, data) => console.log(`ℹ️ ${message}`, JSON.stringify(data)),
  warn: (message, data) => console.log(`⚠️ ${message}`, JSON.stringify(data)),
  error: (message, data) => console.log(`❌ ${message}`, JSON.stringify(data))
};

logger.info('Validation données', { id: offre.id, fields: Object.keys(offre) });
```

### 2. **Métriques et monitoring**
```javascript
// Ajout de métriques dans chaque nœud
const metrics = {
  node_name: 'validation_donnees',
  execution_time_ms: Date.now() - startTime,
  items_processed: $input.all().length,
  errors_count: validationErrors.length,
  success_rate: (successCount / totalCount) * 100
};

return {
  json: {
    ...result,
    _metrics: metrics,
    _timestamp: new Date().toISOString()
  }
};
```

### 3. **Documentation des erreurs**
```javascript
const errorCatalog = {
  'VALIDATION_001': {
    message: 'Champ titre manquant',
    severity: 'ERROR',
    recovery: 'Générer titre par défaut',
    documentation: 'https://docs.company.com/errors/VALIDATION_001'
  },
  'API_001': {
    message: 'Erreur 422 API Mistral',
    severity: 'ERROR',
    recovery: 'Vérifier format payload',
    documentation: 'https://docs.mistral.ai/api-reference'
  }
};

function createErrorReport(errorCode, context) {
  const errorDef = errorCatalog[errorCode];
  return {
    error_code: errorCode,
    ...errorDef,
    context,
    timestamp: new Date().toISOString(),
    workflow_execution_id: $executionId
  };
}
```

Ce guide vous donne toutes les techniques nécessaires pour gérer robustement les erreurs et conditions dans vos workflows N8N, en particulier pour l'intégration avec l'API Mistral.