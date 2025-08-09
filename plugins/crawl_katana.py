# plugins/crawl_katana.py
import os
import re
import subprocess
from .base import Plugin
from rich.console import Console

console = Console()

class Katana(Plugin):
    name = "Katana (Crawler)"
    category = "Crawler"
    description = "Modern web crawler with JS support"
    bin_name = "katana"

    def clean_url_for_filename(self, url: str) -> str:
        """Clean URL for safe filename"""
        cleaned = url.replace('://', '_').replace('/', '_')
        # Remove invalid filename characters
        cleaned = re.sub(r'[<>:"/\\|?*]', '_', cleaned)
        return cleaned

    def run(self, url: str, out_dir="reports", depth=2, headless=False, extra=""):
        self.ensure_reports_dir(out_dir)
        out = f"{out_dir}/katana_{self.clean_url_for_filename(url)}.txt"
        
        # Try headless first if requested, fallback to passive mode if fails
        if headless:
            console.print("[yellow]Mencoba mode headless...[/yellow]")
            flags = f"-d {depth} -kf -silent -headless"
            cmd = f"katana -u {url} {flags} -o {out} {extra}"
            
            try:
                console.print(f"[cyan]$ {cmd}[/cyan]")
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=300)
                
                if result.returncode != 0 and ("virus" in result.stderr.lower() or "leakless" in result.stderr.lower()):
                    console.print("[red]Headless mode gagal - Windows Defender memblokir browser.[/red]")
                    console.print("[yellow]Mencoba mode standard (tanpa JS)...[/yellow]")
                    return self._run_standard_mode(url, out_dir, depth, extra)
                elif result.returncode != 0:
                    console.print(f"[red]Command failed ({result.returncode})[/red]")
                    console.print("[yellow]Mencoba mode standard sebagai fallback...[/yellow]")
                    return self._run_standard_mode(url, out_dir, depth, extra)
                else:
                    console.print("[green]Headless crawling berhasil![/green]")
                    return out
                    
            except subprocess.TimeoutExpired:
                console.print("[red]Timeout - mencoba mode standard...[/red]")
                return self._run_standard_mode(url, out_dir, depth, extra)
        else:
            return self._run_standard_mode(url, out_dir, depth, extra)
    
    def _run_standard_mode(self, url: str, out_dir: str, depth: int, extra: str):
        """Run Katana in standard mode without headless browser"""
        out = f"{out_dir}/katana_{self.clean_url_for_filename(url)}.txt"
        # Standard mode tanpa headless, masih bisa crawl links dari HTML
        flags = f"-d {depth} -kf -silent"
        cmd = f"katana -u {url} {flags} -o {out} {extra}"
        
        console.print(f"[cyan]$ {cmd}[/cyan]")
        try:
            subprocess.run(cmd, shell=True, check=True, timeout=180)
            console.print("[green]Standard crawling selesai![/green]")
        except subprocess.CalledProcessError as e:
            console.print(f"[red]Command failed ({e.returncode})[/red]")
        except subprocess.TimeoutExpired:
            console.print("[red]Timeout pada standard mode[/red]")
            
        return out
