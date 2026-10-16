#!/usr/bin/env python3
"""Inventaire dynamique alimenté par un CSV (--list / --host)."""
import argparse
import csv
import json
import os
import sys

DEFAULT_CSV = os.path.join(os.path.dirname(os.path.abspath(__file__)), "serveurs.csv")


def load_servers(path):
    try:
        with open(path, newline="", encoding="utf-8") as handle:
            return list(csv.DictReader(handle))
    except FileNotFoundError:
        sys.exit(f"Erreur : fichier CMDB introuvable : {path}")


def build_inventory(servers):
    inventory = {"_meta": {"hostvars": {}}}
    for srv in servers:
        for group in (f"role_{srv['role']}", f"env_{srv['env']}"):
            inventory.setdefault(group, {"hosts": []})["hosts"].append(srv["name"])
        inventory["_meta"]["hostvars"][srv["name"]] = {
            "ansible_host": srv["ip"],
            "ansible_connection": "local",   # lab : pas de connexion réelle
            "cpu": int(srv["cpu"]),
            "datacenter": srv["datacenter"],
            "env": srv["env"],
            "role": srv["role"],
        }
    return inventory


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--host")
    args = parser.parse_args()

    inventory = build_inventory(load_servers(os.environ.get("CMDB_CSV", DEFAULT_CSV)))
    if args.host:
        print(json.dumps(inventory["_meta"]["hostvars"].get(args.host, {})))
    else:
        print(json.dumps(inventory, indent=2))


if __name__ == "__main__":
    main()
