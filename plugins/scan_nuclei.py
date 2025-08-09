# plugins/scan_nuclei.py
import re
from .base import Plugin

class Nuclei(Plugin):
    name = "Nuclei (Vulnerability Scan)"
    category = "Scanner"
    description = "Template-based vuln scanner (CVE, misconfig)"
    bin_name = "nuclei"

    def clean_target_for_filename(self, target: str) -> str:
        """Clean target for safe filename"""
        cleaned = target.replace("://", "_").replace("/", "_")
        # Remove invalid filename characters
        cleaned = re.sub(r'[<>:"/\\|?*]', '_', cleaned)
        return cleaned

    def run(self, target: str, out_dir="reports", use_urls_file=False, severity=None, tags=None, extra=""):
        self.ensure_reports_dir(out_dir)
        stem = self.clean_target_for_filename(target)
        out = f"{out_dir}/nuclei_{stem}.txt"
        
        # Build command parts
        sev_flag = f"-severity {severity}" if severity else ""
        tags_flag = f"-tags {tags}" if tags else ""
        
        if use_urls_file:
            cmd = f"nuclei -l {target} -o {out} {sev_flag} {tags_flag} {extra}".strip()
        else:
            cmd = f"nuclei -u {target} -o {out} {sev_flag} {tags_flag} {extra}".strip()
        
        # Clean up extra spaces
        cmd = " ".join(cmd.split())
        
        self.run_cmd(cmd)
        return out
