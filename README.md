# Passive Data Collector

El Passive Data Collector es un script de Python que te permite obtener y guardar datos de DNS, WHOIS y certificados SSL para dominios e direcciones IP. Utiliza la biblioteca `passivetotal` para realizar las solicitudes y guarda los resultados en archivos JSON.

## Requisitos

- Python 3.x
- Biblioteca `passivetotal` (puedes instalarla ejecutando `pip install passivetotal`)

## Uso

1. Clona este repositorio o descarga el archivo `passive_data_collector.py` en tu máquina.

2. Ejecuta el script proporcionando una o más consultas de dominio o dirección IP como argumentos:

```bash
python passive_data_collector.py consulta1.com 192.168.0.1 example.com
```

3. El script obtendrá los datos de DNS, WHOIS y SSL para cada consulta válida y los guardará en archivos JSON en un directorio correspondiente a cada consulta. Por ejemplo, si tu consulta es `consulta1.com`, los archivos JSON se guardarán en un directorio llamado `consulta1.com`.

4. Puedes verificar los archivos JSON generados para cada consulta para acceder a los datos obtenidos.

## Configuración

El script utiliza la biblioteca `passivetotal` para realizar las solicitudes de datos. Para utilizarla, debes configurar las credenciales de autenticación en un archivo de configuración. Asegúrate de seguir las instrucciones de configuración proporcionadas por la biblioteca `passivetotal` para autenticarte correctamente.

## Contribuciones

Si deseas contribuir a este proyecto, puedes enviar un pull request. Apreciamos tu interés y aportes.

## Problemas

Si encuentras algún problema o tienes alguna pregunta, siéntete libre de abrir un issue en este repositorio. Intentaremos resolverlo lo antes posible.

## Atribución

Este script utiliza la biblioteca `passivetotal`, que es propiedad de su respectivo autor. Consulta la documentación de la biblioteca para obtener más información sobre su uso y atribución.
