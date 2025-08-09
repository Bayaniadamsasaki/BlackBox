# plugins/recon_subfinder.py
import re
from .base import Plugin

class Subfinder(Plugin):
    name = "Subfinder (Recon)"
    category = "Recon"
    description = "Passive subdomain enumeration"
    bin_name = "subfinder"

    def clean_domain(self, domain: str) -> str:
        """Clean domain string for safe filename"""
        # Remove protocol if present
        domain = re.sub(r'^https?://', '', domain)
        # Remove trailing slashes
        domain = domain.rstrip('/')
        # Replace invalid filename characters
        domain = re.sub(r'[<>:"/\\|?*]', '_', domain)
        return domain

    def run(self, domain: str, out_dir="reports", extra=""):
        self.ensure_reports_dir(out_dir)
        
        # Clean domain for filename
        clean_domain = self.clean_domain(domain)
        out = f"{out_dir}/subfinder_{clean_domain}.txt"
        
        # Use original domain for the actual command
        original_domain = re.sub(r'^https?://', '', domain.rstrip('/'))
        cmd = f"subfinder -d {original_domain} -silent -o {out} {extra}"
        self.run_cmd(cmd)
        return out
