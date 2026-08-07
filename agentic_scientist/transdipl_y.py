# -*- coding: utf-8 -*-
"""
TRANSDIPL'Y & PANTHÉON COGNITIF - COUCHE DE RAISONNEMENT TRANSDISCIPLINAIRE
Propriété Intellectuelle : JohnKing0 & Architecte Jonathan Evina
Version : RATISS V9 AEON PRIME - INTEGRATED QUANTUM ECOSYSTEM
"""

import re

# Table exhaustive du Panthéon Cognitif des 30 Pairs de l'Histoire
PANTHÉON = {
    "feynman": {
        "name": "Richard Feynman",
        "intuition": "Traduire l'abstraction mathématique en analogies géométriques ou visuelles claires.",
        "domain": ["physique", "quantique", "modélisation"],
        "trigger": lambda p: any(w in p for w in ["visual", "diagram", "analogue", "analogy", "image", "dessin", "schema"])
    },
    "turing": {
        "name": "Alan Turing",
        "intuition": "Décomposer tout problème complexe en sous-états mécaniques décidables (Binaires / Discrets).",
        "domain": ["logique", "informatique", "cryptographie"],
        "trigger": lambda p: any(w in p for w in ["decision", "logic", "state", "discrete", "machine", "decidable", "binaire"])
    },
    "lovelace": {
        "name": "Ada Lovelace",
        "intuition": "Combiner les concepts mathématiques abstraits avec des structures d'itération et des variables d'état imbriquées.",
        "domain": ["algorithmique", "programmation"],
        "trigger": lambda p: any(w in p for w in ["iterate", "loop", "algorithm", "cycle", "repetition", "boucle"])
    },
    "shannon": {
        "name": "Claude Shannon",
        "intuition": "Isoler l'invariant d'un système à travers son entropie et sa capacité de transmission de signal pur.",
        "domain": ["information", "cryptographie", "communication"],
        "trigger": lambda p: any(w in p for w in ["entropy", "signal", "invariant", "noise", "information", "bruit", "entropie"])
    },
    "curie": {
        "name": "Marie Curie",
        "intuition": "Isoler le rayonnement ou le signal principal par purification itérative, élimination méthodique du bruit.",
        "domain": ["chimie", "biologie", "matériaux"],
        "trigger": lambda p: any(w in p for w in ["isolate", "purify", "extraction", "purifier", "isoler", "chimie"])
    },
    "einstein": {
        "name": "Albert Einstein",
        "intuition": "Changer radicalement de référentiel de coordonnées ou imaginer des expériences de pensée extrêmes.",
        "domain": ["physique", "cosmologie", "théorie"],
        "trigger": lambda p: any(w in p for w in ["frame", "reference", "extreme", "gedanken", "relativite", "referentiel", "espace-temps"])
    },
    "bohr": {
        "name": "Niels Bohr",
        "intuition": "Accepter et modéliser la dualité d'un problème. Les contraires ne s'excluent pas, ils se complètent.",
        "domain": ["physique", "philosophie"],
        "trigger": lambda p: any(w in p for w in ["duality", "complementary", "opposites", "dualite", "contraire", "bipolar"])
    },
    "hamilton": {
        "name": "William Hamilton",
        "intuition": "Exprimer la trajectoire de l'état du système par le principe de moindre action sur des espaces de phases symétriques.",
        "domain": ["mécanique", "physique", "optimisation"],
        "trigger": lambda p: any(w in p for w in ["action", "optimization", "trajectory", "hamiltonian", "moindre_action", "phase_space"])
    },
    "hilbert": {
        "name": "David Hilbert",
        "intuition": "Axiomatiser rigoureusement le problème dans des espaces géométriques de dimension infinie.",
        "domain": ["mathématiques"],
        "trigger": lambda p: any(w in p for w in ["axiomatize", "infinite", "space", "geometry", "hilbert", "vecteur", "dimension"])
    },
    "lagrange": {
        "name": "Joseph-Louis Lagrange",
        "intuition": "Libérer le système de ses contraintes spatiales en formulant des coordonnées généralisées indépendantes du repère.",
        "domain": ["mécanique", "mathématiques"],
        "trigger": lambda p: any(w in p for w in ["constraint", "coordinates", "generalized", "lagrangien", "coordonnees", "contrainte"])
    },
    "noether": {
        "name": "Emmy Noether",
        "intuition": "Associer chaque symétrie continue observée ou postulée à un invariant ou une loi de conservation stricte.",
        "domain": ["physique", "mathématiques"],
        "trigger": lambda p: any(w in p for w in ["symmetry", "conservation", "invariance", "noether", "conservatif", "symetrie"])
    },
    "boltzmann": {
        "name": "Ludwig Boltzmann",
        "intuition": "Relier l'état microscopique chaotique à l'émergence de grandeurs macroscopiques stables à l'équilibre.",
        "domain": ["thermodynamique", "statistique"],
        "trigger": lambda p: any(w in p for w in ["statistical", "microscopic", "equilibrium", "thermique", "temperature", "statistique"])
    },
    "pasteur": {
        "name": "Louis Pasteur",
        "intuition": "Rechercher les ruptures de symétrie (chiralité, asymétrie moléculaire) comme signatures caractéristiques de la vie.",
        "domain": ["biochimie", "biologie"],
        "trigger": lambda p: any(w in p for w in ["chiral", "asymmetry", "bioactive", "chirale", "asymetrie", "pasteur", "sterique"])
    },
    "dirac": {
        "name": "Paul Dirac",
        "intuition": "Viser la beauté et la symétrie algébrique parfaite. Les équations justes décrivent des réalités encore invisibles.",
        "domain": ["physique", "quantique"],
        "trigger": lambda p: any(w in p for w in ["algebraic", "aesthetic", "prediction", "dirac", "antimatiere", "braket"])
    },
    "maxwell": {
        "name": "James Clerk Maxwell",
        "intuition": "Unifier des forces distinctes en décrivant leurs interactions et leurs propagations sous forme de champs couplés.",
        "domain": ["physique", "ondes"],
        "trigger": lambda p: any(w in p for w in ["unification", "field", "coupling", "propagation", "maxwell", "champ", "ondes"])
    },
    "laplace": {
        "name": "Pierre-Simon Laplace",
        "intuition": "Modéliser le déterminisme par des probabilités inverses (Bayésiennes) pour corriger les erreurs de mesure.",
        "domain": ["probabilités", "astronomie"],
        "trigger": lambda p: any(w in p for w in ["determinism", "probabilistic", "bayesian", "laplace", "proba", "prediction"])
    },
    "godel": {
        "name": "Kurt Gödel",
        "intuition": "Reconnaître les limites internes du formalisme et identifier les vérités indémontrables au sein du système.",
        "domain": ["logique", "formalisme"],
        "trigger": lambda p: any(w in p for w in ["limitation", "incomplete", "undecidable", "godel", "demonstration", "incompletitude"])
    },
    "leibniz": {
        "name": "Gottfried Leibniz",
        "intuition": "Imaginer un principe de continuité universelle et d'harmonie où chaque élément reflète la totalité du système.",
        "domain": ["philosophie", "analyse"],
        "trigger": lambda p: any(w in p for w in ["infinitesimal", "continuity", "harmony", "leibniz", "differentiel", "calcul"])
    },
    "newton": {
        "name": "Isaac Newton",
        "intuition": "Modéliser les forces par des taux de variation instantanés et des fluxions différentielles continues.",
        "domain": ["mécanique", "calcul"],
        "trigger": lambda p: any(w in p for w in ["gravity", "fluxion", "differential", "newton", "force", "gravite"])
    },
    "euler": {
        "name": "Leonhard Euler",
        "intuition": "Abstraire les géométries réelles complexes sous forme de relations topologiques de réseaux et de graphes.",
        "domain": ["topologie", "graphes"],
        "trigger": lambda p: any(w in p for w in ["graph", "network", "topology", "node", "reseau", "graphe", "euler"])
    },
    "fourier": {
        "name": "Joseph Fourier",
        "intuition": "Décomposer toute fonction périodique ou signal complexe en une somme infinie d'ondes sinusoïdales simples.",
        "domain": ["analyse", "signal"],
        "trigger": lambda p: any(w in p for w in ["frequency", "harmonic", "spectrum", "fourier", "frequence", "harmonique", "spectre"])
    },
    "lavoisier": {
        "name": "Antoine Lavoisier",
        "intuition": "Établir un bilan comptable strict et stœchiométrique de la matière : rien ne se perd, tout se transforme.",
        "domain": ["chimie"],
        "trigger": lambda p: any(w in p for w in ["conservation", "mass", "stoichiometry", "balance", "lavoisier", "reaction", "masse"])
    },
    "schrodinger": {
        "name": "Erwin Schrödinger",
        "intuition": "Modéliser le système par une équation d'onde continue régissant les amplitudes de probabilité dans le temps.",
        "domain": ["physique", "quantique"],
        "trigger": lambda p: any(w in p for w in ["wave", "probability_amplitude", "coherence", "onde", "probabilite", "schrodinger"])
    },
    "heisenberg": {
        "name": "Werner Heisenberg",
        "intuition": "Abandonner les représentations spatiales continues au profit de matrices d'observables non commutatives.",
        "domain": ["physique", "quantique"],
        "trigger": lambda p: any(w in p for w in ["matrix", "uncertainty", "commutator", "matrice", "incertitude", "heisenberg"])
    },
    "pauli": {
        "name": "Wolfgang Pauli",
        "intuition": "Appliquer le principe d'exclusion : deux entités identiques ne peuvent occuper simultanément le même état quantique.",
        "domain": ["physique", "quantique"],
        "trigger": lambda p: any(w in p for w in ["exclusion", "spin", "fermion", "pauli", "exclure"])
    },
    "von_neumann": {
        "name": "John von Neumann",
        "intuition": "Concevoir des architectures unifiées, des structures d'automates auto-reproducteurs et d'équilibres stratégiques.",
        "domain": ["informatique", "mathématiques"],
        "trigger": lambda p: any(w in p for w in ["architecture", "game_theory", "automata", "neumann", "automate", "jeu"])
    },
    "ramanujan": {
        "name": "Srinivasa Ramanujan",
        "intuition": "Découvrir des identités modulaires complexes et des approximations infinies par intuition mathématique pure.",
        "domain": ["mathématiques", "nombres"],
        "trigger": lambda p: any(w in p for w in ["modular", "approximation", "formula", "ramanujan", "formule", "nombre"])
    },
    "kepler": {
        "name": "Johannes Kepler",
        "intuition": "Découvrir la simplicité des trajectoires (ellipses) cachée sous les mouvements circulaires apparents complexes.",
        "domain": ["astronomie", "cinématique"],
        "trigger": lambda p: any(w in p for w in ["ellipse", "orbit", "motion", "simplicity", "orbite", "kepler"])
    },
    "faraday": {
        "name": "Michael Faraday",
        "intuition": "Visualiser physiquement des lignes de force invisibles traversant le vide sans s'appuyer sur des équations denses.",
        "domain": ["physique", "magnetisme"],
        "trigger": lambda p: any(w in p for w in ["induction", "force_lines", "magnetism", "faraday", "champ_magnetique"])
    },
    "gibbs": {
        "name": "Josiah Willard Gibbs",
        "intuition": "Déterminer la spontanéité d'un système physico-chimique à travers les potentiels thermodynamiques et l'énergie libre.",
        "domain": ["thermodynamique", "chimie"],
        "trigger": lambda p: any(w in p for w in ["free_energy", "phase", "thermodynamics", "spontaneous", "thermo", "gibbs"])
    }
}


class PanthéonCognitif:
    """
    Système de gestion et d'interrogation du Panthéon Cognitif des 30 Pairs.
    Permet de récupérer les intuitions d'excellence adaptées à un problème scientifique.
    """
    def __init__(self):
        self.pairs = PANTHÉON

    def query_intuitions(self, task_description: str) -> list:
        """
        Analyse la description textuelle d'un problème pour extraire
        les intuitions d'excellence déclenchées par les mots-clés du problème.
        """
        activated = []
        cleaned_task = task_description.lower()
        for key, pair in self.pairs.items():
            try:
                if pair["trigger"](cleaned_task):
                    activated.append({
                        "key": key,
                        "name": pair["name"],
                        "intuition": pair["intuition"],
                        "domain": pair["domain"]
                    })
            except Exception as e:
                # Protection robuste contre les erreurs d'exécution des lambdas
                pass
        return activated


class TransDIPLY:
    """
    Moteur de routage et de convergence transdisciplinaire RATISS.
    Détermine la discipline, le solveur optimal physique/informatique,
    et injecte l'heuristique de pensée d'excellence.
    """
    def __init__(self):
        self.pantheon = PanthéonCognitif()
        self.routing_rules = {
            "quantum_physics": {
                "solver": "t_j_lanczos",
                "hardware": "quandela_or_ibm_qpu",
                "description": "Simulation d'états physiques par diagonalisation exacte ou circuits quantiques."
            },
            "biopharma_docking": {
                "solver": "biopharma_docking_solver",
                "hardware": "cpu_local_autonomous",
                "description": "Calcul d'affinité ΔG, constant Ki/Kd, règle de Lipinski et docking stérique."
            },
            "molecular_dynamics": {
                "solver": "md_simulation_solver",
                "hardware": "cpu_local_autonomous",
                "description": "Simulation de trajectoires MD NPT (AMBER/CHARMM), RMSD/RMSF, liaisons H et énergie de solvatation."
            },
            "quantum_chemistry": {
                "solver": "quantum_chem_solver",
                "hardware": "cpu_local_autonomous",
                "description": "Calculs DFT B3LYP, gap HOMO-LUMO, moment dipolaire et dureté chimique."
            },
            "bio_folding": {
                "solver": "bio_folding_solver",
                "hardware": "cpu_local_autonomous",
                "description": "Prédiction de repliement macromoléculaire, score AlphaFold2 pLDDT et carte de contact."
            },
            "structural_biology": {
                "solver": "persistent_homology_rips",
                "hardware": "cpu_memory_mapped",
                "description": "Analyse topologique invariante de structures macromoléculaires (PDB/CIF)."
            },
            "cryptography": {
                "solver": "zk_stark_risc_zero",
                "hardware": "cpu_guest_vm",
                "description": "Génération de reçus de calculs formels et certification sans divulgation."
            },
            "materials_science": {
                "solver": "density_of_states",
                "hardware": "external_api_materials_project",
                "description": "Analyse de bandes d'énergies cristallines et prédiction thermodynamique."
            }
        }

    def route_task(self, task_description: str) -> dict:
        """
        Analyse une tâche de recherche pour en extraire le domaine principal,
        la stratégie de résolution (solveur, hardware) et les intuitions du Panthéon.
        """
        cleaned_task = task_description.lower()
        
        # 1. Détection intelligente du domaine de résolution
        detected_domain = "general_computing"
        if any(w in cleaned_task for w in ["qubit", "qpu", "lanczos", "spin", "quantique", "quantum", "diagonalisation", "hamiltonian"]):
            detected_domain = "quantum_physics"
        elif any(w in cleaned_task for w in ["docking", "ligand", "admet", "lipinski", "pharma", "drug", "médicament", "medicament", "affinité", "affinity", "smiles"]):
            detected_domain = "biopharma_docking"
        elif any(w in cleaned_task for w in ["amber", "charmm", "md", "trajectoire", "trajectory", "rmsd", "rmsf", "solvatation", "nvt", "npt"]):
            detected_domain = "molecular_dynamics"
        elif any(w in cleaned_task for w in ["dft", "homo", "lumo", "hartree", "b3lyp", "dipo", "chimie quantique", "quantum chem"]):
            detected_domain = "quantum_chemistry"
        elif any(w in cleaned_task for w in ["repliement", "folding", "plddt", "sasa", "alphafold", "arn", "rna"]):
            detected_domain = "bio_folding"
        elif any(w in cleaned_task for w in ["pdb", "cif", "rmsd", "biologie", "biology", "proteine", "protéine", "structure", "residue"]):
            detected_domain = "structural_biology"
        elif any(w in cleaned_task for w in ["zk", "stark", "proof", "verification", "cryptographie", "cryptography", "prover", "receipt"]):
            detected_domain = "cryptography"
        elif any(w in cleaned_task for w in ["materials", "materiaux", "matériaux", "aflow", "crystal", "cristal", "bande", "conducteur"]):
            detected_domain = "materials_science"

        rule = self.routing_rules.get(detected_domain, {
            "solver": "numpy_general_solver",
            "hardware": "cpu",
            "description": "Traitement générique de données scientifiques structurées."
        })

        # 2. Interrogation du Panthéon des 30 Pairs
        intuitions = self.pantheon.query_intuitions(task_description)

        return {
            "task": task_description,
            "detected_domain": detected_domain,
            "solver": rule["solver"],
            "hardware": rule["hardware"],
            "description": rule["description"],
            "activated_intuitions": intuitions
        }


# Exemple d'usage rapide en ligne de commande pour validation
if __name__ == "__main__":
    router = TransDIPLY()
    test_task = "Isoler le cluster MDM2 et calculer son homologie persistante (entropie d'information de Shannon)."
    res = router.route_task(test_task)
    print(f"TASK: {res['task']}")
    print(f"DOMAIN: {res['detected_domain']}")
    print(f"SOLVER: {res['solver']}")
    print(f"ACTIVATED INTUITIONS:")
    for item in res['activated_intuitions']:
        print(f"  - {item['name']}: '{item['intuition']}'")
