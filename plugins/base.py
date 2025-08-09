# plugins/base.py
import os, shutil, subprocess
from datetime import datetime
from rich.console import Console

console = Console()

class Plugin:
    name        = "Base"
    category    = "General"
    description = "Base plugin"
    bin_name    = None              # nama executable CLI

    def is_available(self) -> bool:
        return shutil.which(self.bin_name) is not None if self.bin_name else False

    def ensure_reports_dir(self, reports_dir="reports"):
        os.makedirs(reports_dir, exist_ok=True)
        return reports_dir

    def timestamped_path(self, base, ext):
        ts = datetime.now().strftime("%Y%m%d-%H%M%S")
        return f"{base}-{ts}.{ext}"

    def run_cmd(self, cmd: str):
        console.rule(f"[bold]{self.name}[/bold]")
        console.print(f"[cyan]$ {cmd}[/cyan]")
        try:
            subprocess.run(cmd, shell=True, check=True)
        except subprocess.CalledProcessError as e:
            console.print(f"[red]Command failed ({e.returncode})[/red]")
