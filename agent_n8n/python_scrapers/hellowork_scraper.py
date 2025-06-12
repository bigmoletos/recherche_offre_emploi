#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SCRAPER HELLOWORK - ALTERNANCE CYBERSÉCURITÉ
Scraping des vraies offres d'emploi pour le workflow N8N
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import re
from datetime import datetime
import logging
from urllib.parse import urljoin, urlparse, parse_qs
import random
from typing import List, Dict, Optional

# Configuration logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class HelloWorkScraper:
    """Scraper pour HelloWork - Alternance Cybersécurité"""

    def __init__(self):
        self.base_url = "https://www.hellowork.com"
        self.search_url = "https://www.hellowork.com/fr-fr/emploi/recherche.html"

        # Headers pour éviter la détection
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'fr-FR,fr;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
        }

        # Session pour maintenir les cookies
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def search_offers(self, keywords: str = "alternance cybersécurité", location: str = "", max_pages: int = 3) -> List[Dict]:
        """
        Recherche les offres sur HelloWork
        """
        logger.info(f"🔍 Recherche HelloWork: '{keywords}' - {location}")

        all_offers = []

        for page in range(1, max_pages + 1):
            logger.info(f"📄 Scraping page {page}/{max_pages}")

            # Paramètres de recherche
            params = {
                'k': keywords,
                'l': location,
                'p': page,
                'sort': 'date'  # Tri par date
            }

            try:
                # Délai aléatoire pour éviter la détection
                time.sleep(random.uniform(2, 4))

                response = self.session.get(self.search_url, params=params, timeout=15)
                response.raise_for_status()

                logger.info(f"✅ Page {page} récupérée (status: {response.status_code})")

                # Parser la page
                soup = BeautifulSoup(response.content, 'html.parser')
                page_offers = self._extract_offers_from_page(soup, page)

                if not page_offers:
                    logger.warning(f"⚠️ Aucune offre trouvée page {page}")
                    break

                all_offers.extend(page_offers)
                logger.info(f"📊 {len(page_offers)} offres extraites page {page}")

            except requests.RequestException as e:
                logger.error(f"❌ Erreur requête page {page}: {e}")
                break
            except Exception as e:
                logger.error(f"❌ Erreur traitement page {page}: {e}")
                continue

        logger.info(f"🎯 Total offres trouvées: {len(all_offers)}")
        return all_offers

    def _extract_offers_from_page(self, soup: BeautifulSoup, page_num: int) -> List[Dict]:
        """
        Extrait les offres d'une page de résultats
        """
        offers = []

        # Sélecteurs possibles pour les offres HelloWork
        offer_selectors = [
            'article[data-testid="job-item"]',
            '.job-card',
            '.offer-item',
            'div[data-job-id]',
            'li[data-offer-id]',
            '.search-result-item'
        ]

        offer_elements = []
        for selector in offer_selectors:
            offer_elements = soup.select(selector)
            if offer_elements:
                logger.info(f"✅ Trouvé {len(offer_elements)} offres avec sélecteur: {selector}")
                break

        if not offer_elements:
            # Fallback: recherche par patterns de texte
            logger.warning("⚠️ Sélecteurs standards non trouvés, essai patterns fallback")
            offer_elements = self._find_offers_by_patterns(soup)

        for i, element in enumerate(offer_elements):
            try:
                offer_data = self._extract_offer_details(element, page_num, i)
                if offer_data and self._is_relevant_offer(offer_data):
                    offers.append(offer_data)

            except Exception as e:
                logger.error(f"❌ Erreur extraction offre {i}: {e}")
                continue

        return offers

    def _find_offers_by_patterns(self, soup: BeautifulSoup) -> List:
        """
        Recherche d'offres par patterns de texte (fallback)
        """
        logger.info("🔍 Recherche par patterns de texte...")

        # Recherche d'éléments contenant des mots-clés d'offres d'emploi
        keywords = ['alternance', 'apprentissage', 'cybersécurité', 'sécurité', 'informatique']

        potential_offers = []
        for keyword in keywords:
            elements = soup.find_all(text=re.compile(keyword, re.IGNORECASE))
            for elem in elements:
                parent = elem.parent
                while parent and parent.name not in ['article', 'div', 'li']:
                    parent = parent.parent
                if parent and parent not in potential_offers:
                    potential_offers.append(parent)

        logger.info(f"📋 {len(potential_offers)} éléments potentiels trouvés")
        return potential_offers[:20]  # Limite pour éviter le spam

    def _extract_offer_details(self, element, page_num: int, index: int) -> Optional[Dict]:
        """
        Extrait les détails d'une offre
        """
        try:
            # ID unique pour l'offre
            offer_id = f"hellowork-{int(time.time() * 1000)}-{page_num}-{index}"

            # Extraction du titre
            title = self._extract_text(element, [
                'h2 a', 'h3 a', '.job-title', '.offer-title',
                '[data-testid="job-title"]', 'a[href*="emploi"]'
            ])

            if not title:
                return None

            # Extraction de l'entreprise
            company = self._extract_text(element, [
                '.company-name', '.employer', '[data-testid="company-name"]',
                '.job-company', 'span[class*="company"]'
            ])

            # Extraction de la localisation
            location = self._extract_text(element, [
                '.location', '.job-location', '[data-testid="location"]',
                'span[class*="location"]', 'span[class*="city"]'
            ])

            # Extraction de l'URL
            url = self._extract_url(element)

            # Extraction du type de contrat
            contract_type = self._extract_contract_type(element, title)

            # Extraction de la description (courte)
            description = self._extract_text(element, [
                '.job-description', '.description', '.summary',
                'p', '.job-summary'
            ])

            # Extraction du salaire
            salary = self._extract_text(element, [
                '.salary', '.wage', '[data-testid="salary"]',
                'span[class*="salary"]', 'span[class*="wage"]'
            ])

            # Construction de l'offre
            offer = {
                'offer_id': offer_id,
                'title': title.strip(),
                'company': company.strip() if company else 'Entreprise non spécifiée',
                'description': description.strip() if description else title.strip(),
                'contract_type': contract_type,
                'location': location.strip() if location else 'France',
                'salary_range': salary.strip() if salary else 'Non spécifié',
                'duration': self._extract_duration(description or title),
                'url': url,
                'reference': f"HW-{offer_id}",
                'source_site': 'HelloWork',
                'source_type': 'emploi',
                'posted_date': datetime.now().strftime('%Y-%m-%d'),
                'scraped_at': datetime.now().isoformat(),
                'raw_html': str(element)[:500]  # Pour debug
            }

            return offer

        except Exception as e:
            logger.error(f"❌ Erreur extraction détails: {e}")
            return None

    def _extract_text(self, element, selectors: List[str]) -> Optional[str]:
        """
        Extrait le texte avec plusieurs sélecteurs possibles
        """
        for selector in selectors:
            try:
                found = element.select_one(selector)
                if found:
                    text = found.get_text(strip=True)
                    if text and len(text) > 2:
                        return text
            except:
                continue
        return None

    def _extract_url(self, element) -> str:
        """
        Extrait l'URL de l'offre
        """
        try:
            # Recherche de liens
            link = element.find('a', href=True)
            if link:
                href = link['href']
                if href.startswith('/'):
                    return urljoin(self.base_url, href)
                elif href.startswith('http'):
                    return href

        except:
            pass

        return f"{self.base_url}/emploi/recherche.html"

    def _extract_contract_type(self, element, title: str) -> str:
        """
        Détermine le type de contrat
        """
        text = f"{element.get_text()} {title}".lower()

        if any(word in text for word in ['apprentage', 'apprenti']):
            return 'Contrat d\'apprentissage'
        elif any(word in text for word in ['alternance', 'alterné']):
            return 'Contrat d\'alternance'
        elif 'stage' in text:
            return 'Stage'
        elif 'cdi' in text:
            return 'CDI'
        elif 'cdd' in text:
            return 'CDD'
        else:
            return 'Contrat d\'alternance'  # Par défaut pour la recherche

    def _extract_duration(self, text: str) -> str:
        """
        Extrait la durée du contrat
        """
        if not text:
            return '24 mois'

        # Recherche de patterns de durée
        duration_patterns = [
            r'(\d+)\s*mois',
            r'(\d+)\s*ans?',
            r'(\d+)\s*années?'
        ]

        for pattern in duration_patterns:
            match = re.search(pattern, text.lower())
            if match:
                num = match.group(1)
                if 'an' in match.group(0):
                    return f"{int(num) * 12} mois"
                else:
                    return f"{num} mois"

        return '24 mois'  # Défaut

    def _is_relevant_offer(self, offer: Dict) -> bool:
        """
        Vérifie si l'offre est pertinente (cybersécurité + alternance)
        """
        text = f"{offer['title']} {offer['description']}".lower()

        # Mots-clés cybersécurité
        cyber_keywords = [
            'cybersécurité', 'cyber', 'sécurité informatique', 'soc',
            'pentest', 'siem', 'firewall', 'intrusion', 'malware',
            'sécurité', 'protection', 'audit sécurité'
        ]

        # Mots-clés alternance
        alternance_keywords = [
            'alternance', 'apprentage', 'apprenti', 'formation'
        ]

        has_cyber = any(keyword in text for keyword in cyber_keywords)
        has_alternance = any(keyword in text for keyword in alternance_keywords)

        # Exclusions
        exclusions = ['stage', 'cdi senior', 'manager', 'directeur']
        has_exclusion = any(exc in text for exc in exclusions)

        is_relevant = has_cyber and (has_alternance or not has_exclusion)

        if is_relevant:
            logger.info(f"✅ Offre pertinente: {offer['title'][:50]}...")
        else:
            logger.debug(f"❌ Offre non pertinente: {offer['title'][:50]}...")

        return is_relevant

def main():
    """
    Fonction principale de test
    """
    print("🕷️ === SCRAPER HELLOWORK - ALTERNANCE CYBERSÉCURITÉ ===")

    scraper = HelloWorkScraper()

    # Recherche des offres
    offers = scraper.search_offers(
        keywords="alternance cybersécurité",
        location="",
        max_pages=2
    )

    print(f"\n📊 === RÉSULTATS ===")
    print(f"Total offres trouvées: {len(offers)}")

    # Affichage des offres
    for i, offer in enumerate(offers, 1):
        print(f"\n🎯 Offre {i}:")
        print(f"  Titre: {offer['title']}")
        print(f"  Entreprise: {offer['company']}")
        print(f"  Contrat: {offer['contract_type']}")
        print(f"  Lieu: {offer['location']}")
        print(f"  URL: {offer['url']}")

    # Sauvegarde JSON pour N8N
    output_file = 'hellowork_offers.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(offers, f, ensure_ascii=False, indent=2)

    print(f"\n💾 Offres sauvegardées dans: {output_file}")

    return offers

if __name__ == "__main__":
    offers = main()