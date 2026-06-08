import argparse
import getpass
import re
import os
import pdfplumber
import pandas as pd

def secure_credentials():
    """Handles CLI arguments securely without exposing passwords in history."""
    parser = argparse.ArgumentParser(description="Scrape and parse Texas Energy Plan EFLs.")
    parser.add_argument("-u", "--username", required=True, help="Your electricity provider account username/email")
    parser.add_argument("-f", "--file", help="Path to a local EFL PDF (skips scraping step if provided)")
    
    args = parser.parse_args()
    
    password = None
    if not args.file:
        password = getpass.getpass(prompt="Enter your Provider Account Password: ")
        
    return args.username, password, args.file

def download_efl_pdf(username, password):
    """
    Uses Playwright to log in and download the EFL PDF file.
    """
    from playwright.sync_api import sync_playwright

    print(f"Connecting to provider portal as {username}...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=1000)
        page = browser.new_page()
        
        page.goto("https://myaccount.ambitenergy.com/login")
        
        page.get_by_label("Username").fill(username)
        page.get_by_label("Password").fill(password)
        page.click("button[type='submit']")
        page.wait_for_load_state("networkidle")
        
        print("Locating EFL document link...")
        with page.expect_download() as download_info:
            page.click("text=Electricity Facts Label") 
        
        download = download_info.value
        path = f"./downloaded_efl_{download.suggested_filename}"
        download.save_as(path)
        browser.close()
        print(f"EFL successfully saved to: {path}")
        return path

def extract_rates_from_pdf(pdf_path):
    """Parses text from a standard Texas EFL document using Regex"""
    print(f"Extracting rate structures from {pdf_path}...")
    
    extracted_text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            extracted_text += page.extract_text() or ""

    base_charge_match = re.search(r"Base Charge\s* \$?([0-9.]+)", extracted_text, re.IGNORECASE)
    energy_charge_match = re.search(r"Energy Charge\s*([0-9.]+)\s*¢", extracted_text, re.IGNORECASE)
    
    base_cost = float(base_charge_match.group(1)) if base_charge_match else 0.0
    energy_rate = float(energy_charge_match.group(1)) if energy_charge_match else 0.0
    
    print(f"Found Base Cost: ${base_cost}")
    print(f"Found Energy Rate: {energy_rate}¢ per kWh")
    
    return {
        "Base Cost": base_cost,
        "Raw Rate": energy_rate
    }

if __name__ == "__main__":
    username, password, local_file = secure_credentials()
    
    if local_file:
        pdf_path = local_file
    else:
        try:
            pdf_path = download_efl_pdf(username, password)
        except Exception as e:
            print(f"Failed to scrape portal automatically: {e}")
            exit(1)
            
    try:
        plan_data = extract_rates_from_pdf(pdf_path)
    except Exception as e:
        print(f"Failed to parse PDF: {e}")
