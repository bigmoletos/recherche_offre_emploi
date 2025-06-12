// CLASSIFICATION MISTRAL - FETCH NATIF N8N
// Solution sans node-fetch pour Docker N8N

// Configuration centralisée
const config = {
  apiKey: process.env.MISTRAL_API_KEY || 'fe8GdBIIBwYk8Dj1GvclASPE3j0Zbt95',
  apiUrl: 'https://api.mistral.ai/v1/chat/completions',
  model: 'mistral-small-latest',
  timeout: 30000
};

// Données de l'offre actuelle
const offre = $input.item.json;

console.log(`🤖 === CLASSIFICATION MISTRAL: ${offre.title} ===`);
console.log('🏢 Entreprise:', offre.company);
console.log('📍 Localisation:', offre.location);

// Prompt optimisé pour la classification
const prompt = `Analyse cette offre d'emploi :

Titre: ${offre.title}
Entreprise: ${offre.company}
Description: ${offre.description || 'Non spécifiée'}

Cette offre correspond-elle à une ALTERNANCE en CYBERSÉCURITÉ ?

Critères :
- Doit être une alternance (pas un stage ou CDI)
- Doit être liée à la cybersécurité, sécurité informatique, SOC, pentest, audit sécurité

Réponds uniquement par: VALIDE ou INVALIDE`;

// Payload Mistral
const payload = {
  model: config.model,
  messages: [
    {
      role: "user",
      content: prompt
    }
  ],
  temperature: 0.1,
  max_tokens: 100
};

console.log('📦 Payload Mistral préparé');
console.log('📏 Taille prompt:', prompt.length, 'caractères');

try {
  // Test si fetch global est disponible
  if (typeof fetch === 'undefined') {
    console.log('❌ fetch global non disponible - test alternatives...');

    // Alternative 1: Essayer avec globalThis
    if (typeof globalThis.fetch !== 'undefined') {
      console.log('✅ globalThis.fetch trouvé');
      var fetchFn = globalThis.fetch;
    } else {
      console.log('❌ Aucune méthode fetch disponible');
      return {
        json: {
          ...offre,
          mistral_response: 'ERREUR_FETCH_UNAVAILABLE',
          classification: 'ERREUR',
          is_valid: false,
          confidence: 0,
          error: 'Fetch API non disponible dans cet environnement N8N',
          processed_at: new Date().toISOString()
        }
      };
    }
  } else {
    console.log('✅ fetch global disponible');
    var fetchFn = fetch;
  }

  // Appel API Mistral avec fetch natif
  console.log('🌐 Appel API Mistral avec fetch natif...');

  const response = await fetchFn(config.apiUrl, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${config.apiKey}`
    },
    body: JSON.stringify(payload)
  });

  console.log('📊 Status HTTP:', response.status);

  if (!response.ok) {
    const errorText = await response.text();
    console.log('❌ Erreur API:', response.status, errorText);

    return {
      json: {
        ...offre,
        mistral_response: 'ERREUR_API',
        classification: 'ERREUR',
        is_valid: false,
        confidence: 0,
        error: `HTTP ${response.status}: ${errorText}`,
        processed_at: new Date().toISOString()
      }
    };
  }

  // Parse de la réponse
  const data = await response.json();
  console.log('📥 Réponse reçue');

  if (data && data.choices && data.choices[0] && data.choices[0].message && data.choices[0].message.content) {
    const content = data.choices[0].message.content.trim();

    console.log('✅ === MISTRAL SUCCESS ===');
    console.log('📝 Réponse brute:', content);

    // Classification intelligente
    const contentUpper = content.toUpperCase();
    let classification, isValid, confidence;

    if (contentUpper.includes('VALIDE') && !contentUpper.includes('INVALIDE')) {
      classification = 'VALIDE';
      isValid = true;
      confidence = 0.9;
      console.log('✅ Offre VALIDÉE');
    } else if (contentUpper.includes('INVALIDE')) {
      classification = 'INVALIDE';
      isValid = false;
      confidence = 0.9;
      console.log('❌ Offre REJETÉE');
    } else {
      // Réponse ambiguë
      classification = 'INCERTAIN';
      isValid = false;
      confidence = 0.3;
      console.log('⚠️ Réponse ambiguë');
    }

    console.log('🎯 Classification finale:', classification);
    console.log('📊 Usage tokens:', JSON.stringify(data.usage || {}));

    // Retour enrichi
    return {
      json: {
        ...offre,
        mistral_response: content,
        classification: classification,
        is_valid: isValid,
        confidence: confidence,
        model_used: data.model || config.model,
        usage: data.usage || {},
        processed_at: new Date().toISOString(),
        method: 'native_fetch_production'
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
        processed_at: new Date().toISOString()
      }
    };
  }

} catch (error) {
  console.log('🚨 === ERREUR CRITIQUE ===');
  console.log('Type:', error.constructor.name);
  console.log('Message:', error.message);
  console.log('Stack:', error.stack);

  return {
    json: {
      ...offre,
      mistral_response: 'ERREUR_RESEAU',
      classification: 'ERREUR',
      is_valid: false,
      confidence: 0,
      error: `${error.constructor.name}: ${error.message}`,
      processed_at: new Date().toISOString()
    }
  };
}