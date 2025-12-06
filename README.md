````markdown
# 🚀 Network CI/CD Pipeline with Ansible & PyATS

![Ansible][<img width="1897" height="973" alt="Image" src="https://github.com/user-attachments/assets/3d1fb89b-77e6-40df-9bda-5373ea552a51" />](https://private-user-images.githubusercontent.com/247868388/523390111-3d1fb89b-77e6-40df-9bda-5373ea552a51.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NjUwNjQ1NjUsIm5iZiI6MTc2NTA2NDI2NSwicGF0aCI6Ii8yNDc4NjgzODgvNTIzMzkwMTExLTNkMWZiODliLTc3ZTYtNDBkZi05YmRhLTUzNzNlYTU1MmE1MS5wbmc_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1BS0lBVkNPRFlMU0E1M1BRSzRaQSUyRjIwMjUxMjA2JTJGdXMtZWFzdC0xJTJGczMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDI1MTIwNlQyMzM3NDVaJlgtQW16LUV4cGlyZXM9MzAwJlgtQW16LVNpZ25hdHVyZT03OTEwZmJmYzM5MDhmNDljOGIyMGRmZDIxNjg1MTRlM2I2NDllMjRiZDBjMjQyNjFhNzZlMzYzNmUxMjE3MDNhJlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCJ9.Dx5-uPoVMKaYdDaptIzfIlx_m-BsdTXO7_tjg2Jf-h4) ![Cisco PyATS]<img width="1887" height="942" alt="Image" src="https://github.com/user-attachments/assets/b7baf46e-99f0-4ccf-bfbc-a44e61480649" />

## 📌 Executive Summary
This project demonstrates a fully automated **Continuous Integration / Continuous Deployment (CI/CD)** pipeline for Network Infrastructure.

Instead of manual CLI configurations, the network state is defined as code (**IaC**) using YAML variables. The pipeline ensures that any configuration change is automatically deployed and, crucially, **verified against business logic** before being accepted.

### Network Topology
![Network Topology]<img width="662" height="357" alt="Image" src="https://github.com/user-attachments/assets/2ebe59b1-5fa6-4cef-bbce-92564d21d01b" />

## ⚙️ Architecture & Workflow

The pipeline consists of two major stages orchestrated by a Master Bash script (`run_pipeline.sh`):

1.  **Deploy Stage (Ansible):**
    * Reads host variables (`host_vars/`) defining the desired state (IPs, OSPF Areas).
    * Configures Cisco IOS-XE routers using the `cisco.ios` collection.
    * Ensures idempotency (only changes what is necessary).

2.  **Test Stage (Cisco PyATS/Genie):**
    * Connects to the network post-deployment.
    * Parses operational data (`show ip ospf neighbor`) into structured Python objects.
    * **Quality Gate:** Validates if OSPF neighbors are in `FULL` state. If not, the pipeline fails and alerts the operator.

## 🛠️ Technology Stack
* **Controller:** Ubuntu Linux (Control Node)
* **Automation:** Ansible Core
* **Testing:** Python 3 + Cisco PyATS (Genie)
* **Devices:** Cisco CSR1000v (IOS-XE) within Cisco Modeling Labs (CML)

## 🧪 Pipeline Demonstration

### Scenario 1: Happy Path (Success) ✅
In this scenario, the configuration in `host_vars` is correct. Ansible deploys the changes, and PyATS confirms that OSPF adjacency has reached the `FULL` state.

**Pipeline Output:**
```text
=== STEP 1: DEPLOY CONFIGURATION (ANSIBLE) ===
PLAY [Configure Production Network (OSPF)] *************************************
TASK [Configure Interfaces] ****************************************************
changed: [R1-Core]
changed: [R2-Edge]
...
>>> Deployment Successful! Proceeding to Testing phase...

=== STEP 2: VERIFY NETWORK STATE (PYATS) ===
[*] Connecting to R1-Core...
[*] Parsing 'show ip ospf neighbor' on R1-Core...
    -> Interface GigabitEthernet2: Neighbor 192.168.1.115 is in state FULL/DR
[+] PASS: OSPF Adjacency is healthy.

✅ CI/CD PIPELINE FINISHED SUCCESSFULLY! The network is healthy.
````

> **Analysis:**
>
>   * **Deployment:** Ansible successfully pushed the configuration without errors.
>   * **Verification:** PyATS parsed the routing table and confirmed that OSPF neighbors are established.
>   * **Result:** The pipeline exits with **Code 0**, signaling a successful deployment.

**Screenshot:**

-----

### Scenario 2: Failure Detection (Quality Gate) ❌

Here, an intentional error was introduced (IP Address mismatch in `host_vars/R1-Core.yml`). Ansible deployed the configuration successfully (as it was syntactically correct), but **PyATS detected the logical error**.

**Pipeline Output:**

```text
=== STEP 1: DEPLOY CONFIGURATION (ANSIBLE) ===
...
>>> Deployment Successful! Proceeding to Testing phase...

=== STEP 2: VERIFY NETWORK STATE (PYATS) ===
[*] Connecting to R1-Core...
[*] Parsing 'show ip ospf neighbor' on R1-Core...
[!] FAIL: No OSPF neighbors found on R1-Core!

❌ PIPELINE FAILED! Tests did not pass. Check logs.
```

> **Analysis:**
>
>   * **The Trap:** Even though Ansible finished successfully, the network was broken (OSPF down due to mismatch).
>   * **The Catch:** The PyATS script detected the missing neighbor relationship.
>   * **Result:** The pipeline failed with **Exit Code 1**, preventing the bad configuration from being marked as "Success".

**Screenshot:**

## 📂 Repository Structure

```text
.
├── host_vars/              # Device-specific variables (Source of Truth)
│   ├── R1-Core.yml
│   └── R2-Edge.yml
├── playbooks/              # Ansible Playbooks
│   ├── deploy_ospf.yml     # Main configuration logic
│   └── check_ospf.yml      # Ad-hoc verification
├── images/                 # Evidence & Diagrams
│   ├── topology_diagram.png.png
│   ├── image_a4d67a.png
│   └── image_1ab12d.png
├── inventory               # Inventory file (IPs and credentials)
├── ansible.cfg             # Ansible configuration
├── testbed.yml             # PyATS network definition
├── verify_ospf.py          # Python testing script (The Logic)
└── run_pipeline.sh         # Master CI/CD Orchestrator
```

## 🚀 How to Run

1.  **Clone the repository:**

    ```bash
    git clone [https://github.com/YourUsername/Network-CICD-Pipeline-Demo.git](https://github.com/YourUsername/Network-CICD-Pipeline-Demo.git)
    cd Network-CICD-Pipeline-Demo
    ```

2.  **Install dependencies:**

    ```bash
    pip3 install -r requirements.txt
    ansible-galaxy collection install cisco.ios
    ```

3.  **Run the pipeline:**

    ```bash
    chmod +x run_pipeline.sh
    ./run_pipeline.sh
    ```

-----

*Created by Mateusz W*

```
```
