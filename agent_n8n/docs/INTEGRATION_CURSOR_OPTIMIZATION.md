# Intégration de cursor_optimization dans agent_n8n

## Objectif

Ce document explique comment intégrer et exploiter le module `cursor_optimization` au sein du projet `agent_n8n` pour bénéficier de ses fonctionnalités d'analyse, d'optimisation et de monitoring de code.

---

## 1. Installation et Dépendance

1. Vérifier que le dossier `cursor_optimization` est bien présent à la racine de `C:/programmation/Projets_python/`.
2. Ajouter la dépendance dans `requirements.txt` :
   ```txt
   cursor_optimization @ file:///C:/programmation/Projets_python/cursor_optimization
   ```
3. Installer les dépendances :
   ```bash
   pip install -r requirements.txt
   ```

---

## 2. Utilisation dans le code Python

### Exemple d'import et d'initialisation

```python
from cursor_optimization import initialize_project

optimizer = initialize_project(
    project_type="python",
    config_path=".cursor-optimization.yaml"  # Optionnel, selon vos besoins
)
```

### Analyse de code

```python
analysis = optimizer.analyze_code(
    file_path="votre_script.py",
    rules=["pep8", "security", "performance"]
)
print(analysis)
```

### Optimisation automatique

```python
optimizer.optimize_project(
    target="performance",
    level="aggressive"
)
```

---

## 3. Bonnes pratiques
- Centraliser la configuration dans un fichier `.cursor-optimization.yaml` si besoin de règles spécifiques.
- Utiliser le logger fourni par `cursor_optimization` pour le suivi des optimisations.
- Consulter le README du module pour des exemples avancés et la structure des plugins.

---

## 4. Références
- Documentation officielle : voir `cursor_optimization/README.md`
- Dépendances : `cursor_optimization/requirements.txt`

---

## 5. Commandes utiles

```bash
# Installer les dépendances (si ce n'est pas déjà fait)
pip install -r requirements.txt

# (Optionnel) Mettre à jour la dépendance locale si le code de cursor_optimization évolue
pip install --upgrade --force-reinstall --no-deps cursor_optimization @ file:///C:/programmation/Projets_python/cursor_optimization
```

---

## 6. Support
Pour toute question ou contribution, se référer au README du module ou contacter le mainteneur du projet.