# lick.py

`lick.py` es un script de Python para hacer consultas a la API de PassiveTotal y almacenar los resultados en archivos JSON (TXT). El script consulta los servicios DNS pasivos, SSL y WHOIS de una dirección IP o dominio ingresado por el usuario.

## Requisitos

Para utilizar este script, necesitarás lo siguiente:

- Python instalado en tu máquina.
- Una cuenta en PassiveTotal.
- Una llave API de PassiveTotal.

Puedes obtener la llave API de PassiveTotal en la configuración de tu cuenta. Una vez que la tengas, añádela al archivo `to.json` junto al correo asociado.

## Funciones y Clases del script

- Clase `PassiveTotalClient`: Clase para interactuar con la API de PassiveTotal.
- Clase `Validator`: Métodos estáticos para validar IPs y dominios.
- Clase `FileManager`: Métodos estáticos para guardar y cargar resultados.
- Clase `ResultProcessor`: Clase para procesar y guardar resultados de DNS pasivos.

## Uso

1. Primero, asegúrate de tener Python y la biblioteca `['click',
'ipaddress',
'json',
'os',
'requests',
'rich',
'socket']` instaladas en tu máquina.
2. Ejecuta el script con el siguiente comando:

```bash
python lick.py
```

3. Cuando se te pida, ingresa la dirección IP o el dominio que deseas consultar. Por ejemplo:

```txt
Por favor, introduzca un dominio o IP: example.com
```

El script realizará las consultas a la API de PassiveTotal y almacenará los resultados en la carpeta `Results`. Se creará una carpeta con el nombre del dominio o IP consultado, y dentro de esta carpeta se guardarán los archivos JSON (TXT) con los resultados.

## Estructura de archivos de salida

Los resultados de las consultas a la API de PassiveTotal se guardan en la siguiente estructura de archivos:

```dir
RiskPI/ (Nota: Actualizar según la estructura real)
└── Results/
    └── [Dominio_o_IP]/
        ├── dns_passive_results.json & ordered_domains.txt
        ├── services_results.json
        ├── ssl_history_results.json
        └── whois_results.json
```

Cada archivo JSON contiene los resultados de una consulta específica a la API de PassiveTotal.

---
