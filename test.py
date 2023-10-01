import click
import ipaddress
import socket
import requests
import json
import os
import colorama
from colorama import Fore, Style


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


# inicializa colorama
colorama.init()


def display_intro():
    print(Fore.CYAN + Style.BRIGHT + "-" * 40)
    print(f"{Fore.GREEN}Bienvenido al sistema de consulta de dominio/IP en RiskIQ")
    print(Fore.WHITE + "Este programa le permite realizar consultas de DNS pasivo,")
    print("consultas de servicios, consultas de historial SSL y consultas ")
    print("WHOIS a un dominio o IP específicos.")
    print(Fore.CYAN + Style.BRIGHT + "-" * 40 + Style.RESET_ALL)


def display_menu():
    print(Fore.CYAN + Style.BRIGHT + "-" * 40)
    print(f"{Fore.GREEN}Seleccione una opción:")
    print(Fore.BLUE + "1. Consultar DNS pasivo")
    print("2. Consultar servicios")
    print("3. Consultar historial SSL")
    print("4. Consultar WHOIS")
    print(Fore.RED + "5. Salir")
    print(Fore.CYAN + Style.BRIGHT + "-" * 40 + Style.RESET_ALL)


def display_exit_menu():
    print(Fore.CYAN + Style.BRIGHT + "-" * 40)
    print(f"{Fore.GREEN}Seleccione una opción:")
    print(Fore.BLUE + "1. Escoger otra opción")
    print(Fore.RED + "2. Salir")
    print(Fore.CYAN + Style.BRIGHT + "-" * 40 + Style.RESET_ALL)


def is_valid_option(option):
    return option in ["1", "2", "3", "4", "5"]


def main():
    display_intro()
    while True:
        display_menu()
        choice = input(Fore.GREEN + Style.BRIGHT +
                       "Ingrese su opción: " + Style.RESET_ALL)
        while not is_valid_option(choice):
            print(
                Fore.RED + "Opción no válida. Por favor, intente de nuevo." + Style.RESET_ALL)
            choice = input(Fore.GREEN + Style.BRIGHT +
                           "Ingrese su opción: " + Style.RESET_ALL)
        if choice == "5":
            print(Fore.RED + "Saliendo del programa." + Style.RESET_ALL)
            break
        query = input(Fore.GREEN + Style.BRIGHT +
                      "Ingrese un dominio o IP: " + Style.RESET_ALL)
        while not (Validator.is_valid_ip(query) or Validator.is_valid_domain(query)):
            print(
                Fore.RED + "Dominio o IP no válidos. Por favor, intente de nuevo." + Style.RESET_ALL)
            query = input(Fore.GREEN + Style.BRIGHT +
                          "Ingrese un dominio o IP: " + Style.RESET_ALL)
        print(Fore.YELLOW +
              "Procesando su solicitud, por favor espere..." + Style.RESET_ALL)
        result = run_script(query, choice)
        print(result)

        while True:
            display_exit_menu()
            exit_choice = input(Fore.GREEN + Style.BRIGHT +
                                "Ingrese su opción: " + Style.RESET_ALL)
            if exit_choice == "1":
                break  # Rompe el bucle interno y regresa al bucle principal para escoger otra opción
            elif exit_choice == "2":
                print(
                    Fore.RED + "Finalizando proceso. Gracias por usar el programa." + Style.RESET_ALL)
                return  # Sale de la función main y termina el programa
            else:
                print(
                    Fore.RED + "Opción no válida. Por favor, intente de nuevo." + Style.RESET_ALL)


@click.group()
def cli():
    pass


def run_script(query, choice):
    with open('to.json', 'r') as file:
        credentials = json.load(file)

    client = PassiveTotalClient(credentials['USERNAME'], credentials['KEY'])
    validator = Validator()
    file_manager = FileManager()

    if not validator.is_valid_ip(query) and not validator.is_valid_domain(query):
        return "La entrada proporcionada no es un dominio ni una IP válida. Terminando el programa."

    params = {'query': query}
    folder_name = query.replace('/', '_') if '/' in query else query
    results_folder = os.path.join('Results', folder_name)

    if choice == "1":
        result = client.get_dns_passive(params=params)
        file_manager.save_results(
            results_folder, 'dns_passive_results.json', result)
        processor = ResultProcessor(results_folder, result)
        processor.process_and_save_results()
    elif choice == "2":
        result = client.get_services(params=params)
        file_manager.save_results(
            results_folder, 'services_results.json', result)
    elif choice == "3":
        result = client.get_ssl_history(params=params)
        file_manager.save_results(
            results_folder, 'ssl_history_results.json', result)
    elif choice == "4":
        result = client.get_whois(params=params)
        file_manager.save_results(results_folder, 'whois_results.json', result)
    elif choice == "5":
        return "Saliendo del programa."

    return "Consulta completada. Revise la carpeta 'Results' para ver los resultados."


if __name__ == "__main__":
    main()
