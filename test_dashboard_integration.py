#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test Dashboard Integration
Verifies HTML structure and JavaScript integration without running Flask
"""

import re
from pathlib import Path

print("=" * 70)
print("  TEST DASHBOARD INTEGRATION - MedSystem PRO")
print("=" * 70)

# Read HTML file
html_path = Path(__file__).parent / "templates" / "index_pro.html"
if not html_path.exists():
    print(f"\n✗ HTML file not found: {html_path}")
    exit(1)

print(f"\n[1/4] Reading HTML file...")
with open(html_path, 'r', encoding='utf-8') as f:
    html_content = f.read()
print(f"  ✓ HTML file read ({len(html_content)} bytes)")

# Check for data-metric attributes
print(f"\n[2/4] Checking for data-metric attributes...")
metrics = ['consultas_hoje', 'pacientes_ativos', 'exames_pendentes', 'novos_pacientes']
found_metrics = {}

for metric in metrics:
    pattern = f'data-metric="{metric}"'
    if pattern in html_content:
        found_metrics[metric] = True
        print(f"  ✓ Found: {metric}")
    else:
        found_metrics[metric] = False
        print(f"  ✗ Missing: {metric}")

# Check for table IDs
print(f"\n[3/4] Checking for table and timeline IDs...")
elements = {
    'exames-pendentes-tbody': 'Exames Pendentes table body',
    'proximos-retornos-timeline': 'Próximos Retornos timeline',
    'btn-refresh-dashboard': 'Refresh Dashboard button'
}

found_elements = {}
for elem_id, desc in elements.items():
    pattern = f'id="{elem_id}"'
    if pattern in html_content:
        found_elements[elem_id] = True
        print(f"  ✓ Found: {desc} (id='{elem_id}')")
    else:
        found_elements[elem_id] = False
        print(f"  ✗ Missing: {desc} (id='{elem_id}')")

# Read main.js file
print(f"\n[4/4] Checking JavaScript implementation...")
js_path = Path(__file__).parent / "static" / "js" / "main.js"
if not js_path.exists():
    print(f"  ✗ JS file not found: {js_path}")
    exit(1)

with open(js_path, 'r', encoding='utf-8') as f:
    js_content = f.read()

# Check for functions
functions = [
    'carregarDashboard',
    'getDayName',
    'getPriorityClass',
    'getStatusBadgeClass',
    'setupKeyboardShortcuts'
]

found_functions = {}
for func in functions:
    pattern = f'function {func}'
    if pattern in js_content:
        found_functions[func] = True
        print(f"  ✓ Found function: {func}")
    else:
        found_functions[func] = False
        print(f"  ✗ Missing function: {func}")

# Summary
print(f"\n" + "=" * 70)
print(f"  SUMMARY")
print(f"=" * 70)

all_metrics_found = all(found_metrics.values())
all_elements_found = all(found_elements.values())
all_functions_found = all(found_functions.values())

print(f"\n  Data-metric attributes: {'✓ ALL FOUND' if all_metrics_found else '✗ SOME MISSING'}")
print(f"  HTML Elements: {'✓ ALL FOUND' if all_elements_found else '✗ SOME MISSING'}")
print(f"  JavaScript Functions: {'✓ ALL FOUND' if all_functions_found else '✗ SOME MISSING'}")

if all_metrics_found and all_elements_found and all_functions_found:
    print(f"\n  ✓ INTEGRATION TEST PASSED!")
    print(f"\n  Dashboard Integration Summary:")
    print(f"  • Metric cards with data-metric attributes: {sum(found_metrics.values())}/{len(metrics)}")
    print(f"  • HTML elements with correct IDs: {sum(found_elements.values())}/{len(elements)}")
    print(f"  • JavaScript functions implemented: {sum(found_functions.values())}/{len(functions)}")
    exit(0)
else:
    print(f"\n  ✗ INTEGRATION TEST FAILED!")
    exit(1)
