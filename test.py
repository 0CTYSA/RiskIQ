import click
import ipaddress
import socket
import requests
import json
import os


class PassiveTotalClient:
    BASE_URL = 'https://api.riskiq.net/pt'

    def __init__(self, username, key):
        self.auth = (username, key)

    def _make_request(self, path, params=None):
        url = self.BASE_URL + path
        response = requests.get(url, auth=self.auth, params=params)
        return response.json()

    def get_dns_passive(self, params=None):
        return self._make_request('/v2/dns/passive', params)

    def get_services(self, params=None):
        return self._make_request('/v2/services', params)

    def get_ssl_history(self, params=None):
        return self._make_request('/v2/ssl-certificate/history', params)

    def get_whois(self, params=None):
        return self._make_request('/v2/whois', params)


class Validator:
    @staticmethod
    def is_valid_ip(ip):
        try:
            ipaddress.ip_address(ip)
            return True
        except ValueError:
            return False

    @staticmethod
    def is_valid_domain(domain):
        try:
            socket.gethostbyname(domain)
            return True
        except socket.error:
            return False


class FileManager:
    @staticmethod
    def save_results(folder, filename, data):
        os.makedirs(folder, exist_ok=True)
        with open(os.path.join(folder, filename), 'w', encoding='utf8') as file:
            json.dump(data, file, indent=4, ensure_ascii=False)

    @staticmethod
    def load_results(folder, filename):
        with open(os.path.join(folder, filename), 'r', encoding='utf8') as file:
            return json.load(file)


class ResultProcessor:
    def __init__(self, results_folder, dns_passive_results):
        self.results_folder = results_folder
        self.dns_passive_results = dns_passive_results

    def process_and_save_results(self):
        results = self.process_results()
        self.save_ordered_domains(results)

    def process_results(self):
        results = []
        for result in self.dns_passive_results.get('results', []):
            if 'resolve' in result and result['resolve'] and 'value' in result and result['value'] and 'collected' in result and result['collected']:
                item = {
                    'domain': result['resolve'],
                    'ip': result['value'],
                    'collected': result['collected']
                }
                results.append(item)
        results.sort(key=lambda x: x['collected'])
        return results

    def save_ordered_domains(self, results):
        with open(os.path.join(self.results_folder, 'ordered_domains.txt'), 'w', encoding='utf8') as file:
            for item in results:
                file.write(f"{item['domain']}\n")


def display_menu():
    print("Seleccione una opción:")
    print("1. Consultar DNS pasivo")
    print("2. Consultar servicios")
    print("3. Consultar historial SSL")
    print("4. Consultar WHOIS")
    print("5. Salir")


@click.group()
def cli():
    pass


@cli.command(help="Ejecuta las consultas basadas en el dominio o IP proporcionado.")
@click.option(
    '--query',
    prompt='Por favor, introduzca un dominio o IP',
    help='El dominio o IP a consultar. Debe ser una dirección IP válida o un nombre de dominio resoluble.'
)
def run(query):
    with open('to.json', 'r') as file:
        credentials = json.load(file)

    client = PassiveTotalClient(credentials['USERNAME'], credentials['KEY'])
    validator = Validator()
    file_manager = FileManager()

    if not validator.is_valid_ip(query) and not validator.is_valid_domain(query):
        click.echo(
            "La entrada proporcionada no es un dominio ni una IP válida. Terminando el programa.")
        return

    params = {'query': query}
    folder_name = query.replace('/', '_') if '/' in query else query
    results_folder = os.path.join('Results', folder_name)

    while True:
        display_menu()
        choice = input("Ingrese el número de la opción que desea: ")

        if choice == '1':
            result = client.get_dns_passive(params=params)
            file_manager.save_results(
                results_folder, 'dns_passive_results.json', result)
            # Crear el procesador de resultados
            processor = ResultProcessor(results_folder, result)
            # Procesar y guardar los resultados ordenados
            processor.process_and_save_results()
        elif choice == '2':
            result = client.get_services(params=params)
            file_manager.save_results(
                results_folder, 'services_results.json', result)
        elif choice == '3':
            result = client.get_ssl_history(params=params)
            file_manager.save_results(
                results_folder, 'ssl_history_results.json', result)
        elif choice == '4':
            result = client.get_whois(params=params)
            file_manager.save_results(
                results_folder, 'whois_results.json', result)
        elif choice == '5':
            break  # Salir del bucle
        else:
            print("Opción no válida. Por favor, intente de nuevo.")


if __name__ == '__main__':
    cli()
