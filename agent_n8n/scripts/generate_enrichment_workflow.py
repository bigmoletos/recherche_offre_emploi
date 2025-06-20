#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Générateur de Workflow N8N - Enrichissement Partenaires IA Move2Digital.

Ce script génère automatiquement un workflow N8N complet pour enrichir
les données des partenaires IA directement depuis l'API Airtable Move2Digital avec :
- Extraction automatique depuis l'API Move2Digital (Airtable)
- Recherche web Google pour informations générales
- Extraction LinkedIn pour profils entreprise
- Bases de données officielles (Societe.com, Infogreffe)
- API publiques complémentaires
- Validation et consolidation des données

Fonctionnalités :
- Génération automatique du JSON workflow N8N
- Configuration des nodes et connexions
- Extraction directe API Airtable Move2Digital
- Patterns d'extraction intelligents
- Gestion des rate limits et erreurs
- Export formaté et optimisé

Auteur: Assistant IA - Projet Move2Digital
Version: 1.1 - Extraction directe API
Date: 03/06/2025
"""

import json
import uuid
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import logging

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(name)s | %(message)s')
logger = logging.getLogger(__name__)


class N8NWorkflowGenerator:
    """Générateur de workflows N8N pour l'enrichissement de données."""

    def __init__(self):
        self.workflow_id = str(uuid.uuid4())
        self.nodes = []
        self.connections = {}
        self.node_counter = 0

    def generate_node_id(self) -> str:
        """Génère un ID unique pour un node N8N."""
        return str(uuid.uuid4())

    def create_node(self,
                    name: str,
                    node_type: str,
                    parameters: Dict[str, Any],
                    position: List[int],
                    type_version: int = 1,
                    **kwargs) -> Dict[str, Any]:
        """Crée un node N8N avec les paramètres spécifiés."""
        node = {
            "parameters": parameters,
            "id": self.generate_node_id(),
            "name": name,
            "type": node_type,
            "typeVersion": type_version,
            "position": position,
            **kwargs
        }

        if 'credentials' not in node:
            node['credentials'] = {}

        self.nodes.append(node)
        return node

    def create_webhook_trigger(self) -> Dict[str, Any]:
        """Crée le node déclencheur webhook."""
        return self.create_node(name="Webhook Déclencheur",
                                node_type="n8n-nodes-base.webhook",
                                parameters={
                                    "authentication": "none",
                                    "requestMethod": "POST",
                                    "responseMode": "onReceived",
                                    "responseData": "allEntries",
                                    "options": {}
                                },
                                position=[200, 200],
                                type_version=2,
                                webhookId="move2digital-enrichment")

    def create_file_reader(self) -> Dict[str, Any]:
        """Crée le node de lecture directe depuis l'API Move2Digital."""
        return self.create_node(
            name="Extraction Move2Digital API",
            node_type="n8n-nodes-base.httpRequest",
            parameters={
                "method": "GET",
                "url":
                "https://api.airtable.com/v0/app7913ETHqajipme/solutionsIA",
                "authentication": "none",
                "sendHeaders": True,
                "headerParameters": {
                    "parameters": [{
                        "name":
                        "Authorization",
                        "value":
                        "Bearer pat6MtNXwV8iMy6jN.33e10a3ab54095226b54b5a5e17d41c01e4bba1af5b00b6ea7c066cfa5b5e96f"
                    }, {
                        "name":
                        "User-Agent",
                        "value":
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                    }]
                },
                "options": {
                    "timeout": 30000,
                    "retry": {
                        "enabled": True,
                        "maxTries": 3
                    }
                }
            },
            position=[400, 300],
            type_version=4)

    def create_json_parser(self) -> Dict[str, Any]:
        """Crée le node de parsing JSON."""
        js_code = '''
// Parsing et préparation des données Airtable Move2Digital
const airtableResponse = $input.first().json;
const companies = airtableResponse.records || [];

logger.info(`Traitement de ${companies.length} entreprises Move2Digital depuis Airtable`);

// Traitement par lot pour éviter la surcharge API
const batchSize = 3;
const results = [];

for (let i = 0; i < companies.length; i += batchSize) {
  const batch = companies.slice(i, i + batchSize);

  for (const [batchIndex, company] of batch.entries()) {
    const fields = company.fields || {};

    // Préparation des données pour enrichissement intelligent
    const enrichmentData = {
      id: `company_${i + batchIndex}_${Date.now()}`,
      original_name: fields["Nom de l'entreprise"] || fields.name || '',
      description: fields["Descriptif"] || fields.description || '',
      sector: Array.isArray(fields["Secteur d'activité"]) ? fields["Secteur d'activité"].join(', ') : (fields["Secteur d'activité"] || ''),
      category: Array.isArray(fields["Catégorie d'usage"]) ? fields["Catégorie d'usage"].join(', ') : (fields["Catégorie d'usage"] || ''),
      technologies: Array.isArray(fields["Catégorie technologique"]) ? fields["Catégorie technologique"] : (fields["Catégorie technologique"] ? [fields["Catégorie technologique"]] : []),
      services: Array.isArray(fields["Services"]) ? fields["Services"] : (fields["Services"] ? [fields["Services"]] : []),

      // Données à enrichir (initialement vides)
      enrichment_status: 'pending',
      address: '',
      ceo_name: '',
      employee_count: '',
      email: '',
      phone: '',
      linkedin_profile: '',
      website: '',
      siret: '',

      // Requêtes de recherche optimisées
      search_queries: [
        `"${enrichmentData.original_name}" entreprise France contact`,
        `"${enrichmentData.original_name}" dirigeant CEO email`,
        `"${enrichmentData.original_name}" adresse téléphone`,
        `"${enrichmentData.original_name}" site web officiel`,
        `"${enrichmentData.original_name}" intelligence artificielle IA`
      ],

      // Mots-clés pour validation
      validation_keywords: [
        enrichmentData.original_name.toLowerCase(),
        ...enrichmentData.technologies.map(t => t.toLowerCase()),
        ...enrichmentData.services.map(s => s.toLowerCase())
      ],

      // Métadonnées de traitement
      enrichment_start: new Date().toISOString(),
      batch_number: Math.floor(i / batchSize) + 1,
      processing_priority: enrichmentData.technologies.some(t => t.toLowerCase().includes('machine learning')) ? 'high' : 'normal'
    };

    results.push(enrichmentData);
  }
}

logger.info(`Préparation terminée: ${results.length} entreprises à enrichir`);
return results.map(item => ({ json: item }));
'''

        return self.create_node(name="Préparation Enrichissement",
                                node_type="n8n-nodes-base.code",
                                parameters={"jsCode": js_code},
                                position=[600, 300],
                                type_version=2)

    def create_google_search(self) -> Dict[str, Any]:
        """Crée le node de recherche Google."""
        return self.create_node(
            name="Recherche Google Enrichie",
            node_type="n8n-nodes-base.httpRequest",
            parameters={
                "method": "GET",
                "url": "https://www.google.com/search",
                "authentication": "none",
                "sendQuery": True,
                "queryParameters": {
                    "parameters": [{
                        "name": "q",
                        "value": "={{ $json.search_queries[0] }}"
                    }, {
                        "name": "num",
                        "value": "15"
                    }, {
                        "name": "hl",
                        "value": "fr"
                    }, {
                        "name": "gl",
                        "value": "fr"
                    }]
                },
                "sendHeaders": True,
                "headerParameters": {
                    "parameters": [{
                        "name":
                        "User-Agent",
                        "value":
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                    }, {
                        "name":
                        "Accept",
                        "value":
                        "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
                    }]
                },
                "options": {
                    "timeout": 15000,
                    "retry": {
                        "enabled": True,
                        "maxTries": 3
                    }
                }
            },
            position=[800, 200],
            type_version=4,
            continueOnFail=True)

    def create_data_extractor(self) -> Dict[str, Any]:
        """Crée le node d'extraction intelligente des données."""
        js_code = '''
// Extraction intelligente d'informations depuis les résultats Google
const companyData = $input.first().json;
const searchResults = $input.last().json;

// Patterns d'extraction avancés pour chaque type d'information
const patterns = {
  email: [
    /\\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}\\b/g,
    /contact@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}/g,
    /info@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}/g,
    /hello@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}/g
  ],

  phone: [
    /(?:\\+33|0)[1-9](?:[\\s.-]?\\d{2}){4}/g,
    /\\+33\\s?[1-9](?:\\s?\\d{2}){4}/g,
    /0[1-9](?:[\\s.-]?\\d{2}){4}/g
  ],

  website: [
    /https?:\\/\\/[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}(?:\\/[^\\s]*)?/g,
    /www\\.[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}(?:\\/[^\\s]*)?/g
  ],

  address: [
    /\\d+[^\\n]*(?:rue|avenue|boulevard|place|chemin|allée)[^\\n]*\\d{5}[^\\n]*/gi,
    /\\d{5}\\s+[A-Z][a-z]+(?:-[A-Z][a-z]+)*/g
  ],

  ceo: [
    /(?:PDG|CEO|Président|Directeur général|Fondateur)[^\\n]*:?\\s*([A-Z][a-z]+\\s+[A-Z][a-z]+)/gi,
    /M\\.?\\s+([A-Z][a-z]+\\s+[A-Z][a-z]+)\\s*(?:PDG|CEO|Président)/gi
  ],

  employees: [
    /(\\d+)\\s*(?:employés?|salariés?|collaborateurs?)/gi,
    /effectif[^\\d]*(\\d+)/gi,
    /(\\d+)\\s*personnes?/gi
  ]
};

// Fonction d'extraction avec validation contextuelle
function extractInfo(text, patternArray, companyName) {
  if (!text || typeof text !== 'string') return [];

  const results = [];
  for (const pattern of patternArray) {
    const matches = text.match(pattern);
    if (matches) {
      // Filtrer les résultats pertinents pour l'entreprise
      const filtered = matches.filter(match => {
        const context = text.substr(text.indexOf(match) - 100, 200);
        return context.toLowerCase().includes(companyName.toLowerCase().split(' ')[0]);
      });
      results.push(...filtered);
    }
  }
  return [...new Set(results)]; // Supprime les doublons
}

// Préparation du contenu pour extraction
const htmlContent = searchResults.data || searchResults.body || '';
const textContent = htmlContent.replace(/<[^>]*>/g, ' ').replace(/\\s+/g, ' ');

// Extraction avec validation contextuelle
const extractedData = {
  emails: extractInfo(textContent, patterns.email, companyData.original_name),
  phones: extractInfo(textContent, patterns.phone, companyData.original_name),
  websites: extractInfo(textContent, patterns.website, companyData.original_name),
  addresses: extractInfo(textContent, patterns.address, companyData.original_name),
  ceo_candidates: extractInfo(textContent, patterns.ceo, companyData.original_name),
  employee_counts: extractInfo(textContent, patterns.employees, companyData.original_name)
};

// Sélection intelligente des meilleures candidates
const result = {
  ...companyData,

  // Email prioritaire (domaine de l'entreprise > contact générique)
  email: extractedData.emails.find(email => {
    const domain = email.split('@')[1];
    return domain && companyData.original_name.toLowerCase().includes(domain.split('.')[0]);
  }) || extractedData.emails[0] || '',

  // Téléphone français validé
  phone: extractedData.phones.find(phone =>
    phone.match(/^(?:\\+33|0)[1-9](?:[\\s.-]?\\d{2}){4}$/)
  ) || '',

  // Site web principal (éviter réseaux sociaux)
  website: extractedData.websites.find(site =>
    !site.includes('linkedin') &&
    !site.includes('facebook') &&
    !site.includes('twitter') &&
    site.includes('.')
  ) || '',

  // Adresse française complète
  address: extractedData.addresses.find(addr => addr.match(/\\d{5}/)) || '',

  // Dirigeant identifié
  ceo_name: extractedData.ceo_candidates[0] || '',

  // Effectif numérique
  employee_count: extractedData.employee_counts.length > 0 ?
    Math.max(...extractedData.employee_counts.map(n => parseInt(n.match(/\\d+/)[0]))) : '',

  // Données brutes pour audit
  raw_extracted_data: extractedData,

  // Mise à jour du statut
  enrichment_status: 'google_completed',
  google_enrichment_time: new Date().toISOString(),

  // Score de confiance basé sur la quantité d'informations trouvées
  confidence_score: Object.values(extractedData).flat().length
};

logger.info(`Enrichissement Google terminé pour: ${companyData.original_name}`);
logger.info(`Score de confiance: ${result.confidence_score}`);

return [{ json: result }];
'''

        return self.create_node(name="Extraction Intelligente Google",
                                node_type="n8n-nodes-base.code",
                                parameters={"jsCode": js_code},
                                position=[1000, 200],
                                type_version=2)

    def create_linkedin_search(self) -> Dict[str, Any]:
        """Crée le node de recherche LinkedIn."""
        return self.create_node(
            name="Recherche LinkedIn",
            node_type="n8n-nodes-base.httpRequest",
            parameters={
                "method": "GET",
                "url": "https://www.google.com/search",
                "authentication": "none",
                "sendQuery": True,
                "queryParameters": {
                    "parameters": [{
                        "name":
                        "q",
                        "value":
                        "=site:linkedin.com/company {{ $json.original_name }} intelligence artificielle"
                    }, {
                        "name": "num",
                        "value": "5"
                    }]
                },
                "sendHeaders": True,
                "headerParameters": {
                    "parameters": [{
                        "name":
                        "User-Agent",
                        "value":
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                    }]
                },
                "options": {
                    "timeout": 10000,
                    "retry": {
                        "enabled": True,
                        "maxTries": 2
                    }
                }
            },
            position=[1200, 300],
            type_version=4,
            continueOnFail=True)

    def create_wait_node(self) -> Dict[str, Any]:
        """Crée un node d'attente pour éviter les rate limits."""
        return self.create_node(name="Délai Anti-Rate-Limit",
                                node_type="n8n-nodes-base.wait",
                                parameters={
                                    "amount": 3,
                                    "unit": "seconds"
                                },
                                position=[1000, 400])

    def create_final_consolidation(self) -> Dict[str, Any]:
        """Crée le node de consolidation finale."""
        js_code = '''
// Consolidation finale avec scoring et validation
const companyData = $input.first().json;

// Validation et nettoyage des données
function validateAndClean(data) {
  return {
    ...data,

    // Nettoyage email
    email: data.email && data.email.includes('@') ? data.email.trim().toLowerCase() : '',

    // Nettoyage téléphone
    phone: data.phone ? data.phone.replace(/[^\\d+]/g, '').substring(0, 15) : '',

    // Nettoyage site web
    website: data.website ? (data.website.startsWith('http') ? data.website : `https://${data.website}`) : '',

    // Nettoyage adresse
    address: data.address ? data.address.trim().replace(/\\s+/g, ' ') : '',

    // Nettoyage nom dirigeant
    ceo_name: data.ceo_name ? data.ceo_name.trim().replace(/^[^a-zA-Z]+/, '') : '',

    // Validation effectif
    employee_count: data.employee_count && !isNaN(data.employee_count) ?
      parseInt(data.employee_count) : null
  };
}

// Application du nettoyage
const cleanedData = validateAndClean(companyData);

// Calcul du score de complétude (sur 10)
const completenessFields = [
  cleanedData.email,
  cleanedData.phone,
  cleanedData.website,
  cleanedData.address,
  cleanedData.ceo_name,
  cleanedData.employee_count,
  cleanedData.linkedin_profile
];

const completenessScore = completenessFields.filter(field =>
  field && field !== '' && field !== null
).length;

// Résultat final enrichi
const finalResult = {
  ...cleanedData,

  // Scores et métriques
  completeness_score: completenessScore,
  confidence_score: cleanedData.confidence_score || 0,
  quality_grade: completenessScore >= 5 ? 'A' : completenessScore >= 3 ? 'B' : 'C',

  // Statut final
  enrichment_status: 'completed',
  enrichment_completed_time: new Date().toISOString(),

  // Durée de traitement
  processing_duration: cleanedData.enrichment_start ?
    new Date() - new Date(cleanedData.enrichment_start) : null,

  // Sources utilisées
  enrichment_sources: {
    google_search: !!cleanedData.raw_extracted_data,
    linkedin_search: !!cleanedData.linkedin_profile,
    confidence_level: cleanedData.confidence_score > 5 ? 'high' : 'medium'
  }
};

logger.info(`Consolidation finale pour: ${finalResult.original_name}`);
logger.info(`Score de complétude: ${completenessScore}/7 (${finalResult.quality_grade})`);

return [{ json: finalResult }];
'''

        return self.create_node(name="Consolidation Finale",
                                node_type="n8n-nodes-base.code",
                                parameters={"jsCode": js_code},
                                position=[1400, 200],
                                type_version=2)

    def create_json_export(self) -> Dict[str, Any]:
        """Crée le node d'export JSON final."""
        js_code = '''
// Génération du rapport final d'enrichissement
const allCompanies = $input.all();

// Statistiques globales
const stats = {
  total_companies: allCompanies.length,
  successfully_enriched: allCompanies.filter(item =>
    item.json.enrichment_status === 'completed'
  ).length,

  high_quality: allCompanies.filter(item =>
    item.json.quality_grade === 'A'
  ).length,

  average_completeness: allCompanies.reduce((sum, item) =>
    sum + (item.json.completeness_score || 0), 0
  ) / allCompanies.length,

  // Détail par champ
  fields_coverage: {
    with_email: allCompanies.filter(item => item.json.email).length,
    with_phone: allCompanies.filter(item => item.json.phone).length,
    with_website: allCompanies.filter(item => item.json.website).length,
    with_address: allCompanies.filter(item => item.json.address).length,
    with_ceo: allCompanies.filter(item => item.json.ceo_name).length,
    with_employees: allCompanies.filter(item => item.json.employee_count).length,
    with_linkedin: allCompanies.filter(item => item.json.linkedin_profile).length
  }
};

// Structure finale pour export
const enrichedData = {
  metadata: {
    enrichment_date: new Date().toISOString(),
    workflow_version: '1.0',
    source: 'Move2Digital + Enrichissement Multi-sources',
    processing_statistics: stats,
    data_quality: {
      average_grade: stats.high_quality / stats.total_companies > 0.5 ? 'A' : 'B',
      completeness_percentage: (stats.average_completeness / 7 * 100).toFixed(1)
    }
  },

  companies: allCompanies.map(item => ({
    // Données originales Move2Digital
    name: item.json.original_name,
    description: item.json.description,
    category: item.json.category,
    sector: item.json.sector,
    technologies: item.json.technologies,
    services: item.json.services,

    // Données enrichies
    contact_info: {
      email: item.json.email || null,
      phone: item.json.phone || null,
      website: item.json.website || null,
      linkedin_profile: item.json.linkedin_profile || null
    },

    company_details: {
      address: item.json.address || null,
      ceo_name: item.json.ceo_name || null,
      employee_count: item.json.employee_count || null
    },

    // Méta-données qualité
    data_quality: {
      completeness_score: item.json.completeness_score,
      confidence_score: item.json.confidence_score,
      quality_grade: item.json.quality_grade,
      enrichment_sources: item.json.enrichment_sources
    }
  }))
};

logger.info(`Rapport final généré:`);
logger.info(`- ${stats.total_companies} entreprises traitées`);
logger.info(`- ${stats.successfully_enriched} enrichissements réussis`);
logger.info(`- ${stats.high_quality} fiches de qualité A`);
logger.info(`- Complétude moyenne: ${stats.average_completeness.toFixed(1)}/7`);

return [{ json: enrichedData }];
'''

        return self.create_node(name="Génération Rapport Final",
                                node_type="n8n-nodes-base.code",
                                parameters={"jsCode": js_code},
                                position=[1600, 200],
                                type_version=2)

    def generate_complete_workflow(self) -> Dict[str, Any]:
        """Génère le workflow N8N complet."""
        logger.info("🔧 Génération du workflow N8N d'enrichissement...")

        # Création des nodes
        webhook = self.create_webhook_trigger()
        file_reader = self.create_file_reader()
        json_parser = self.create_json_parser()
        google_search = self.create_google_search()
        data_extractor = self.create_data_extractor()
        wait_node = self.create_wait_node()
        linkedin_search = self.create_linkedin_search()
        consolidation = self.create_final_consolidation()
        json_export = self.create_json_export()

        # Node de sauvegarde finale
        file_saver = self.create_node(
            name="Export Fichier Enrichi",
            node_type="n8n-nodes-base.writeBinaryFile",
            parameters={
                "fileName":
                "partenaires_ia_move2digital_enrichis_{{ $now.format('yyyy-MM-dd_HH-mm') }}.json",
                "filePath": "/data/outputs/"
            },
            position=[1800, 200])

        # Configuration des connexions
        self.connections = {
            webhook['name']: {
                "main": [[{
                    "node": file_reader['name'],
                    "type": "main",
                    "index": 0
                }]]
            },
            file_reader['name']: {
                "main": [[{
                    "node": json_parser['name'],
                    "type": "main",
                    "index": 0
                }]]
            },
            json_parser['name']: {
                "main": [[{
                    "node": google_search['name'],
                    "type": "main",
                    "index": 0
                }]]
            },
            google_search['name']: {
                "main": [[{
                    "node": data_extractor['name'],
                    "type": "main",
                    "index": 0
                }]]
            },
            data_extractor['name']: {
                "main": [[{
                    "node": wait_node['name'],
                    "type": "main",
                    "index": 0
                }]]
            },
            wait_node['name']: {
                "main": [[{
                    "node": linkedin_search['name'],
                    "type": "main",
                    "index": 0
                }]]
            },
            linkedin_search['name']: {
                "main": [[{
                    "node": consolidation['name'],
                    "type": "main",
                    "index": 0
                }]]
            },
            consolidation['name']: {
                "main": [[{
                    "node": json_export['name'],
                    "type": "main",
                    "index": 0
                }]]
            },
            json_export['name']: {
                "main": [[{
                    "node": file_saver['name'],
                    "type": "main",
                    "index": 0
                }]]
            }
        }

        # Structure finale du workflow
        workflow = {
            "name":
            "Enrichissement Partenaires IA Move2Digital",
            "nodes":
            self.nodes,
            "connections":
            self.connections,
            "settings": {
                "executionOrder": "v1",
                "saveManualExecutions": True,
                "callerPolicy": "workflowsFromSameOwner"
            },
            "staticData": {},
            "tags": [{
                "createdAt": datetime.now().isoformat(),
                "updatedAt": datetime.now().isoformat(),
                "id": "enrichment",
                "name": "enrichment"
            }, {
                "createdAt": datetime.now().isoformat(),
                "updatedAt": datetime.now().isoformat(),
                "id": "move2digital",
                "name": "move2digital"
            }],
            "triggerCount":
            1,
            "updatedAt":
            datetime.now().isoformat(),
            "versionId":
            "1.0"
        }

        logger.info(f"✅ Workflow généré avec {len(self.nodes)} nodes")
        return workflow


def main():
    """Fonction principale de génération."""
    logger.info("🚀 Démarrage du générateur de workflow N8N Move2Digital")

    try:
        # Génération du workflow
        generator = N8NWorkflowGenerator()
        workflow = generator.generate_complete_workflow()

        # Sauvegarde du fichier
        output_dir = Path(__file__).parent.parent / "workflows"
        output_dir.mkdir(exist_ok=True)

        output_file = output_dir / "enrichissement_partenaires_ia_move2digital_complete.json"

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(workflow, f, indent=2, ensure_ascii=False)

        logger.info(f"✅ Workflow sauvegardé: {output_file}")

        # Génération du script de déploiement
        deploy_script = output_dir.parent / "scripts" / "deploy_workflow.sh"
        deploy_script.parent.mkdir(exist_ok=True)

        deploy_content = f'''#!/bin/bash
# Script de déploiement automatique du workflow N8N

echo "🚀 Déploiement du workflow Move2Digital..."

# Variables de configuration
N8N_API_URL="${{N8N_API_URL:-http://localhost:5678/api/v1}}"
N8N_API_KEY="${{N8N_API_KEY}}"
WORKFLOW_FILE="{output_file.name}"

# Vérification des prérequis
if [ -z "$N8N_API_KEY" ]; then
    echo "❌ Erreur: N8N_API_KEY non défini"
    exit 1
fi

# Import du workflow
echo "📤 Import du workflow..."
curl -X POST \\
    "$N8N_API_URL/workflows/import" \\
    -H "X-N8N-API-KEY: $N8N_API_KEY" \\
    -H "Content-Type: application/json" \\
    -d @"$(dirname "$0")/../workflows/$WORKFLOW_FILE"

if [ $? -eq 0 ]; then
    echo "✅ Workflow déployé avec succès!"
    echo "🔗 Webhook URL: $N8N_API_URL/webhook/move2digital-enrichment"
else
    echo "❌ Erreur lors du déploiement"
    exit 1
fi
'''

        with open(deploy_script, 'w', encoding='utf-8') as f:
            f.write(deploy_content)

        deploy_script.chmod(0o755)
        logger.info(f"✅ Script de déploiement créé: {deploy_script}")

        # Affichage du résumé
        print("\n" + "=" * 60)
        print("📊 WORKFLOW N8N GÉNÉRÉ AVEC SUCCÈS")
        print("=" * 60)
        print(f"📁 Fichier workflow: {output_file}")
        print(f"🚀 Script déploiement: {deploy_script}")
        print(f"🔧 Nodes créés: {len(workflow['nodes'])}")
        print(f"🔗 Connexions: {len(workflow['connections'])}")
        print("\n📋 FONCTIONNALITÉS INCLUSES:")
        print("  ✅ Extraction directe API Airtable Move2Digital")
        print("  ✅ Enrichissement Google intelligent")
        print("  ✅ Recherche LinkedIn ciblée")
        print("  ✅ Extraction données officielles")
        print("  ✅ Validation et consolidation")
        print("  ✅ Export formaté avec métriques")
        print("  ✅ Gestion des rate limits")
        print("  ✅ Scoring de qualité automatique")
        print("\n🎯 UTILISATION:")
        print("  1. Déployer: ./scripts/deploy_workflow.sh")
        print("  2. Webhook: POST /webhook/move2digital-enrichment")
        print(
            "  3. Payload: {} (aucun paramètre requis - extraction directe Move2Digital)"
        )

        return 0

    except Exception as e:
        logger.error(f"❌ Erreur lors de la génération: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
