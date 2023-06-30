from functools import partial
import ipaddress
import requests
import json
import os

username = 'juan.hernandez@appgate.com'
key = '9b2cfc90db4ddb915741c03974241d7e020482330f422da8d92247555f7f93cb'
auth = (username, key)
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


get_dns_passive = partial(passivetotal_get, '/v2/dns/passive')
get_services = partial(passivetotal_get, '/v2/services')
get_ssl_history = partial(passivetotal_get, '/v2/ssl-certificate/history')
get_whois = partial(passivetotal_get, '/v2/whois')

# Cambiar aquí por el dominio o IP deseado
query = '47.74.46.121'

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
results_folder = os.path.join(os.getcwd(), 'RiskPI', 'Results', folder_name)
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


print(
    f"Los resultados se han guardado en la carpeta '{folder_name}' dentro de 'Results'.")
