import os
import json
import argparse
import logging
from ipaddress import ip_address, IPv4Address, IPv6Address
from passivetotal.libs.dns import DnsRequest
from passivetotal.libs.whois import WhoisRequest
from passivetotal.libs.ssl import SslRequest

# Configurar el registro
logging.basicConfig(level=logging.INFO)


def is_valid_domain_or_ip(query):
    try:
        # Intentar convertir a una dirección IP
        ip = ip_address(query)

        # Verificar si es una dirección IPv4 o IPv6
        if isinstance(ip, (IPv4Address, IPv6Address)):
            return True
    except ValueError:
        pass

    # Verificar si es un dominio válido
    if query.count('.') >= 1:
        return True

    return False

# Resto del código...


def get_data(query, client_dns, client_whois, client_ssl):
    data = {}

    # Get DNS resolutions
    try:
        dns_resolutions = client_dns.get_passive_dns(query=query)
        data['dns_resolutions'] = dns_resolutions
    except Exception as e:
        logging.error(f"Error getting DNS data for {query}: {e}")

    # Get WHOIS data
    try:
        whois_data = client_whois.get_whois_details(query=query)
        data['whois_data'] = whois_data
    except Exception as e:
        logging.error(f"Error getting WHOIS data for {query}: {e}")

    # Get SSL certificate data
    try:
        ssl_certificates = client_ssl.get_ssl_certificate_details(query=query)
        data['ssl_certificates'] = ssl_certificates
    except Exception as e:
        logging.error(f"Error getting SSL data for {query}: {e}")

    return data


def save_data(query, data):
    # Create a new directory for this query if it doesn't exist
    if not os.path.exists(query):
        os.makedirs(query)

    # Save each type of data to a separate file
    for key, value in data.items():
        with open(f'{query}/{key}.json', 'w') as f:
            json.dump(value, f, indent=4)


def main(queries):
    # Initialize clients
    client_dns = DnsRequest.from_config()
    client_whois = WhoisRequest.from_config()
    client_ssl = SslRequest.from_config()

    # Get and save data for each query
    for query in queries:
        if is_valid_domain_or_ip(query):
            data = get_data(query, client_dns, client_whois, client_ssl)
            save_data(query, data)
        else:
            logging.error(f"Invalid query: {query}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Get and save DNS, WHOIS, and SSL data.')
    parser.add_argument('queries', metavar='Q', type=str, nargs='+',
                        help='one or more domains or IPs to query')
    args = parser.parse_args()
    main(args.queries)
