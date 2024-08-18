import os
from dotenv import load_dotenv
import tkinter as tk
from tkinter import messagebox
from threading import Thread
from scrap import google_search, fetch_emails_from_urls, save_to_csv

load_dotenv()

API_KEY = os.getenv('API_KEY')
CSE_ID = os.getenv('CSE_ID')

def show_progress_window():
    progress_window = tk.Toplevel()
    progress_window.title("En cours")
    progress_window.geometry("300x100")
    label = tk.Label(progress_window, text="Les robots recherchent sur la toile...", padx=20, pady=20)
    label.pack()
    return progress_window

def hide_progress_window(progress_window):
    progress_window.destroy()

def start_scraping(queries, max_sites, max_pages_per_site, progress_window):
    urls = []
    for query in queries:
        search_results = google_search(query, API_KEY, CSE_ID, num=max_sites)
        urls.extend([item['link'] for item in search_results])

    urls = urls[:max_sites]
    all_emails, total_pages_scraped, total_sites_scraped = fetch_emails_from_urls(urls, max_sites, max_pages_per_site)
    save_to_csv('emails.csv', all_emails)

    hide_progress_window(progress_window)

    result_text = f"Total d'emails trouvés: {len(all_emails)}\n"
    result_text += f"Total de pages scrappées: {total_pages_scraped}\n"
    result_text += f"Total de sites scrappés: {total_sites_scraped}\n\n"
    result_text += "Emails trouvés :\n"
    for email, site in all_emails.items():
        result_text += f"Email: {email}, Site: {site}\n"

    progress_window.after(0, lambda: messagebox.showinfo("Résultats du Scraping", result_text))

def run_scraping_thread(queries, max_sites, max_pages_per_site):
    progress_window = show_progress_window()
    Thread(target=start_scraping, args=(queries, max_sites, max_pages_per_site, progress_window)).start()

def run_gui():
    root = tk.Tk()
    root.title("Scraper d'Emails")

    tk.Label(root, text="Entrez les requêtes (séparées par des virgules):").pack(padx=10, pady=10)
    entry_queries = tk.Entry(root, width=50)
    entry_queries.pack(padx=10, pady=10)

    tk.Label(root, text="Nombre maximum de sites à visiter:").pack(padx=10, pady=10)
    entry_max_sites = tk.Entry(root, width=10)
    entry_max_sites.pack(padx=10, pady=10)
    entry_max_sites.insert(0, "50")  # Valeur par défaut

    tk.Label(root, text="Nombre maximum de pages par site:").pack(padx=10, pady=10)
    entry_max_pages_per_site = tk.Entry(root, width=10)
    entry_max_pages_per_site.pack(padx=10, pady=10)
    entry_max_pages_per_site.insert(0, "5")  # Valeur par défaut

    def on_submit():
        queries = entry_queries.get().split(',')
        queries = [q.strip() for q in queries]
        try:
            max_sites = int(entry_max_sites.get())
            max_pages_per_site = int(entry_max_pages_per_site.get())
            if not queries:
                messagebox.showwarning("Erreur", "Veuillez entrer au moins une requête.")
            elif max_sites <= 0 or max_pages_per_site <= 0:
                messagebox.showwarning("Erreur", "Les nombres doivent être des entiers positifs.")
            else:
                run_scraping_thread(queries, max_sites, max_pages_per_site)
        except ValueError:
            messagebox.showwarning("Erreur", "Veuillez entrer un nombre valide pour les valeurs numériques.")

    tk.Button(root, text="Envoyer", command=on_submit).pack(padx=10, pady=10)

    root.mainloop()

if __name__ == "__main__":
    run_gui()
