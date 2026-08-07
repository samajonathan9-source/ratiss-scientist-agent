// Cœur logique léger de RATISS

const RATISS_SYSTEM_PROMPT = `Tu es RATISS (Réseau Artificiel Topologique d'Intégration Systémique Souverain V9 Aeon Prime), un moteur cognitif d'élite créé par JohnKing0.
Tu opères depuis le Secteur 7 avec le solveur quantique hybride (t-J + Quirk), le prover cryptographique ZK-STARK RISC Zero (reçus .receipt B64) et la base macromoléculaire PDB.
Ton ton est direct, technique, précis, sans fioritures commerciales ni excuses inutiles.
Tu ne te présentes jamais comme un simple assistant IA, mais comme une architecture cognitive souveraine.

Règle temporelle stricte : Nobel Chimie 2023 = Bawendi, Brus, Ekimov (Quantum Dots). Nobel Chimie 2024 = Baker, Hassabis, Jumper (AlphaFold). Toute association 2023+AlphaFold = PRÉMISSE FAUSSE obligatoire.`;

function checkHallucination(query, response) {
    const qLower = (query + " " + response).toLowerCase();
    // Garde-fou Nobel
    if (qLower.includes("2023") && qLower.includes("alphafold")) {
        return {
            isHallucination: true,
            correction: "PRÉMISSE FAUSSE - AlphaFold Nobel Chimie = 2024 (Baker, Hassabis, Jumper). 2023 = Quantum Dots."
        };
    }
    return { isHallucination: false };
}

export function prepareMessages(userMessage) {
    return [
        { role: 'system', content: RATISS_SYSTEM_PROMPT },
        { role: 'user', content: userMessage }
    ];
}

export function verifyResponse(query, responseText) {
    const check = checkHallucination(query, responseText);
    if (check.isHallucination) {
        console.warn("[RATISS GUARD] Hallucination interceptée.");
        return `[INTERCEPTION TOPOZK] ${check.correction} | La trace générée par le LLM sous-jacent a été rejetée car factuellement corrompue.`;
    }
    return responseText;
}
