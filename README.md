# test.py

`test.py` es un script de Python para hacer consultas a la API de PassiveTotal y almacenar los resultados en archivos JSON. El script consulta los servicios DNS pasivos, SSL y WHOIS de una dirección IP o dominio ingresado por el usuario.

## Requisitos

Para utilizar este script, necesitarás lo siguiente:

- Python instalado en tu máquina.
- Una cuenta en PassiveTotal.
- Una llave API de PassiveTotal.

Puedes obtener la llave API de PassiveTotal en la configuración de tu cuenta. Una vez que la tengas, añádela al script en las variables `USERNAME` y `KEY` en la parte superior del script:

```python
USERNAME = "your@email.here"
KEY = "API key from account settings"
```

Reemplaza `"your@email.here"` con tu correo electrónico de PassiveTotal y `"API key from account settings"` con tu llave API.

## Funciones del script

- `passivetotal_get`: Función para hacer consultas GET a la API de PassiveTotal.
- `is_valid_ip`: Función para validar si un texto es una dirección IP válida.
- `is_valid_domain`: Función para validar si un texto es un nombre de dominio válido.

## Uso

Para ejecutar el script, asegúrate de tener Python instalado en tu máquina, luego ejecuta el siguiente comando en tu terminal:

```bash
python test.py
```

Cuando se te pida, ingresa la dirección IP o el dominio que deseas consultar. Por ejemplo:

```
Por favor, introduzca un dominio o IP: example.com
```

El script realizará las consultas a la API de PassiveTotal y almacenará los resultados en la carpeta `Results` dentro del directorio `RiskPI`. Se creará una carpeta con el nombre del dominio o IP consultado, y dentro de esta carpeta se guardarán los archivos JSON con los resultados.

## Estructura de archivos de salida

Los resultados de las consultas a la API de PassiveTotal se guardan en la siguiente estructura de archivos:

```
RiskPI/
└── Results/
    └── [Dominio_o_IP]/
        ├── dns_passive_results.json
        ├── services_results.json (solo para direcciones IP)
        ├── ssl_history_results.json
        └── whois_results.json
```

Cada archivo JSON contiene los resultados de una consulta específica a la API de PassiveTotal.
