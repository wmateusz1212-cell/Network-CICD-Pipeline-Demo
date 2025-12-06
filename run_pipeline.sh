#!/bin/bash

# Kolory do outputu
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== STEP 1: DEPLOY CONFIGURATION (ANSIBLE) ===${NC}"
# Uruchamiamy Playbook
ansible-playbook playbooks/deploy_ospf.yml

# Sprawdzamy kod wyjścia (czy Ansible zakończył się sukcesem?)
if [ $? -eq 0 ]; then
    echo -e "${GREEN}>>> Deployment Successful! Proceeding to Testing phase...${NC}"
else
    echo -e "${RED}>>> Deployment FAILED! Stopping pipeline.${NC}"
    exit 1
fi

echo -e "\n${GREEN}=== STEP 2: VERIFY NETWORK STATE (PYATS) ===${NC}"
# Uruchamiamy testy PyATS (pamiętaj o środowisku wirtualnym jeśli używasz)
python3 verify_ospf.py

# Sprawdzamy wynik testów
if [ $? -eq 0 ]; then
    echo -e "\n${GREEN}✅ CI/CD PIPELINE FINISHED SUCCESSFULLY! The network is healthy.${NC}"
    exit 0
else
    echo -e "\n${RED}❌ PIPELINE FAILED! Tests did not pass. Check logs.${NC}"
    exit 1
fi
