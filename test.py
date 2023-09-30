import click
import ipaddress
import socket
import requests
import json
import os
import customtkinter as ctk
from customtkinter import *


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

    if choice == "Consultar DNS pasivo":
        result = client.get_dns_passive(params=params)
        file_manager.save_results(
            results_folder, 'dns_passive_results.json', result)
        processor = ResultProcessor(results_folder, result)
        processor.process_and_save_results()
    elif choice == "Consultar servicios":
        result = client.get_services(params=params)
        file_manager.save_results(
            results_folder, 'services_results.json', result)
    elif choice == "Consultar historial SSL":
        result = client.get_ssl_history(params=params)
        file_manager.save_results(
            results_folder, 'ssl_history_results.json', result)
    elif choice == "Consultar WHOIS":
        result = client.get_whois(params=params)
        file_manager.save_results(results_folder, 'whois_results.json', result)
    elif choice == "Salir":
        return "Saliendo del programa."

    return "Consulta completada. Revise la carpeta 'Results' para ver los resultados."


class PlaceholderEntry(ctk.CTkEntry):
    def __init__(self, master, placeholder, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.placeholder = placeholder
        self.insert(0, self.placeholder)
        self.bind("<FocusIn>", self._clear_placeholder)
        self.bind("<FocusOut>", self._add_placeholder)

    def _clear_placeholder(self, e):
        if self.get() == self.placeholder:
            self.delete(0, ctk.END)

    def _add_placeholder(self, e):
        if not self.get():
            self.insert(0, self.placeholder)


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Consulta de dominio/IP")
        self.root.geometry("500x500")
        self.root.resizable(False, False)

        self.query_entry = PlaceholderEntry(
            root, placeholder="Introduce un dominio o IP")
        self.query_entry.pack(pady=10)

        self.options = ["Consultar DNS pasivo", "Consultar servicios",
                        "Consultar historial SSL", "Consultar WHOIS", "Salir"]
        # Usa CTkComboBox en lugar de CTkOptionMenu
        self.option_menu = CTkComboBox(root, values=self.options)
        self.option_menu.pack(pady=10)

        self.run_button = CTkButton(root, text="Ejecutar", command=self.run)
        self.run_button.pack()

        self.result_text = ctk.CTkTextbox(
            root, width=80, height=20)  # Corregido a CTkTextbox
        self.result_text.pack(pady=10)

    def run(self):
        query = self.query_entry.get()
        choice = self.option_menu.get()
        # Asegúrate de que run_script pueda manejar el argumento choice
        result = run_script(query, choice)
        self.result_text.delete(1.0, ctk.END)
        self.result_text.insert(ctk.END, result)


def main():
    root = ctk.CTk()  # Usa ctk.CTk como antes
    app = App(root)
    root.mainloop()


if __name__ == "__main__":
    use_gui = True
    if use_gui:
        main()
    else:
        cli()
