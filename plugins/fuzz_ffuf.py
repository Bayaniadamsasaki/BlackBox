# plugins/fuzz_ffuf.py
import os
import re
from .base import Plugin

class FFUF(Plugin):
    name = "FFUF (Content Discovery)"
    category = "Fuzzer"
    description = "Fast web fuzzer for directories/params"
    bin_name = "ffuf"
    
    def clean_url_for_filename(self, url: str) -> str:
        """Clean URL for safe filename"""
        cleaned = url.replace("://", "_").replace("/", "_")
        # Remove invalid filename characters
        cleaned = re.sub(r'[<>:"/\\|?*]', '_', cleaned)
        return cleaned
    
    def get_default_wordlist(self, mode="dir"):
        """Get default wordlist based on mode"""
        base_dir = os.path.dirname(os.path.dirname(__file__))
        if mode == "dir":
            return os.path.join(base_dir, "wordlists", "common-dirs.txt")
        else:  # param mode
            return os.path.join(base_dir, "wordlists", "common-params.txt")

    def run(self, url: str, wordlist: str, out_dir="reports", mode="dir", extra=""):
        self.ensure_reports_dir(out_dir)
        
        # Use default wordlist if file doesn't exist
        if not os.path.isfile(wordlist):
            default_wl = self.get_default_wordlist(mode)
            if os.path.isfile(default_wl):
                print(f"File {wordlist} tidak ditemukan, menggunakan wordlist default: {default_wl}")
                wordlist = default_wl
            else:
                print(f"Wordlist {wordlist} tidak ditemukan dan wordlist default tidak tersedia!")
                return None
        
        stem = self.clean_url_for_filename(url)
        out_json = f"{out_dir}/ffuf_{stem}.json"
        if mode == "dir":
            cmd = f"ffuf -u {url.rstrip('/')}/FUZZ -w {wordlist} -of json -o {out_json} {extra}"
        else:  # param fuzz
            cmd = f"ffuf -u '{url}?FUZZ=test' -w {wordlist} -of json -o {out_json} {extra}"
        self.run_cmd(cmd)
        return out_json
