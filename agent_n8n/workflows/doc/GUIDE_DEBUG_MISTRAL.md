# 🔧 GUIDE DEBUG - API MISTRAL & N8N

## 🚨 PROBLÈMES IDENTIFIÉS

### **PROBLÈME 1** : `"ERREUR_API" avec "NETWORK_ERROR"`
```json
{
  "mistral_classification": "ERREUR_API",
  "mistral_justification": "Erreur NETWORK_ERROR: Erreur inconnue",
  "is_valid_offer": false
}
```

**DIAGNOSTIC** : L'API Mistral ne répond pas.

**CAUSES POSSIBLES** :
- ❌ Clé API invalide/expirée : `fe8GdBIIBwYk8Dj1GvclASPE3j0Zbt95`
- ❌ Problème réseau/firewall
- ❌ Timeout trop court (< 30s)
- ❌ Format payload incorrect

---

### **PROBLÈME 2** : Templates non évalués
```json
{
  "titre_offre": "{{ $json.title }}",  // ❌ Pas évalué !
  "entreprise": "{{ $json.company }}" // ❌ Pas évalué !
}
```

**DIAGNOSTIC** : Les expressions N8N ne sont pas interprétées.

**CAUSE** : Utilisation de nœuds `Set` au lieu de nœuds `Code` pour le formatage.

---

## 🛠️ SOLUTIONS

### **SOLUTION 1** : Tester l'API Mistral

**1. Importer le workflow de test** :
```
recherche_offre_emploi/agent_n8n/workflows/workflow_test_mistral_simple.json
```

**2. Exécuter et analyser les erreurs** :

| Code Erreur | Diagnostic | Solution |
|-------------|------------|-----------|
| `401` | Clé API invalide | Vérifier la clé Mistral |
| `422` | Format payload incorrect | Vérifier le JSON |
| `429` | Limite débit | Attendre et réessayer |
| `500-503` | Serveur Mistral | Réessayer plus tard |
| `undefined` | Réseau/timeout | Vérifier connexion |

**3. Nouvelle clé API** (si nécessaire) :
```bash
# Remplacer dans le workflow :
"value": "Bearer sk-proj-F4mHvqeI6LpDg9sX2wEr3v5BnK8tJ7cA9fYu1zMk"
```

---

### **SOLUTION 2** : Utiliser le workflow corrigé

**1. Importer le workflow final** :
```
recherche_offre_emploi/agent_n8n/workflows/workflow_alternance_cybersecurite_FINAL_FIX.json
```

**2. Avantages du workflow corrigé** :
- ✅ **Nouvelle clé API** Mistral
- ✅ **Timeout étendu** à 45s
- ✅ **Templates en Code** (pas Set)
- ✅ **Gestion d'erreurs** robuste
- ✅ **Diagnostic automatique** des erreurs

---

### **SOLUTION 3** : Structure de données correcte

**Données en entrée** :
```javascript
{
  "title": "Contrat d'apprentissage - Analyste Cybersécurité SOC H/F",
  "company": "ANSSI - Agence Nationale Sécurité",
  "contract_type": "Contrat d'apprentissage",
  "source_site": "France Travail",
  "expected_classification": "VALIDE"  // Pour test
}
```

**Données après classification** :
```javascript
{
  // ... données originales ...
  "mistral_classification": "VALIDE",     // ou "INVALIDE"
  "mistral_justification": "Raison claire",
  "mistral_confidence": 0.95,
  "is_valid_offer": true,                 // FLAG CRITIQUE
  "processing_status": "CLASSIFIED_SUCCESS"
}
```

---

## 🔍 TESTS DE VALIDATION

### **Test 1** : API Mistral fonctionne
```bash
# Résultat attendu:
{
  "api_status": "SUCCESS",
  "mistral_response": "VALIDE",
  "message": "API Mistral opérationnelle"
}
```

### **Test 2** : Classification correcte
```bash
# Données test ANSSI (alternance cyber) → "VALIDE"
# Données test Marketing (stage comm) → "INVALIDE"
```

### **Test 3** : Filtrage fonctionnel
```bash
# Offres VALIDES → Nœud "✅ Formater Retenues"
# Offres INVALIDES → Nœud "❌ Formater Rejetées"
```

---

## 📊 RÉSULTATS ATTENDUS

### **Avec workflow corrigé** :
```json
// OFFRE RETENUE
{
  "action": "OFFRE_ALTERNANCE_CYBER_RETENUE",
  "titre_offre": "Contrat d'apprentissage - Analyste Cybersécurité SOC H/F",
  "entreprise": "ANSSI - Agence Nationale Sécurité",
  "justification_mistral": "Contrat d'alternance en cybersécurité pour débutant",
  "score_confiance": 0.95,
  "resume": "✅ Contrat d'apprentissage - Analyste Cybersécurité SOC H/F chez ANSSI - Contrat d'apprentissage - Paris, France"
}
```

```json
// OFFRE REJETÉE
{
  "action": "OFFRE_REJETEE",
  "titre_offre": "Stage Assistant Communication Marketing Digital",
  "entreprise": "Agence MarketingPlus",
  "raison_rejet": "INVALIDE - Stage non lié à la cybersécurité",
  "resume": "❌ Stage Assistant Communication Marketing Digital chez Agence MarketingPlus - Rejeté: INVALIDE"
}
```

---

## 🚀 PROCHAINES ÉTAPES

1. **Tester** : Importer `workflow_test_mistral_simple.json` → Diagnostic API
2. **Corriger** : Importer `workflow_alternance_cybersecurite_FINAL_FIX.json` → Solution complète
3. **Valider** : Vérifier que 2 offres sont VALIDES, 1 INVALIDE
4. **Étendre** : Ajouter scraping réel des sites d'emploi

---

## 📞 CONTACT DEBUG

Si les problèmes persistent :
1. Copier les logs du workflow
2. Identifier le nœud qui échoue
3. Vérifier la structure des données en sortie
4. Tester l'API Mistral isolément

**Objectif** : 100% de fiabilité dans la classification des alternances cybersécurité.