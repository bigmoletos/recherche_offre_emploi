# 🔧 Guide d'Activation du Workflow n8n

## ❌ Problème : "Waiting for Trigger"

**Cause :** Le workflow n'est pas activé ou mal configuré.

## ✅ Solution Étape par Étape

### **1. Vérification de l'État du Workflow**

Dans l'interface n8n :

1. **Ouvrez** http://localhost:5678
2. **Connectez-vous** avec vos credentials
3. **Sélectionnez** votre workflow "Agent Alternance Cybersécurité"

### **2. Activation du Workflow**

🎯 **Action Critique :**
- **Localisez** le bouton **"Active"** en haut à droite
- **Cliquez** dessus pour l'activer
- **Vérifiez** qu'il devient **VERT** ✅

```
❌ Inactif = Rouge/Gris
✅ Actif = Vert
```

### **3. Configuration du Déclencheur**

**Option A : Déclencheur Cron (Automatique)**
- ⏰ Se déclenche à 9h du lundi au vendredi
- ❗ Nécessite d'attendre ou de modifier l'heure

**Option B : Déclencheur Webhook (Manuel)**
- 🔗 URL : `http://localhost:5678/webhook/test-mistral-workflow`
- ⚡ Test immédiat possible

### **4. Test Immédiat**

#### **Méthode 1 : Exécution Manuelle**
1. **Cliquez** sur le nœud de déclenchement
2. **Cliquez** sur **"Execute Node"** ou **"Test"**
3. **Observez** l'exécution en temps réel

#### **Méthode 2 : Test du Webhook**
```powershell
# Dans PowerShell
Invoke-WebRequest -Uri "http://localhost:5678/webhook/test-mistral-workflow" -Method POST
```

### **5. Diagnostic des Problèmes**

#### **Workflow Toujours en "Waiting" ?**

**Vérifiez :**
- [ ] Workflow activé (bouton vert)
- [ ] Credential Mistral valide
- [ ] n8n Docker en cours d'exécution
- [ ] Pas d'erreurs dans les logs

#### **Messages d'Erreur Courants :**

```json
// ❌ Webhook non enregistré
{"code":404,"message":"webhook not registered"}
→ Solution: Activez le workflow

// ❌ Erreur Mistral 401
{"message":"Unauthorized"}
→ Solution: Vérifiez la clé API

// ❌ Rate Limit 429
{"message":"Too Many Requests"}
→ Solution: Attendez quelques minutes
```

### **6. Alternative de Test**

Si le webhook ne fonctionne pas immédiatement :

```python
# Script Python de test direct
python test_workflow_direct.py
```

Ce script simule exactement le workflow sans n8n.

## 🎯 **Actions Prioritaires**

1. **ACTIVEZ** le workflow dans n8n (bouton vert)
2. **TESTEZ** avec l'exécution manuelle d'un nœud
3. **VÉRIFIEZ** les logs d'exécution dans n8n
4. **UTILISEZ** le script Python en parallèle pour valider

## 📊 **Indicateurs de Succès**

✅ **Workflow Fonctionnel :**
- Bouton "Active" en vert
- Exécutions visibles dans l'historique
- Pas de message "waiting for trigger"
- Classifications Mistral fonctionnelles

❌ **Problèmes Persistants :**
- Bouton reste rouge/gris
- Aucune exécution dans l'historique
- Erreurs 404/401 dans les logs
- Message "waiting" constant

## 🚀 **Prochaines Étapes**

Une fois le workflow activé et fonctionnel :

1. **Intégrer** les vrais scrapers Python
2. **Configurer** la génération Excel
3. **Programmer** l'exécution quotidienne
4. **Ajouter** les notifications

---

**💡 Astuce :** Le message "waiting for trigger" disparaît dès que le workflow est correctement activé ET qu'un déclencheur a été exécuté au moins une fois.