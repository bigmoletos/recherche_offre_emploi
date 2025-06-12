# Plan de Test Mistral - Diagnostic Systématique

## 🎯 Objectif
Identifier et résoudre l'erreur "Request body is not a valid query" (code 2201) avec l'API Mistral dans n8n.

## 📋 Tests à effectuer (par ordre de priorité)

### Test 1 : BodyParameters Ultra-Simple
**Fichier** : `workflow_test_mistral_statique.json` (MODIFIÉ)
**Description** : bodyParameters au lieu de jsonBody (d'après workflow fonctionnel)
**Points clés** :
- ✅ Utilise `bodyParameters` comme le workflow qui marchait
- ✅ Pas de variables n8n
- ✅ Modèle `mistral-small-latest`
- ✅ Message ultra-simple

**Si ça marche** → Le problème était `jsonBody` vs `bodyParameters`
**Si ça échoue** → Le problème vient du credential ou de l'API

### Test 2 : Body Parameters
**Fichier** : `workflow_test_mistral_body_params.json`
**Description** : Utilisation de bodyParameters au lieu de jsonBody
**Points clés** :
- ✅ Format clé/valeur
- ✅ Même contenu que Test 1

**Si ça marche** → Le problème vient de `jsonBody` vs `bodyParameters`
**Si ça échoue** → Confirme le problème de credential

### Test 3 : Node Code avec Fetch
**Fichier** : `workflow_test_mistral_code.json`
**Description** : Appel direct via JavaScript/fetch
**Points clés** :
- ⚠️ Nécessite de remplacer `VOTRE_CLE_API_ICI` par la vraie clé
- ✅ Bypass complet du system credential n8n
- ✅ Logs détaillés de la requête

**Si ça marche** → Le problème vient du credential type n8n
**Si ça échoue** → Le problème vient de la clé API ou des permissions

## 🔍 Diagnostics possibles

### Scenario A : Test 1 réussit
- ✅ **Solution** : Utiliser JSON statique ou simplifier les expressions
- 🔧 **Action** : Modifier le workflow principal pour éviter les expressions complexes

### Scenario B : Test 2 réussit mais pas Test 1
- ✅ **Solution** : Utiliser bodyParameters dans le workflow principal
- 🔧 **Action** : Convertir le workflow pour utiliser bodyParameters

### Scenario C : Test 3 réussit mais pas Test 1 & 2
- ✅ **Solution** : Problème de credential type dans n8n
- 🔧 **Action** : Utiliser le node Code ou changer le type de credential

### Scenario D : Aucun test ne réussit
- ❌ **Problème** : Clé API invalide ou permissions insuffisantes
- 🔧 **Action** : Vérifier la clé API sur https://console.mistral.ai/

## 📋 Checklist avant test

### Prérequis
- [ ] API scraper démarrée sur port 9555
- [ ] Credential "MistralApi" configuré dans n8n
- [ ] Clé API Mistral valide et active

### Ordre d'exécution
1. [ ] **Test 1** : workflow_test_mistral_statique.json
2. [ ] **Test 2** : workflow_test_mistral_body_params.json
3. [ ] **Test 3** : workflow_test_mistral_code.json (avec vraie clé API)

### Informations à collecter
- Status HTTP retourné
- Message d'erreur exact
- Contenu de la requête envoyée (si visible dans les logs n8n)

## 🎯 Résolution attendue

**Une fois qu'un test fonctionne**, appliquer la même configuration au workflow principal :
- `workflow_api_scraper_final.json`

## 🚨 Note importante

Si **TOUS** les tests échouent avec la même erreur, le problème est :
1. **Clé API Mistral invalide/expirée**
2. **Quota Mistral dépassé**
3. **Problème de connectivité réseau**

Dans ce cas, vérifiez d'abord la clé API sur la console Mistral avant de continuer.

---

**🚀 Commencez par le Test 1 et progressez selon les résultats !**