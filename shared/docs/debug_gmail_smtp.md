# 🔧 Debug Gmail SMTP - Erreur TLS

## 🚨 **Votre Erreur :**
```
Couldn't connect with these settings
Client network socket disconnected before secure TLS connection was established
```

## ✅ **Solutions par Ordre d'Efficacité :**

### **1. Configuration Gmail Exacte :**
```
Host: smtp.gmail.com
Port: 587
Security: TLS
Username: votre-email@gmail.com
Password: [mot-de-passe-app-16-caractères]
```

### **2. Checklist Gmail :**
- [ ] **2FA activée** sur votre compte Gmail
- [ ] **Mot de passe d'application** créé (pas votre mot de passe normal)
- [ ] **Port 587** avec TLS (pas 465 avec SSL)
- [ ] **Format email** : user@gmail.com (pas juste "user")

### **3. Alternative Port 465 :**
Si 587 ne fonctionne pas :
```
Host: smtp.gmail.com
Port: 465
Security: SSL
Username: votre-email@gmail.com
Password: [mot-de-passe-app]
```

### **4. Test avec Outlook/Hotmail (Plus Simple) :**
```
Host: smtp-mail.outlook.com
Port: 587
Security: TLS
Username: votre-email@outlook.com
Password: votre-mot-de-passe-outlook
```

### **5. Test avec Yahoo Mail :**
```
Host: smtp.mail.yahoo.com
Port: 587
Security: TLS
Username: votre-email@yahoo.com
Password: mot-de-passe-app-yahoo
```

## 🎯 **Recommandation Immédiate :**

### **Option A : Testez Outlook (Plus Simple)**
1. **Créez** un compte Outlook gratuit
2. **Configurez** dans n8n avec les paramètres ci-dessus
3. **Testez** → Souvent plus simple que Gmail

### **Option B : Utilisez le Workflow Sans Email**
```
Fichier: workflow_n8n_simple_sans_email.json
✅ Fonctionne immédiatement
✅ Pas de configuration SMTP
✅ Résultats dans les logs n8n
```

## 🚀 **Test Gmail - Étapes Exactes :**

### **1. Gmail - Mot de Passe App :**
```bash
1. https://myaccount.google.com
2. Sécurité → Validation 2 étapes → ACTIVEZ
3. Sécurité → Mots de passe applications → Créer
4. Sélectionnez "Autre" → Tapez "n8n"
5. COPIEZ le mot de passe 16 caractères
```

### **2. Credential n8n :**
```
Name: Gmail SMTP
Type: SMTP
Host: smtp.gmail.com
Port: 587
Secure: TLS
Username: votre.email@gmail.com
Password: [collez-mot-de-passe-app-16-caractères]
```

### **3. Test de Connexion :**
```
Dans n8n → Credentials → Test Connection
Si ça échoue → Essayez Port 465 + SSL
```

## 🔄 **Alternatives si Gmail ne Fonctionne Pas :**

### **Option 1 : Outlook (Recommandé)**
- ✅ Plus simple à configurer
- ✅ Pas de mot de passe d'application
- ✅ Configuration directe

### **Option 2 : Service Email Professionnel**
- ✅ Plus fiable
- ✅ Moins de restrictions
- ✅ Configuration stable

### **Option 3 : Workflow Sans Email**
- ✅ Fonctionne immédiatement
- ✅ Résultats dans n8n
- ✅ Copier-coller vers yopmail

## 📊 **Ordre de Test Recommandé :**

1. **Workflow sans email** → Test immédiat
2. **Gmail avec mot de passe app** → Si vous insistez sur Gmail
3. **Outlook SMTP** → Alternative simple
4. **Autre service email** → Si tout échoue

---

**💡 Le workflow sans email fonctionne immédiatement et vous donne les mêmes résultats !**