#!/usr/bin/env python3
import os, sys, shutil
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from pyfiglet import figlet_format

# import plugins
from plugins.recon_subfinder import Subfinder
from plugins.crawl_katana import Katana
from plugins.crawl_simple import SimpleCrawler
from plugins.fuzz_ffuf import FFUF
from plugins.scan_nuclei import Nuclei

console = Console()

# Tambahkan folder lokal "bin/" ke PATH agar .exe di proyek terdeteksi.
# Cukup taruh subfinder.exe, katana.exe, ffuf.exe, nuclei.exe ke folder ini bila belum ada di PATH global.
BIN_DIR = os.path.join(os.path.dirname(__file__), "bin")
if os.path.isdir(BIN_DIR):
    os.environ["PATH"] = BIN_DIR + os.pathsep + os.environ.get("PATH", "")

PLUGINS = [
    Subfinder(), Katana(), SimpleCrawler(), FFUF(), Nuclei()
]

def banner():
    console.print("[bold cyan]" + figlet_format("BLACKBOX", width=120) + "[/bold cyan]")
    console.print("[bold magenta]by Sasaki[/bold magenta]\n")
    console.print(Panel.fit("Toolkit interaktif. Jalankan HANYA pada aset yang kamu miliki/diizinkan.", style="bold yellow"))

def pause():
    console.print("\n[dim]Tekan Enter untuk kembali ke menu...[/dim]")
    input()

def list_tools():
    t = Table(title="Tools", show_lines=False)
    t.add_column("#", justify="right")
    t.add_column("Nama")
    t.add_column("Kategori")
    t.add_column("Ketersediaan")
    t.add_column("Deskripsi")
    for i, p in enumerate(PLUGINS, start=1):
        t.add_row(str(i), p.name, p.category, "[green]OK[/green]" if p.is_available() else "[red]Not Found[/red]", p.description)
    console.print(t)

def ensure_bins_msg():
    missing = [p.bin_name for p in PLUGINS if not p.is_available()]
    if missing:
        console.print(Panel.fit(
            "Tool berikut belum terinstal: [red]{}[/red]\nSilakan install via package manager / release GitHub masing-masing."
            .format(", ".join(missing)), style="red"))
    else:
        console.print(Panel.fit("Semua tools terdeteksi. Gas!", style="green"))

def menu():
    while True:
        os.system("clear" if os.name != "nt" else "cls")
        banner()
        console.print("[bold]1[/bold]) Daftar Tools")
        console.print("[bold]2[/bold]) Recon (Subfinder)")
        console.print("[bold]3[/bold]) Crawler (Katana)")
        console.print("[bold]4[/bold]) Fuzzer (FFUF)")
        console.print("[bold]5[/bold]) Vulnerability Scan (Nuclei)")
        console.print("[bold]6[/bold]) Pipeline Cepat (Katana ➜ Nuclei)")
        console.print("[bold]0[/bold]) Keluar\n")
        choice = input("Pilih opsi: ").strip()

        if choice == "1":
            list_tools(); ensure_bins_msg(); pause()

        elif choice == "2":
            console.print("[dim]Contoh input:[/dim]")
            console.print("  - [cyan]example.com[/cyan] (tanpa protokol)")
            console.print("  - [cyan]testphp.vulnweb.com[/cyan] (domain saja)")
            domain = input("Domain (contoh: example.com): ").strip()
            extra  = input("Tambahan flag (opsional, Enter untuk skip): ").strip()
            out = Subfinder().run(domain, extra=extra)
            console.print(f"[green]Output:[/green] {out}"); pause()

        elif choice == "3":
            url    = input("URL target (https://example.com): ").strip()
            depth  = input("Depth (default 2): ").strip() or "2"
            
            # Check if Katana is available
            katana = Katana()
            simple_crawler = SimpleCrawler()
            
            if katana.is_available():
                console.print("[dim]Mode crawling:[/dim]")
                console.print("  - [green]N[/green] = Standard mode (aman, crawl dari HTML)")  
                console.print("  - [yellow]Y[/yellow] = Headless mode (dengan JS, mungkin diblokir Windows Defender)")
                head   = input("Headless? (y/N): ").lower().startswith("y")
                extra  = input("Tambahan flag (opsional): ").strip()
                out = katana.run(url, depth=int(depth), headless=head, extra=extra)
            elif simple_crawler.is_available():
                console.print("[yellow]Katana tidak tersedia, menggunakan Simple Crawler (Python)[/yellow]")
                out = simple_crawler.run(url, depth=int(depth))
            else:
                console.print("[red]Tidak ada crawler yang tersedia![/red]")
                pause()
                continue
                
            console.print(f"[green]Output:[/green] {out}")
            # Show results preview if file exists and not empty
            if os.path.isfile(out) and os.path.getsize(out) > 0:
                console.print(f"[blue]File berisi {sum(1 for line in open(out))} URLs[/blue]")
            else:
                console.print("[red]File output kosong atau tidak ada[/red]")
            pause()

        elif choice == "4":
            url = input("Base URL (https://example.com): ").strip()
            console.print("[dim]Wordlist default tersedia:[/dim]")
            console.print("  - [cyan]wordlists/common-dirs.txt[/cyan] (untuk directory fuzzing)")
            console.print("  - [cyan]wordlists/common-params.txt[/cyan] (untuk parameter fuzzing)")
            wl  = input("Path wordlist (Enter untuk wordlist default, atau path custom): ").strip()
            mode = input("Mode [dir/param] (default dir): ").strip() or "dir"
            
            # Set default wordlist if empty
            if not wl:
                default_wl = f"wordlists/common-{'dirs' if mode == 'dir' else 'params'}.txt"
                wl = default_wl
                console.print(f"[green]Menggunakan wordlist default: {wl}[/green]")
            
            extra = input("Tambahan flag (opsional): ").strip()
            out = FFUF().run(url, wl, mode=mode, extra=extra)
            console.print(f"[green]Output:[/green] {out}"); pause()

        elif choice == "5":
            console.print("[dim]Mode scan:[/dim]")
            console.print("  - [cyan]URL tunggal[/cyan]: https://example.com")
            console.print("  - [cyan]File URLs[/cyan]: path/ke/urls.txt (satu URL per baris)")
            target = input("Target (URL tunggal atau file urls): ").strip()
            use_file = os.path.isfile(target)
            
            console.print("[dim]Severity levels (kosongkan untuk semua):[/dim]")
            console.print("  - [green]low[/green]: Masalah minor")
            console.print("  - [yellow]medium[/yellow]: Masalah sedang") 
            console.print("  - [red]high[/red]: Masalah serius")
            console.print("  - [bold red]critical[/bold red]: Masalah kritis")
            severity = input("Filter severity (low,medium,high,critical) atau Enter untuk semua: ").strip()
            
            console.print("[dim]Tags populer (kosongkan untuk semua):[/dim]")
            console.print("  - [cyan]cve[/cyan]: CVE vulnerabilities")
            console.print("  - [cyan]misconfig[/cyan]: Misconfiguration issues")
            console.print("  - [cyan]exposure[/cyan]: Information exposure")
            console.print("  - [cyan]sqli[/cyan]: SQL injection")
            console.print("  - [cyan]xss[/cyan]: Cross-site scripting")
            tags = input("Filter tags (mis: cve,misconfig) atau Enter untuk semua: ").strip()
            
            extra = input("Tambahan flag nuclei (opsional): ").strip()
            out = Nuclei().run(target, use_urls_file=use_file, severity=severity or None, tags=tags or None, extra=extra)
            console.print(f"[green]Output:[/green] {out}")
            
            # Show scan results preview
            if os.path.isfile(out) and os.path.getsize(out) > 0:
                try:
                    import json
                    vulns_count = sum(1 for line in open(out, encoding='utf-8') if line.strip())
                    console.print(f"[blue]Ditemukan {vulns_count} hasil scan[/blue]")
                except:
                    console.print("[blue]File hasil scan tersedia untuk analisis[/blue]")
            else:
                console.print("[yellow]Tidak ada vulnerability ditemukan atau scan gagal[/yellow]")
            pause()

        elif choice == "6":
            url = input("URL target untuk crawl lalu scan (https://example.com): ").strip()
            
            # 1) Crawl - Use available crawler
            katana = Katana()
            simple_crawler = SimpleCrawler()
            
            if katana.is_available():
                console.print("[blue]Menggunakan Katana untuk crawling...[/blue]")
                urls_file = katana.run(url, depth=2, headless=False)
            elif simple_crawler.is_available():
                console.print("[blue]Menggunakan Simple Crawler untuk crawling...[/blue]")
                urls_file = simple_crawler.run(url, depth=2)
            else:
                console.print("[red]Tidak ada crawler tersedia untuk pipeline![/red]")
                pause()
                continue
                
            console.print(f"[blue]URL hasil crawl:[/blue] {urls_file}")
            
            # Check if crawl was successful
            if not os.path.isfile(urls_file) or os.path.getsize(urls_file) == 0:
                console.print("[red]Crawling gagal atau tidak menemukan URL. Pipeline dihentikan.[/red]")
                pause()
                continue
            
            # 2) Scan dengan nuclei
            nuclei = Nuclei()
            if nuclei.is_available():
                out = nuclei.run(urls_file, use_urls_file=True, severity=None, tags=None)
                console.print(f"[green]Output Nuclei:[/green] {out}")
            else:
                console.print("[red]Nuclei tidak tersedia untuk scanning![/red]")
            
            pause()

        elif choice == "0":
            break
        else:
            console.print("[red]Pilihan tidak valid[/red]")
            pause()

if __name__ == "__main__":
    os.makedirs("reports", exist_ok=True)
    menu()
