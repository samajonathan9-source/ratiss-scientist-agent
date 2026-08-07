export interface ModelInfo {
  id: string;
  provider: string;
  name: string;
  desc: string;
}

export const MODELS: ModelInfo[] = [
  { id: "nvidia/nemotron-3-ultra-550b-a55b:free", provider: "NVIDIA", name: "Nemotron 3 Ultra 550B", desc: "Nemotron 3 Ultra 550B (Modèle ultra-puissant d'origine)" },
  { id: "nvidia/nemotron-nano-9b-v2:free", provider: "NVIDIA", name: "Nemotron Nano 9B V2", desc: "Nemotron Nano 9B (ultra léger, très rapide)" },
  { id: "openai/gpt-oss-20b:free", provider: "OpenAI", name: "gpt-oss-20b", desc: "Modèle open-source 20B hébergé par OpenAI" },
  { id: "google/gemma-4-26b-a4b-it:free", provider: "Google", name: "Gemma 4 26B A4B", desc: "Gemma 4 (architecture optimisée)" },
  { id: "meta-llama/llama-3.2-3b-instruct:free", provider: "Meta", name: "Llama 3.2 3B Instruct", desc: "Llama 3.2 3B (très léger, rapide)" },
  { id: "cohere/north-mini-code:free", provider: "Cohere", name: "Cohere North Mini Code", desc: "Cohere North Mini Code (compact)" },
  { id: "qwen/qwen3-next-80b-a3b-instruct:free", provider: "Qwen / Alibaba", name: "Qwen3 Next 80B Instruct", desc: "Qwen 80B (puissant, raisonnement logique)" }
];
