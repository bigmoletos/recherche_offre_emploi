// CLASSIFICATION MISTRAL - VERSION OPTIMISÉE
// Améliorations : retry logic, rate limiting, prompt amélioré

const fetch = require('node-fetch');

// Configuration avancée
const config = {
  apiKey: process.env.MISTRAL_API_KEY || 'fe8GdBIIBwYk8Dj1GvclASPE3j0Zbt95',
  apiUrl: 'https://api.mistral.ai/v1/chat/completions',
  model: 'mistral-small-latest',
  timeout: 30000,
  maxRetries: 2,
  retryDelay: 1000
};

// Fonction utilitaire pour retry
async function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

// Données de l'offre actuelle
const offre = $input.item.json;

console.log(`🤖 === CLASSIFICATION MISTRAL: ${offre.title} ===`);
console.log('🏢 Entreprise:', offre.company);
console.log('📍 Localisation:', offre.location);

// Prompt optimisé avec exemples
const prompt = `Tu es un expert en classification d'offres d'emploi en cybersécurité.

OFFRE À ANALYSER:
Titre: ${offre.title}
Entreprise: ${offre.company}
Localisation: ${offre.location}
Description: ${offre.description || 'Non spécifiée'}

QUESTION: Cette offre correspond-elle exactement à une ALTERNANCE en CYBERSÉCURITÉ ?

CRITÈRES OBLIGATOIRES:
✓ Type de contrat: ALTERNANCE (pas stage, CDI, CDD, freelance)
✓ Domaine: Cybersécurité, sécurité informatique, SOC, pentest, audit sécurité, RSSI

EXEMPLES:
- "Alternance SOC Analyst" → VALIDE
- "Stage cybersécurité" → INVALIDE (pas alternance)
- "CDI développeur sécurité" → INVALIDE (pas alternance)
- "Alternance marketing" → INVALIDE (pas cybersécurité)

RÉPONSE STRICTE: VALIDE ou INVALIDE`;

// Payload Mistral optimisé
const payload = {
  model: config.model,
  messages: [
    {
      role: "system",
      content: "Tu es un classificateur expert. Réponds uniquement par VALIDE ou INVALIDE."
    },
    {
      role: "user",
      content: prompt
    }
  ],
  temperature: 0.05, // Plus déterministe
  max_tokens: 50,    // Plus économique
  top_p: 0.1        // Plus focalisé
};

console.log('📦 Payload Mistral optimisé');
console.log('📏 Taille prompt:', prompt.length, 'caractères');

// Fonction d'appel API avec retry
async function callMistralWithRetry(payload, retries = 0) {
  try {
    console.log(`🌐 Appel API Mistral (tentative ${retries + 1})...`);

    const response = await fetch(config.apiUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${config.apiKey}`,
        'User-Agent': 'N8N-Docker-Agent/1.0'
      },
      body: JSON.stringify(payload),
      timeout: config.timeout
    });

    console.log('📊 Status HTTP:', response.status);

    // Gestion des erreurs de rate limit
    if (response.status === 429 && retries < config.maxRetries) {
      const retryAfter = response.headers.get('retry-after') || config.retryDelay;
      console.log(`⏳ Rate limit - retry dans ${retryAfter}ms`);
      await sleep(parseInt(retryAfter));
      return callMistralWithRetry(payload, retries + 1);
    }

    // Gestion des erreurs serveur temporaires
    if (response.status >= 500 && retries < config.maxRetries) {
      console.log(`🔄 Erreur serveur ${response.status} - retry dans ${config.retryDelay}ms`);
      await sleep(config.retryDelay * (retries + 1)); // Backoff exponentiel
      return callMistralWithRetry(payload, retries + 1);
    }

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`HTTP ${response.status}: ${errorText}`);
    }

    return await response.json();

  } catch (error) {
    if (retries < config.maxRetries && (error.code === 'ECONNRESET' || error.code === 'ETIMEDOUT')) {
      console.log(`🔄 Erreur réseau ${error.code} - retry dans ${config.retryDelay}ms`);
      await sleep(config.retryDelay * (retries + 1));
      return callMistralWithRetry(payload, retries + 1);
    }
    throw error;
  }
}

try {
  // Appel API avec retry automatique
  const data = await callMistralWithRetry(payload);
  console.log('📥 Réponse reçue');

  if (data && data.choices && data.choices[0] && data.choices[0].message && data.choices[0].message.content) {
    const content = data.choices[0].message.content.trim();

    console.log('✅ === MISTRAL SUCCESS ===');
    console.log('📝 Réponse brute:', content);

    // Classification améliorée avec patterns
    const contentUpper = content.toUpperCase();
    let classification, isValid, confidence;

    // Patterns de détection plus précis
    const validePatterns = ['VALIDE', 'VALID', 'OUI', 'YES', 'ACCEPTÉ'];
    const invalidePatterns = ['INVALIDE', 'INVALID', 'NON', 'NO', 'REJETÉ'];

    const hasValide = validePatterns.some(pattern => contentUpper.includes(pattern));
    const hasInvalide = invalidePatterns.some(pattern => contentUpper.includes(pattern));

    if (hasValide && !hasInvalide) {
      classification = 'VALIDE';
      isValid = true;
      confidence = 0.95;
      console.log('✅ Offre VALIDÉE');
    } else if (hasInvalide) {
      classification = 'INVALIDE';
      isValid = false;
      confidence = 0.95;
      console.log('❌ Offre REJETÉE');
    } else {
      // Analyse secondaire sur le contenu
      const cybersecurityTerms = ['CYBER', 'SECURITE', 'SOC', 'PENTEST', 'AUDIT'];
      const alternanceTerms = ['ALTERNANCE', 'APPRENTISSAGE'];

      const hasCyber = cybersecurityTerms.some(term =>
        offre.title.toUpperCase().includes(term) ||
        (offre.description && offre.description.toUpperCase().includes(term))
      );
      const hasAlternance = alternanceTerms.some(term =>
        offre.title.toUpperCase().includes(term)
      );

      if (hasCyber && hasAlternance) {
        classification = 'VALIDE_PROBABLE';
        isValid = true;
        confidence = 0.7;
        console.log('✅ Offre VALIDÉE (analyse secondaire)');
      } else {
        classification = 'INCERTAIN';
        isValid = false;
        confidence = 0.3;
        console.log('⚠️ Réponse ambiguë');
      }
    }

    console.log('🎯 Classification finale:', classification);
    console.log('📊 Confidence:', confidence);
    console.log('📊 Usage tokens:', JSON.stringify(data.usage || {}));

    // Retour enrichi avec métadonnées
    return {
      json: {
        ...offre,
        mistral_response: content,
        classification: classification,
        is_valid: isValid,
        confidence: confidence,
        model_used: data.model || config.model,
        usage: data.usage || {},
        processing_time: Date.now() - startTime,
        processed_at: new Date().toISOString(),
        method: 'node_code_optimized',
        version: '2.0'
      }
    };

  } else {
    console.log('❌ Structure réponse Mistral invalide');
    console.log('🔍 Clés trouvées:', Object.keys(data || {}));

    return {
      json: {
        ...offre,
        mistral_response: 'STRUCTURE_INVALIDE',
        classification: 'ERREUR',
        is_valid: false,
        confidence: 0,
        error: 'Structure réponse Mistral invalide',
        received_data: data,
        processed_at: new Date().toISOString(),
        method: 'node_code_optimized'
      }
    };
  }

} catch (error) {
  console.log('🚨 === ERREUR CRITIQUE ===');
  console.log('Type:', error.constructor.name);
  console.log('Message:', error.message);

  return {
    json: {
      ...offre,
      mistral_response: 'ERREUR_RESEAU',
      classification: 'ERREUR',
      is_valid: false,
      confidence: 0,
      error: `${error.constructor.name}: ${error.message}`,
      processed_at: new Date().toISOString(),
      method: 'node_code_optimized'
    }
  };
}

// Mesure du temps de traitement
const startTime = Date.now();