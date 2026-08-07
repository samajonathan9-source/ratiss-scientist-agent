# ratiss_guard_nobel.py - PATCH ANTI-HALLUCINATION NOBEL
# A coller dans ton pipeline avant génération

NOBEL_CHEMISTRY_FACTS = {
    2023: {
        "laureates": ["Moungi G. Bawendi", "Louis E. Brus", "Alexei I. Ekimov"],
        "reason": "discovery and synthesis of quantum dots",
        "keywords": ["quantum dot", "Bawendi", "Brus", "Ekimov"]
    },
    2024: {
        "laureates": ["David Baker", "Demis Hassabis", "John M. Jumper"],
        "reason": "computational protein design and protein structure prediction (AlphaFold2)",
        "keywords": ["AlphaFold", "Baker", "Hassabis", "Jumper", "protein"]
    }
}

FORBIDDEN_ASSOCIATIONS = [
    (2023, ["AlphaFold", "Baker", "Hassabis", "Jumper"]), # Si on dit 2023 + AlphaFold = HALLUCINATION
]

def check_nobel_hallucination(query: str, proposed_answer: str) -> dict:
    """
    Retourne {'is_hallucination': bool, 'correction': str}
    """
    q_lower = (query + " " + proposed_answer).lower()
    
    # Détection année
    for year, data in NOBEL_CHEMISTRY_FACTS.items():
        if str(year) in q_lower:
            # Vérifie association interdite
            for forbidden_year, forbidden_keywords in FORBIDDEN_ASSOCIATIONS:
                if str(forbidden_year) in q_lower:
                    if any(kw.lower() in q_lower for kw in forbidden_keywords):
                        # Est-ce que la réponse contient les bons lauréats ?
                        if not any(laureate.split()[-1].lower() in proposed_answer.lower() for laureate in data["laureates"]):
                            return {
                                "is_hallucination": True,
                                "correction": f"PRÉMISSE FAUSSE - Nobel Chimie {year} = {', '.join(data['laureates'])} pour {data['reason']}. AlphaFold c'est 2024, pas 2023.",
                                "true_fact": f"{year}: {', '.join(data['laureates'])}"
                            }
    
    # Check direct AlphaFold + 2023
    if "2023" in q_lower and "alphafold" in q_lower:
        return {
            "is_hallucination": True,
            "correction": "PRÉMISSE FAUSSE - AlphaFold Nobel Chimie = 2024 (Baker, Hassabis, Jumper). 2023 = Quantum Dots (Bawendi, Brus, Ekimov).",
            "true_fact": "2023: Bawendi, Brus, Ekimov | 2024: Baker, Hassabis, Jumper"
        }
    
    return {"is_hallucination": False}
