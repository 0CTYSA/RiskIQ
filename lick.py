import click
import ipaddress
import socket
import requests
import json
import os
from rich.console import Console
from rich.table import Table
from rich import print as rprint

# Manejo de errores mejorado para solicitudes de API


def make_api_request(url, auth, params=None):
    try:
        response = requests.get(url, auth=auth, params=params)
        response.raise_for_status()
        return response.json()
    except requests.ConnectionError:
        return {"error": "Failed to connect to the API. Please check your internet connection or the API endpoint."}
    except requests.Timeout:
        return {"error": "The request to the API timed out. Please try again later."}
    except requests.RequestException as e:
        return {"error": f"An error occurred while making the request: {e}"}
    except ValueError:
        return {"error": "Received an invalid response from the API."}


class PassiveTotalClient:
    BASE_URL = 'https://api.riskiq.net/pt'

    def __init__(self, username, key):
        self.auth = (username, key)

    def _make_request(self, path, params=None):
        url = self.BASE_URL + path
        return make_api_request(url, self.auth, params)

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


# Crea una instancia de Console
console = Console()


def display_intro():
    console.print(
        "\n[bold cyan]Bienvenido al sistema de consulta de dominio/IP en RiskIQ[/bold cyan]")
    console.print("Este programa permite realizar consultas de DNS pasivo, "
                  "consultas de servicios, consultas de historial SSL y consultas WHOIS "
                  "a un dominio o IP específicos.\n")


def display_menu():
    table = Table(title="Escoge una opción:")
    table.add_column("Item", justify="center", style="cyan", no_wrap=True)
    table.add_column("Opción")

    table.add_row("1", "Consultar DNS pasivo")
    table.add_row("2", "Consultar servicios")
    table.add_row("3", "Consultar historial SSL")
    table.add_row("4", "Consultar WHOIS")
    table.add_row("5", "Salir")

    console.print(table)


def display_options():
    table = Table()  # Crea la tabla sin título
    table.add_column("Opción", justify="right", style="cyan", no_wrap=True)
    table.add_column("Descripción")

    table.add_row("1", "Consultar DNS pasivo")
    table.add_row("2", "Consultar servicios")
    table.add_row("3", "Consultar historial SSL")
    table.add_row("4", "Consultar WHOIS")
    table.add_row("5", "Salir")

    console.print(table)


def display_exit_menu():
    table = Table(title="Escoge una opción:")
    table.add_column("Item", justify="center", style="cyan", no_wrap=True)
    table.add_column("Opción")

    table.add_row("1", "Escoger otra opción")
    table.add_row("2", "Salir")

    console.print(table)


def is_valid_option(option):
    return option in ["1", "2", "3", "4", "5"]


def main():
    display_intro()
    while True:
        display_menu()
        invalid_count = 0  # Inicializa el contador de opciones inválidas
        warning_issued = False  # Nuevo: indica si se ha emitido una advertencia
        while True:  # Modificado a un bucle infinito
            choice = input("Ingrese su opción: ")
            if is_valid_option(choice):
                break  # Si la opción es válida, rompe el bucle
            invalid_count += 1  # Incrementa el contador de opciones inválidas
            if invalid_count == 3:
                rprint("[red]Has ingresado una opción inválida 3 veces. "
                       "Las opciones válidas son: 1, 2, 3, 4, 5.[/red]")
                display_options()  # Muestra la tabla de opciones
                warning_issued = True  # Nuevo: establece que se ha emitido una advertencia
            elif warning_issued:  # Nuevo: si se ha emitido una advertencia y el usuario se equivoca nuevamente
                rprint("[red]Has ingresado una opción inválida nuevamente después de la advertencia. "
                       "Finalizando la ejecución.[/red]")
                return  # Finaliza el programa
            rprint("[red]Opción no válida. Por favor, intente de nuevo.[/red]")

        if choice == "5":
            rprint("[red]Saliendo del programa.[/red]")
            break

        query = input("Ingrese un dominio o IP: ")
        while not (Validator.is_valid_ip(query) or Validator.is_valid_domain(query)):
            rprint("[red]Dominio o IP no válidos. Por favor, intente de nuevo.[/red]")
            query = input("Ingrese un dominio o IP: ")

        rprint("[yellow]Procesando su solicitud, por favor espere...[/yellow]")
        result = run_script(query, choice)
        rprint(result)

        while True:
            display_exit_menu()
            exit_choice = input("Ingrese su opción: ")
            if exit_choice == "1":
                break  # Rompe el bucle interno y regresa al bucle principal para escoger otra opción
            elif exit_choice == "2":
                rprint(
                    "[red]Finalizando proceso. Gracias por usar el programa.[/red]")
                return  # Sale de la función main y termina el programa
            else:
                rprint("[red]Opción no válida. Por favor, intente de nuevo.[/red]")


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

 # Obtén la ruta completa a la carpeta 'Results'
    project_path = os.getcwd()  # Obtén la ruta del directorio actual
    # Construye la ruta completa a la carpeta 'Results'
    results_path = os.path.join(project_path, 'Results')

    result_message = (
        "Consulta completada. Revise la carpeta 'Results' en la siguiente ruta para ver los resultados:\n"
        f"[bold cyan]{results_path}[/bold cyan]\n"  # Resalta y colorea la ruta
    )
    return result_message


if __name__ == "__main__":
    main()
