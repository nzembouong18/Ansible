#!/usr/bin/env python3
"""Inventaire dynamique minimal (script) : respecte le contrat --list / --host <nom>.

Source simulée : un dictionnaire (en vrai : API CMDB, cloud, base de données...).
Usage : ansible-inventory -i inventory-script.py --graph
"""
import argparse
import json

SERVERS = [
    {"name": "web-01", "ip": "10.0.1.11", "role": "web", "env": "prod", "cpu": 4},
    {"name": "web-02", "ip": "10.0.1.12", "role": "web", "env": "prod", "cpu": 4},
    {"name": "db-01", "ip": "10.0.2.21", "role": "db", "env": "prod", "cpu": 8},
    {"name": "web-stg", "ip": "10.0.9.11", "role": "web", "env": "staging", "cpu": 2},
]


def build_inventory():
    inventory = {"_meta": {"hostvars": {}}, "all": {"children": ["ungrouped"]}}
    for srv in SERVERS:
        for group in (f"role_{srv['role']}", f"env_{srv['env']}"):
            inventory.setdefault(group, {"hosts": []})["hosts"].append(srv["name"])
        # _meta.hostvars évite un appel --host par hôte (beaucoup plus rapide)
        inventory["_meta"]["hostvars"][srv["name"]] = {
            "ansible_host": srv["ip"],
            "cpu_count": srv["cpu"],
        }
    return inventory


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--host")
    args = parser.parse_args()

    if args.host:
        print(json.dumps(build_inventory()["_meta"]["hostvars"].get(args.host, {})))
    else:
        print(json.dumps(build_inventory(), indent=2))


if __name__ == "__main__":
    main()
