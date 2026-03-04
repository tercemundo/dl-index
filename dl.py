
#!/usr/bin/env python3
"""
Script dinámico para SIENA - URL CORREGIDAS
"""

import os
import sys
from urllib.parse import urljoin, urlparse
from pathlib import Path

import argparse  # <--- nuevo
import requests
from bs4 import BeautifulSoup
from urllib3.exceptions import InsecureRequestWarning
import warnings
warnings.filterwarnings('ignore', category=InsecureRequestWarning)

def create_output_directory(output_dir):
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    print(f"✓ Directorio '{output_dir}' listo")

def fetch_html(url):
    try:
        r = requests.get(url, timeout=30, verify=False)
        r.raise_for_status()
        return r.text
    except:
        print(f"✗ Error obteniendo {url}")
        return None

def parse_siena_files(html):
    soup = BeautifulSoup(html, 'html.parser')
    files = []
    for tr in soup.find_all('tr'):
        img = tr.find('img', alt='[TXT]')
        if img:
            a = tr.find('a', href=True)
            if a:
                files.append(a['href'])
    return files

def download_file(page_url, href, output_dir):
    full_url = urljoin(page_url, href)
    try:
        r = requests.get(full_url, timeout=30, verify=False)
        r.raise_for_status()

        path = urlparse(full_url).path.lstrip('/')
        local_path = os.path.join(output_dir, path)
        os.makedirs(os.path.dirname(local_path), exist_ok=True)

        with open(local_path, 'wb') as f:
            f.write(r.content)

        size = len(r.content)
        print(f"  ✓ {href} → {full_url} ({size/1024:.1f} KB)")
        return True, size

    except Exception as e:
        print(f"  ✗ {href} → {full_url}: {e}")
        return False, 0

def process_path(base_url, path, output_dir):
    page_url = urljoin(base_url, path)
    print(f"\n>>> {page_url}")

    html = fetch_html(page_url)
    if not html:
        return 0, 0, 0

    files = parse_siena_files(html)
    print(f"  Encontrados {len(files)} archivos")

    total, ok, bytes_dl = 0, 0, 0
    for href in files:
        total += 1
        success, size = download_file(page_url, href, output_dir)
        if success:
            ok += 1
            bytes_dl += size

    return total, ok, bytes_dl

def main():
    parser = argparse.ArgumentParser(
        description="Downloader de archivos TXT de SIENA"
    )
    parser.add_argument(
        "-u", "--url",
        required=True,
        help="URL base, por ejemplo https://ejemplo.ejemplo.com.ar/"
    )
    parser.add_argument(
        "-d", "--directory",
        required=True,
        help="Directorio de salida, por ejemplo /tmp"
    )
    parser.add_argument(
        "-p", "--path",
        default="tmp/",
        help="Path inicial relativo a la base (default: tmp/)"
    )

    args = parser.parse_args()

    base_url = args.url
    output_dir = args.directory
    start_path = args.path

    print("=" * 80)
    print("SIENA DOWNLOADER - URLS CORREGIDAS")
    print("=" * 80)

    create_output_directory(output_dir)

    grand_total = grand_ok = grand_bytes = 0

    t, o, b = process_path(base_url, start_path, output_dir)
    grand_total += t
    grand_ok += o
    grand_bytes += b

    print("\n" + "=" * 80)
    print("RESUMEN FINAL")
    print("=" * 80)
    print(f"Total: {grand_total} | OK: {grand_ok} | {grand_bytes/(1024*1024):.2f} MB")
    print(f"Guardados en: {output_dir}/")
    print("=" * 80)

if __name__ == "__main__":
    main()
