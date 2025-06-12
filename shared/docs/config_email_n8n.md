# 📧 Configuration Email dans n8n

## 🎯 **Options Disponibles**

### **Option 1 : Email Générique (Simple)**
- ✅ **Le plus facile** à configurer
- ✅ Pas besoin de credentials
- ❌ Peut finir dans les spams

### **Option 2 : Gmail SMTP (Recommandé)**
- ✅ Fiable et sécurisé
- ✅ N'arrive pas en spam
- ⚙️ Nécessite configuration Gmail

## 🚀 **Configuration Rapide - Email Générique**

### **1. Dans n8n :**
```
Settings → Credentials → Add Credential
→ Email (SMTP) → Generic
```

### **2. Paramètres Email Générique :**
```
Host: smtp.gmail.com
Port: 587
Secure: TLS
User: votre-email@gmail.com
Password: mot-de-passe-app (voir ci-dessous)
```

## 🔐 **Configuration Gmail App Password**

### **1. Activez l'Authentification 2FA :**
1. Allez sur [myaccount.google.com](https://myaccount.google.com)
2. **Sécurité** → **Validation en 2 étapes** → **Activer**

### **2. Créez un Mot de Passe d'Application :**
1. **Sécurité** → **Validation en 2 étapes**
2. **Mots de passe des applications** → **Sélectionner l'app**
3. Choisissez **"Autre"** → Tapez **"n8n"**
4. **Générer** → Copiez le mot de passe (16 caractères)

### **3. Configuration dans n8n :**
```
Name: Gmail SMTP
Type: Email (SMTP)
Host: smtp.gmail.com
Port: 587
Secure: TLS
User: votre-email@gmail.com
Password: [mot-de-passe-app-16-caractères]
From Email: votre-email@gmail.com
From Name: Agent IA Alternance
```

## ⚡ **Test Immédiat**

### **1. Workflow Recommandé :**
Utilisez : `workflow_n8n_final_avec_email.json`

### **2. Test Manuel :**
1. **Importez** le workflow final
2. **Activez** le workflow
3. **Cliquez** sur "Déclencheur Quotidien" → **Execute Node**
4. **Vérifiez** votre boîte `bigmoletos@yopmail.com`

## 📊 **Format Email Reçu**

### **Sujet :**
```
🎯 3 Offres Alternance Cybersécurité - 15/01/2025
```

### **Contenu :**
```
Bonjour,

📊 RÉSUMÉ EXÉCUTIF
✅ 3 offres validées par IA Mistral
🌐 Sites scrapés: pole_emploi, apec, linkedin
📅 Date génération: 15/01/2025 à 09:00:00
🤖 Moteur IA: Mistral Large

🏆 TOP LOCALISATIONS
Paris: 1 offre(s)
Marseille: 1 offre(s)
Toulouse: 1 offre(s)

📋 DÉTAIL DES OFFRES VALIDÉES

1. **Alternance Cybersécurité - Analyste SOC H/F**
   🏢 SecureTech Solutions
   📍 Paris (75)
   ⏱️ Durée: 24 mois
   🚀 Début: septembre 2025
   🔗 https://example.com/offer1
   ✅ Validation: VALIDE
   📊 Source: pole_emploi

[...autres offres...]

💡 PROCHAINES ÉTAPES
1. Consultez les liens directs pour postuler
2. Préparez votre CV et lettre de motivation
3. Suivez les candidatures dans votre tableau de bord

🔄 AUTOMATISATION
- Prochaine exécution: demain 9h00
- Fréquence: du lundi au vendredi
- Filtrage IA: automatique via Mistral
```

## 🚨 **Dépannage**

### **Problème : Email non reçu**
1. **Vérifiez** les spams de `bigmoletos@yopmail.com`
2. **Testez** avec votre email personnel d'abord
3. **Consultez** les logs n8n pour erreurs

### **Problème : Authentification SMTP**
1. **Vérifiez** le mot de passe d'application
2. **Confirmez** que la 2FA est activée
3. **Testez** avec un autre client email

### **Problème : Rate Limiting**
1. **Ajoutez** un délai entre les emails
2. **Limitez** la fréquence des tests
3. **Utilisez** un compte Gmail dédié

## 🎯 **Recommandation Finale**

### **Pour Commencer :**
1. **Importez** : `workflow_n8n_final_avec_email.json`
2. **Configurez** : Gmail SMTP dans n8n
3. **Testez** : Execution manuelle
4. **Activez** : Mode automatique (9h00 du lundi au vendredi)

### **Résultats Attendus :**
- ✅ Email quotidien avec 3-4 offres validées
- 📊 Statistiques détaillées
- 🔗 Liens directs pour postuler
- 📋 Données formatées style Excel dans l'email

---

**💡 Vous recevrez automatiquement un rapport quotidien formaté avec toutes les offres d'alternance cybersécurité validées par l'IA !**