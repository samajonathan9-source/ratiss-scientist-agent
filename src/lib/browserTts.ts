/**
 * Utility for resolving Browser & Audus TTS Voices with Male/Female selection
 */

export function getBrowserVoice(gender: "homme" | "femme"): SpeechSynthesisVoice | null {
  if (typeof window === "undefined" || !("speechSynthesis" in window)) {
    return null;
  }

  let allVoices = window.speechSynthesis.getVoices();
  if (allVoices.length === 0) {
    // Retry once in case of asynchronous loading
    allVoices = window.speechSynthesis.getVoices();
  }
  if (allVoices.length === 0) return null;

  const isFemme = gender === "femme";
  const lowerName = (v: SpeechSynthesisVoice) => v.name.toLowerCase();

  // 1. Priority to Audus TTS extension voices if present in browser
  const audusVoices = allVoices.filter((v) => lowerName(v).includes("audus"));
  if (audusVoices.length > 0) {
    if (isFemme) {
      const audusFemale = audusVoices.find(
        (v) =>
          lowerName(v).includes("femme") ||
          lowerName(v).includes("female") ||
          lowerName(v).includes("woman") ||
          lowerName(v).includes("f")
      );
      if (audusFemale) return audusFemale;
    } else {
      const audusMale = audusVoices.find(
        (v) =>
          lowerName(v).includes("homme") ||
          lowerName(v).includes("male") ||
          lowerName(v).includes("man") ||
          lowerName(v).includes("m")
      );
      if (audusMale) return audusMale;
    }
    // Return first Audus voice if specific gender isn't explicitly in the extension name
    if (audusVoices[0]) return audusVoices[0];
  }

  // 2. Filter French voices or fallback to all voices
  const frVoices = allVoices.filter((v) => v.lang.toLowerCase().startsWith("fr"));
  const pool = frVoices.length > 0 ? frVoices : allVoices;

  if (isFemme) {
    const femaleKeywords = [
      "femme", "female", "woman", "hortense", "celeste", "samantha", "julie", 
      "aurelie", "amélie", "marie", "virginie", "denise", "zira", "google français"
    ];
    const match = pool.find((v) => femaleKeywords.some((k) => lowerName(v).includes(k)));
    if (match) return match;

    const maleKeywords = ["homme", "male", "man", "paul", "thomas", "nicolas", "daniel", "gilles", "gérard", "henri", "claude", "david"];
    const nonMale = pool.find((v) => !maleKeywords.some((k) => lowerName(v).includes(k)));
    return nonMale || pool[0];
  } else {
    const maleKeywords = [
      "homme", "male", "man", "paul", "thomas", "nicolas", "daniel", 
      "gilles", "gérard", "henri", "claude", "david", "msb", "microsoft henri"
    ];
    const match = pool.find((v) => maleKeywords.some((k) => lowerName(v).includes(k)));
    if (match) return match;

    const femaleKeywords = ["femme", "female", "woman", "hortense", "celeste", "samantha", "julie", "aurelie", "amélie", "marie", "virginie", "denise"];
    const nonFemale = pool.find((v) => !femaleKeywords.some((k) => lowerName(v).includes(k)));
    return nonFemale || pool[1] || pool[0];
  }
}

export function speakBrowserTts(
  text: string, 
  gender: "homme" | "femme", 
  onStart?: () => void, 
  onEnd?: () => void, 
  onError?: (err: any) => void
) {
  if (typeof window === "undefined" || !("speechSynthesis" in window)) {
    if (onError) onError(new Error("speechSynthesis non disponible"));
    return;
  }

  window.speechSynthesis.cancel();

  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = "fr-FR";
  utterance.volume = 1.0;
  utterance.rate = 1.0;

  const selectedVoice = getBrowserVoice(gender);
  if (selectedVoice) {
    utterance.voice = selectedVoice;
  }

  utterance.onstart = () => {
    if (onStart) onStart();
  };

  utterance.onend = () => {
    if (onEnd) onEnd();
  };

  utterance.onerror = (e) => {
    if (e && e.error === "interrupted") return;
    if (onError) onError(e);
  };

  setTimeout(() => {
    window.speechSynthesis.speak(utterance);
  }, 50);
}
