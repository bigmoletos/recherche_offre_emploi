
## debug erreur : Une tentative d’accès à un socket de manière interdite par ses autorisations d’accès a été tentée

```bash
erreur:
PS C:\AJC_projets\projet_qualite_air\services\api_ihm\src> python api_ihm.py
 * Debug mode: on
Une tentative d’accès à un socket de manière interdite par ses autorisations d’accès a été tentée

ou avec un autre message:
"C:\Users\romar\AppData\Local\Programs\Python\Python312\Lib\socketserver.py", line 473, in server_bind
    self.socket.bind(self.server_address)
PermissionError: [WinError 10013] Une tentative d’accès à un socket de manière interdite par ses autorisations d’accès a été tentée
```

### actions correctives sous windows powershell en mode administrateur:

utilisation des ports :

```bash
netstat -ano
```

Redémarrez les services réseau :

```bash
net stop winnat
net start winnat
```


