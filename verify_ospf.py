# Importujemy bibliotekę Genie (część PyATS)
from genie.testbed import load
import sys

# 1. Ładowanie sieci z pliku YAML
testbed = load('testbed.yml')

# Lista urządzeń do sprawdzenia
routers_to_check = ['R1-Core', 'R2-Edge']
failed = False

print("--- STARTING OSPF AUTOMATED VERIFICATION ---")

# 2. Pętla po routerach
for device_name in routers_to_check:
    dev = testbed.devices[device_name]
    
    print(f"\n[*] Connecting to {device_name}...")
    try:
        dev.connect(log_stdout=False) # Łączymy się po SSH (bez spamu w konsoli)
    except Exception as e:
        print(f"[!] Connection failed: {e}")
        failed = True
        continue

    print(f"[*] Parsing 'show ip ospf neighbor' on {device_name}...")
    
    try:
        # MAGIA: PyATS wykonuje komendę i od razu zamienia ją na JSON/Słownik!
        output = dev.parse('show ip ospf neighbor')
        
        # 3. Analiza logiczna (Business Logic)
        # Struktura outputu: output['interfaces']['Gi2']['neighbors']['10.0.0.x']['state']
        
        # Sprawdzamy czy są jacykolwiek sąsiedzi
        if not output:
            print(f"[!] FAIL: No OSPF neighbors found on {device_name}!")
            failed = True
            continue

        # Iterujemy po interfejsach i sąsiadach
        for intf, data in output['interfaces'].items():
            for neighbor_id, neighbor_data in data['neighbors'].items():
                state = neighbor_data['state']
                print(f"    -> Interface {intf}: Neighbor {neighbor_id} is in state {state}")
                
                # Warunek zaliczenia testu
                if 'FULL' in state or '2WAY' in state:    
                    print(f"[+] PASS: OSPF Adjacency is healthy.")
                else:
                    print(f"[!] FAIL: Neighbor is not FULL!")
                    failed = True

    except Exception as e:
        # Jeśli parsowanie się nie uda (np. brak outputu), PyATS rzuci błąd
        print(f"[!] FAIL: Could not parse OSPF or no neighbors active. Error: {e}")
        failed = True
    
    # Rozłączamy się
    dev.disconnect()

print("\n-------------------------------------------")
if failed:
    print("❌ TEST FAILED: Some checks did not pass.")
    sys.exit(1) # Zwracamy kod błędu dla systemu CI/CD
else:
    print("✅ TEST PASSED: Network is compliant.")
    sys.exit(0)
