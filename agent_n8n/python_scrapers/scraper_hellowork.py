#!/usr/bin/env python3
"""
Scraper HelloWork pour offres cybersécurité alternance
URL: https://www.hellowork.com/fr-fr/emploi/recherche.html
"""

import requests
import time
import json
import re
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urljoin, quote

class HelloWorkScraper:
    def __init__(self):
        self.base_url = "https://www.hellowork.com"
        self.search_url = f"{self.base_url}/fr-fr/emploi/recherche.html"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'fr-FR,fr;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })

    def search_cybersecurity_alternance(self, ville="MARSEILLE", rayon=20):
        """
        Recherche des offres cybersécurité en alternance
        """
        params = {
            "k": "cybersécurité",
            "k_autocomplete": "",
            "l": ville,
            "l_autocomplete": "",
            "st": "relevance",
            "c": "Alternance",
            "cod": "5",
            "ray": str(rayon),
            "d": "all"
        }

        try:
            print(f"🔍 Recherche sur HelloWork : cybersécurité alternance à {ville}")
            response = self.session.get(self.search_url, params=params)
            response.raise_for_status()

            return self._parse_search_results(response.text)

        except Exception as e:
            print(f"❌ Erreur lors de la recherche HelloWork: {e}")
            return []

    def _parse_search_results(self, html_content):
        """
        Parse les résultats de recherche HelloWork
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        offres = []

        # Sélecteur pour les offres d'emploi
        # D'après l'analyse, chaque offre semble être dans un conteneur spécifique
        job_containers = soup.find_all('div', class_=re.compile(r'(job|offer|result|card)', re.I))

        if not job_containers:
            # Essayer d'autres sélecteurs
            job_containers = soup.find_all('article') or soup.find_all('li', class_=re.compile(r'(job|offer)', re.I))

        for container in job_containers:
            try:
                offre = self._extract_job_data(container)
                if offre and self._is_cybersecurity_alternance(offre):
                    offres.append(offre)
            except Exception as e:
                print(f"⚠️ Erreur parsing offre: {e}")
                continue

        print(f"✅ {len(offres)} offres cybersécurité alternance trouvées sur HelloWork")
        return offres

    def _extract_job_data(self, container):
        """
        Extrait les données d'une offre individuelle
        """
        # Recherche du titre
        title_elem = (
            container.find('h2') or
            container.find('h3') or
            container.find('a', href=re.compile(r'/emploi/')) or
            container.find(class_=re.compile(r'(title|job-title)', re.I))
        )

        if not title_elem:
            return None

        title = title_elem.get_text(strip=True)

        # Recherche de l'entreprise
        company_elem = (
            container.find(class_=re.compile(r'(company|employer|recruteur)', re.I)) or
            container.find('span', text=re.compile(r'recrutement', re.I))
        )
        company = company_elem.get_text(strip=True) if company_elem else "Non spécifié"

        # Recherche de la localisation
        location_elem = container.find(class_=re.compile(r'(location|lieu|ville)', re.I))
        location = location_elem.get_text(strip=True) if location_elem else "Non spécifié"

        # Recherche du type de contrat
        contract_elem = container.find(text=re.compile(r'(Alternance|Contrat|apprentissage)', re.I))
        contract_type = "Alternance" if contract_elem else "Non spécifié"

        # Recherche de la durée
        duration_elem = container.find(text=re.compile(r'(\d+\s*(mois|ans?))', re.I))
        duration = duration_elem.strip() if duration_elem else "Non spécifié"

        # Recherche du salaire
        salary_elem = container.find(text=re.compile(r'(\d+.*€)', re.I))
        salary = salary_elem.strip() if salary_elem else "Non spécifié"

        # URL de l'offre
        link_elem = container.find('a', href=re.compile(r'/emploi/'))
        job_url = urljoin(self.base_url, link_elem['href']) if link_elem else ""

        # Date de publication
        date_elem = container.find(text=re.compile(r'(il y a|depuis)', re.I))
        published_date = date_elem.strip() if date_elem else "Récent"

        return {
            "title": title,
            "company": company,
            "location": location,
            "contract_type": contract_type,
            "duration": duration,
            "salary": salary,
            "description": f"{title} - {company} - {location}",
            "url": job_url,
            "published_date": published_date,
            "source": "HelloWork",
            "source_url": job_url,
            "scraped_at": datetime.now().isoformat()
        }

    def _is_cybersecurity_alternance(self, offre):
        """
        Vérifie si l'offre correspond aux critères cybersécurité + alternance
        """
        keywords_cyber = [
            'cybersécurité', 'cybersecurity', 'cyber', 'sécurité informatique',
            'soc', 'analyste sécurité', 'expert sécurité', 'ingénieur sécurité'
        ]

        keywords_alternance = [
            'alternance', 'apprentissage', 'contrat pro', 'professionnalisation'
        ]

        text_to_check = f"{offre['title']} {offre['description']} {offre['contract_type']}".lower()

        has_cyber = any(keyword.lower() in text_to_check for keyword in keywords_cyber)
        has_alternance = any(keyword.lower() in text_to_check for keyword in keywords_alternance)

        return has_cyber and has_alternance

    def get_job_details(self, job_url):
        """
        Récupère les détails complets d'une offre
        """
        try:
            response = self.session.get(job_url)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # Extraction de la description complète
            description_elem = (
                soup.find('div', class_=re.compile(r'(description|content|detail)', re.I)) or
                soup.find('section', class_=re.compile(r'(description|content)', re.I))
            )

            full_description = description_elem.get_text(strip=True) if description_elem else ""

            return {
                "full_description": full_description,
                "extracted_at": datetime.now().isoformat()
            }

        except Exception as e:
            print(f"❌ Erreur récupération détails: {e}")
            return {}

def main():
    """Test du scraper HelloWork"""
    scraper = HelloWorkScraper()

    # Test de recherche
    offres = scraper.search_cybersecurity_alternance("MARSEILLE")

    print(f"\n📊 RÉSULTATS HELLOWORK:")
    print(f"Nombre d'offres trouvées: {len(offres)}")

    for i, offre in enumerate(offres[:5], 1):  # Afficher les 5 premières
        print(f"\n{i}. {offre['title']}")
        print(f"   Entreprise: {offre['company']}")
        print(f"   Lieu: {offre['location']}")
        print(f"   Durée: {offre['duration']}")
        print(f"   Salaire: {offre['salary']}")
        print(f"   URL: {offre['url']}")

    return offres

if __name__ == "__main__":
    main()