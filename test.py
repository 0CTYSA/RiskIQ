from functools import partial
import ipaddress
import socket
import requests
import json
import os

with open('to.json', 'r') as file:
    credentials = json.load(file)

USERNAME = credentials['USERNAME']
KEY = credentials['KEY']
auth = (USERNAME, KEY)
base_url = 'https://api.riskiq.net/pt'


def passivetotal_get(path, params=None):
    url = base_url + path
    response = requests.get(url, auth=auth, params=params)
    return response.json()


def is_valid_ip(ip):
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False


def is_valid_domain(domain):
    try:
        socket.gethostbyname(domain)
        return True
    except socket.error:
        return False


get_dns_passive = partial(passivetotal_get, '/v2/dns/passive')
get_services = partial(passivetotal_get, '/v2/services')
get_ssl_history = partial(passivetotal_get, '/v2/ssl-certificate/history')
get_whois = partial(passivetotal_get, '/v2/whois')

# Pedir al usuario que introduzca un dominio o IP
query = input("Por favor, introduzca un dominio o IP: ")

# Verificar si la entrada es válida
if not is_valid_ip(query) and not is_valid_domain(query):
    print("La entrada proporcionada no es un dominio ni una IP válida. Terminando el programa.")
    exit()

dns_passive_params = {'query': query}
services_params = {'query': query}
ssl_history_params = {'query': query}
whois_params = {'query': query, 'history': 'true'}

dns_passive_results = get_dns_passive(params=dns_passive_params)
services_results = get_services(
    params=services_params) if is_valid_ip(query) else None
ssl_history_results = get_ssl_history(params=ssl_history_params)
whois_results = get_whois(params=whois_params)

folder_name = query.replace('/', '_') if '/' in query else query
results_folder = os.path.join('Results', folder_name)
os.makedirs(results_folder, exist_ok=True)

with open(os.path.join(results_folder, 'dns_passive_results.json'), 'w', encoding='utf8') as file:
    json.dump(dns_passive_results, file, indent=4, ensure_ascii=False)

if services_results:
    with open(os.path.join(results_folder, 'services_results.json'), 'w', encoding='utf8') as file:
        json.dump(services_results, file, indent=4, ensure_ascii=False)

with open(os.path.join(results_folder, 'ssl_history_results.json'), 'w', encoding='utf8') as file:
    json.dump(ssl_history_results, file, indent=4, ensure_ascii=False)

with open(os.path.join(results_folder, 'whois_results.json'), 'w', encoding='utf8') as file:
    json.dump(whois_results, file, indent=4, ensure_ascii=False)

# Cargar los datos JSON
with open(os.path.join(results_folder, 'dns_passive_results.json'), 'r', encoding='utf8') as file:
    dns_passive_results = json.load(file)

# Crear una lista para almacenar los dominios y las IPs con sus fechas de recolección
results = []

# Iterar sobre los resultados y agregar los dominios y las IPs al conjunto
for result in dns_passive_results.get('results', []):
    if 'resolve' in result and result['resolve'] and 'value' in result and result['value'] and 'collected' in result and result['collected']:
        item = {
            'domain': result['resolve'],
            'ip': result['value'],
            'collected': result['collected']
        }
        results.append(item)

# Ordenar los resultados por fecha de recolección
results.sort(key=lambda x: x['collected'])

# Escribir solo los dominios en un archivo de texto, ordenados por la fecha de recolección
with open(os.path.join(results_folder, 'ordered_domains.txt'), 'w', encoding='utf8') as file:
    for item in results:
        file.write(f"{item['domain']}\n")

print(
    f"Los dominios ordenados se han guardado en el archivo 'ordered_domains.txt' dentro de la carpeta '{folder_name}' en 'RiskPI/Results'.")
