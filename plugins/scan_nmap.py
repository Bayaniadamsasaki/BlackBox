# plugins/scan_nmap.py
import re
import os
from .base import Plugin

class Nmap(Plugin):
    name = "Nmap (Network Scanner)"
    category = "Scanner"
    description = "Network discovery and security auditing"
    bin_name = "nmap"

    def clean_target_for_filename(self, target: str) -> str:
        """Clean target for safe filename"""
        cleaned = target.replace("://", "_").replace("/", "_")
        # Remove invalid filename characters
        cleaned = re.sub(r'[<>:"/\\|?*]', '_', cleaned)
        return cleaned

    def clean_target_for_nmap(self, target: str) -> str:
        """Clean target for Nmap command - remove protocol and paths"""
        # Remove protocol (http://, https://, etc.)
        target = re.sub(r'^https?://', '', target)
        # Remove trailing paths/slashes
        target = target.split('/')[0]
        # Remove port if specified (nmap will handle ports separately)
        target = target.split(':')[0]
        return target

    def run(self, target: str, out_dir="reports", scan_type="basic", ports=None, extra=""):
        self.ensure_reports_dir(out_dir)
        
        # Clean target for filename (keep original for filename)
        stem = self.clean_target_for_filename(target)
        out = f"{out_dir}/nmap_{stem}.txt"
        
        # Clean target for nmap command (remove protocol, paths)
        clean_target = self.clean_target_for_nmap(target)
        
        # Build scan command based on type
        if scan_type == "basic":
            cmd = f"nmap -sS -O -sV {clean_target} -oN {out}"
        elif scan_type == "fast":
            cmd = f"nmap -F {clean_target} -oN {out}"
        elif scan_type == "comprehensive":
            cmd = f"nmap -sS -sU -O -sV -sC --script vuln {clean_target} -oN {out}"
        elif scan_type == "stealth":
            cmd = f"nmap -sS -f -T2 {clean_target} -oN {out}"
        elif scan_type == "custom":
            if ports:
                cmd = f"nmap -p {ports} {clean_target} -oN {out}"
            else:
                cmd = f"nmap {clean_target} -oN {out}"
        else:
            cmd = f"nmap {clean_target} -oN {out}"
        
        # Add extra flags if provided
        if extra:
            cmd += f" {extra}"
        
        # Clean up extra spaces
        cmd = " ".join(cmd.split())
        
        self.run_cmd(cmd)
        return out
