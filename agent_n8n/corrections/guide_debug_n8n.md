# 🛠️ Guide de Débogage N8N - Problème search_params

## 🔴 Problème Rencontré
```
Problem in node '📦 Extraire Conteneur Offres'
search_params manquant [line 22]
```

## 🔍 Diagnostic avec Version Debug

J'ai ajouté des **logs de debug complets** dans le nœud "📦 Extraire Conteneur Offres". Exécutez le workflow et regardez les logs pour voir ces informations :

### 📋 Logs de Debug à Analyser

1. **Variables N8N disponibles**
```
🔍 Variables N8N disponibles:
$input: [keys]
$input.item: [content]
$input.all(): [length]
```

2. **Index de traitement**
```
📍 Index trouvé: X
OU
⚠️ $input.index non disponible
```

3. **Configurations disponibles**
```
📋 Total configs disponibles: 12
✅ Config trouvée via index: X
OU
⚠️ Fallback: utilisation de la première config
```

4. **Structure de la config**
```
🔍 Config récupérée: {
  "hasConfig": true/false,
  "configKeys": [...],
  "hasSearchParams": true/false
}
```

## 🎯 Solutions Selon le Diagnostic

### Cas 1 : "$input.index non disponible"
**Solution** : N8N ne fournit pas l'index automatiquement
```javascript
// Utilisation d'un compteur global ou d'une autre méthode
let currentItemIndex = 0; // Utilisera toujours la première config
```

### Cas 2 : "Total configs disponibles: 0"
**Problème** : Le nœud Config HelloWork n'a pas généré les configs
**Solution** : Vérifier le nœud "⚙️ Config HelloWork"

### Cas 3 : "hasConfig: true, hasSearchParams: false"
**Problème** : La structure de la config a changé
**Solution** : Examiner la structure réelle dans les logs

## 🚑 Solution d'Urgence Rapide

Si le problème persiste, ajoutez un **nœud Item Lists** après "⚙️ Config HelloWork" :

### Méthode : Nœud Item Lists Split
1. **Ajouter un nœud "Item Lists"** après "⚙️ Config HelloWork"
2. **Configurer** : Operation = "Split Out Items"
3. **Connecter** : Config → Item Lists → Fetch Page

### Avantages
- Traite chaque configuration individuellement
- Plus compatible avec N8N
- Évite les problèmes d'index

## 🔧 Code de Sauvegarde Simple

Si vous voulez une solution temporaire qui fonctionne avec au moins une config :

```javascript
// VERSION FALLBACK SIMPLE
const logger = {
  info: (msg, data = {}) => console.log(`ℹ️ ${msg}`, JSON.stringify(data)),
  error: (msg, error = {}) => console.error(`❌ ${msg}`, JSON.stringify(error))
};

try {
  const httpResponse = $input.item.json;

  // Méthode simple : première config disponible
  let config = $('⚙️ Config HelloWork').item.json;

  // Debug complet
  console.log('Config simple récupérée:', {
    hasConfig: !!config,
    structure: config ? Object.keys(config) : 'null'
  });

  if (!config) {
    const allConfigs = $('⚙️ Config HelloWork').all();
    config = allConfigs[0]?.json;
    console.log('Fallback vers première config:', !!config);
  }

  if (!config || !config.search_params) {
    throw new Error('Configuration introuvable - vérifiez le nœud Config HelloWork');
  }

  // Reste du code identique...
  const html = httpResponse.body.toString();

  const selectors = [
    /<main[^>]*>([\s\S]*?)<\/main>/i,
    /<div[^>]*data-id-storage-target="list"[^>]*>([\s\S]*?)<\/div>/i
  ];

  let offersHtml = null;
  for (const selector of selectors) {
    const match = html.match(selector);
    if (match) {
      offersHtml = match[0];
      break;
    }
  }

  if (!offersHtml) {
    throw new Error('Conteneur des offres non trouvé');
  }

  return [{
    json: {
      offers_html: offersHtml,
      config: config,
      extraction_metadata: {
        status: 'success',
        extracted_at: new Date().toISOString()
      }
    }
  }];

} catch (error) {
  console.error('Erreur:', error.message);
  throw error;
}
```

## 📊 Plan d'Action

### Étape 1 : Exécuter avec Debug
1. **Lancez** le workflow avec la version debug
2. **Examinez** les logs dans la console
3. **Identifiez** quel cas de figure s'applique

### Étape 2 : Solutions par Priorité

1. **🥇 Priorité 1** : Ajouter nœud Item Lists Split
2. **🥈 Priorité 2** : Utiliser le code de sauvegarde simple
3. **🥉 Priorité 3** : Corriger la récupération d'index

### Étape 3 : Validation
- [ ] Le workflow traite au moins 1 configuration
- [ ] search_params est correctement récupéré
- [ ] Les offres sont extraites avec succès

## 🎯 Logs Attendus Après Correction

```
🔍 Variables N8N disponibles:
📋 Total configs disponibles: 12
✅ Config trouvée via index: 0
🔍 Config récupérée: {"hasConfig":true,"hasSearchParams":true}
ℹ️ Configuration récupérée avec succès {"location":"Marseille","keywords":["cybersécurité","alternance"]}
ℹ️ HTML récupéré {"length":50000,"config_index":0}
ℹ️ Conteneur extrait avec succès {"selector":3,"length":15000}
```

## 🚀 Résultat Attendu

Une fois le problème résolu, vous devriez voir :
- ✅ search_params correctement récupéré
- ✅ Progression des 12 configurations (ou au moins 1)
- ✅ Extraction des offres sans erreur