# 📊 Guide d'Utilisation : Logs & Excel

## 🔍 **1. Comment Lire les Logs dans n8n**

### **📍 Navigation vers les Logs :**
```bash
1. Ouvrez n8n → http://localhost:5678
2. Cliquez sur l'onglet "Executions" (en haut à droite)
3. Sélectionnez l'exécution la plus récente
4. Cliquez sur n'importe quel nœud coloré (vert = succès)
5. Dans le panneau de droite → Onglet "Logs"
```

### **📋 Contenu des Logs :**
- ✅ **Rapport complet** avec toutes les offres trouvées
- 📊 **Statistiques détaillées** (total, validées, rejetées)
- 🌐 **Sites scrapés** (Pôle Emploi, LinkedIn, Indeed, etc.)
- 🏆 **Répartition géographique** des offres
- ⏱️ **Timestamp** de traitement

## 📄 **2. Générer un Fichier Excel**

### **🚀 Importer le Workflow Excel :**
```bash
1. Dans n8n, cliquez "Import from file"
2. Sélectionnez : workflow_n8n_avec_excel.json
3. Cliquez "Import"
4. Activez le workflow (bouton toggle vert)
```

### **💾 Télécharger le Fichier Excel :**
```bash
1. Attendez l'exécution automatique (15 minutes)
   OU cliquez "Test workflow" pour exécution immédiate

2. Une fois terminé :
   - Allez dans "Executions"
   - Cliquez sur l'exécution récente
   - Cliquez sur le nœud "Excel Prêt"
   - Onglet "Output" dans le panneau de droite
   - Cliquez "Download binary file"

3. Le fichier sera téléchargé automatiquement !
```

## 📊 **3. Contenu du Fichier Excel**

### **📑 Onglet 1 : "Offres_Alternance"**
| Colonne | Description |
|---------|-------------|
| N° | Numéro séquentiel |
| Titre | Titre du poste |
| Entreprise | Nom de l'entreprise |
| Localisation | Ville + département |
| Durée | Durée de l'alternance |
| Date de début | Date prévue de début |
| Site source | Site web d'origine |
| Lien direct | URL pour postuler |
| Validation IA | Analyse Mistral |
| Statut | ✅ VALIDÉE / ❌ REJETÉE |
| Date traitement | Date d'analyse |
| Description | Résumé du poste |

### **📊 Onglet 2 : "Statistiques"**
- Total offres validées
- Nombre de sites scrapés
- Moteur IA utilisé (Mistral Large)
- Date et heure de génération

### **🏆 Onglet 3 : "Localisations"**
- Répartition par ville
- Nombre d'offres par localisation
- Pourcentages calculés

## 🔧 **4. Personnalisation**

### **⏱️ Modifier la Fréquence :**
```bash
1. Cliquez sur le nœud "Déclencheur Test"
2. Modifiez "cronExpression" :
   - "*/15 * * * *" = Toutes les 15 minutes
   - "0 */2 * * *" = Toutes les 2 heures
   - "0 9 * * *" = Tous les jours à 9h
```

### **📧 Ajouter Email Automatique :**
```bash
1. Ajoutez un nœud "Send Email" après "Excel Prêt"
2. Configurez votre SMTP
3. Attachez le fichier Excel binaire
4. Envoyez à bigmoletos@yopmail.com
```

### **🔍 Modifier les Critères de Filtrage :**
```bash
1. Nœud "Données Enrichies" → Modifier les offres test
2. Nœud "Filtrer Validées" → Ajuster les conditions
3. Ajouter d'autres filtres (salaire, durée, etc.)
```

## 🚨 **5. Dépannage**

### **❌ Excel Non Généré :**
```bash
- Vérifiez que tous les nœuds sont verts
- Regardez les logs pour identifier l'erreur
- Le nœud "Créer Excel" doit avoir un output binaire
```

### **📋 Logs Vides :**
```bash
- Vérifiez l'onglet "Logs" du bon nœud
- Certains nœuds n'affichent que dans "Output"
- Essayez l'exécution manuelle "Test workflow"
```

### **🔄 Workflow Ne Se Lance Pas :**
```bash
- Vérifiez que le workflow est activé (toggle vert)
- Mode cron : attendez la prochaine exécution
- Mode manuel : utilisez "Test workflow"
```

## 💡 **6. Conseils d'Optimisation**

### **🚀 Performance :**
- Utilisez des intervalles raisonnables (pas moins de 15 min)
- Limitez le nombre d'offres test pour éviter le rate limiting
- Surveillez les logs Mistral pour éviter les quotas

### **📊 Qualité des Données :**
- Vérifiez régulièrement la précision de l'IA
- Ajustez les prompts si nécessaire
- Testez avec de vraies données progressivement

### **💾 Sauvegarde :**
- Exportez régulièrement les workflows
- Sauvegardez les fichiers Excel générés
- Gardez une trace des configurations qui fonctionnent

## 🎯 **Résultat Final**

Vous obtenez un fichier Excel professionnel avec :
- ✅ **4 offres d'alternance validées** en cybersécurité
- 📊 **Statistiques complètes** de l'analyse
- 🏆 **Répartition géographique** des opportunités
- 🔗 **Liens directs** pour postuler
- 📅 **Horodatage complet** du traitement

**Nom du fichier :** `alternance_cybersecurite_YYYYMMDDTHHMMSS.xlsx`

---
*Guide créé pour l'agent alternance automatisé - Version Excel optimisée*