import requests
import ipaddress


def check_network():
    # Retrieves the external IP (The IP that other websites actually see me connect from)
    external_ip = requests.get('http://icanhazip.com/').text.strip()

    # The IP range reserved by the "Instituto Politecnico do Porto"
    # For details check:
    # https://apps.db.ripe.net/db-web-ui/lookup?source=RIPE&type=inetnum&key=193.136.56.0%20-%20193.136.63.255
    rede_ipp = '193.136.56.0/21'
    if ipaddress.ip_address(external_ip) not in ipaddress.ip_network(rede_ipp):
        raise Exception(f"Connect to the VPN first!\nYour ip {external_ip} is not in the {rede_ipp} network")
    else:
        print(f"External IP is {external_ip}, which belongs to the range assigned to IPP ({rede_ipp})")