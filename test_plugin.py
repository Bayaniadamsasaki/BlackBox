#!/usr/bin/env python3
# Test script to verify plugin changes
import sys
sys.path.append('.')

from plugins.scan_nuclei import Nuclei

# Test the plugin
nuclei = Nuclei()
print(f"Plugin name: {nuclei.name}")
print(f"Binary name: {nuclei.bin_name}")
print(f"Available: {nuclei.is_available()}")

# Test command generation
cmd_test = nuclei.run("http://testphp.vulnweb.com", severity="critical", tags="cve", extra="")
print(f"Generated command for: {cmd_test}")

# Check the actual run method without executing
import inspect
source = inspect.getsource(nuclei.run)
print("Current run method source:")
print(source)
