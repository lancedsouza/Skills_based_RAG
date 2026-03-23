"use client"

import { useState, useEffect } from "react"

export default function SkillSearch() {
  const [query, setQuery] = useState("")
  const [suggestions, setSuggestions] = useState([])     
  const [selected, setSelected] = useState([])           
  const [recommendations, setRecommendations] = useState([]) 
  const [loading, setLoading] = useState(false)

  // --- 1. THE AI WATCHDOG (Automatic Discovery) ---
  useEffect(() => {
    console.log("📊 WATCHDOG: 'selected' list updated:", selected);

    if (selected.length === 0) {
      setRecommendations([]);
      return;
    }

    const fetchAI = async () => {
      setLoading(true);
      console.log("🚀 TRIGGERING REAL AI SEARCH for:", selected);

      try {
        // Change localhost to 127.0.0.1 if you experience CORS 'Preflight' issues
        const res = await fetch("http://127.0.0.1:8000/multi-skill-search", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(selected),
        });

        if (!res.ok) throw new Error(`Server Response: ${res.status}`);

        const data = await res.json();
        console.log("💎 BACKEND RETURNED:", data.results);

        // Filter out what the user already selected
        const filtered = data.results.filter(
          (rec) => !selected.includes(rec.name)
        );
        
        setRecommendations(filtered.slice(0, 10));
      } catch (e) {
        console.error("❌ AI RECOMMENDATION ERROR:", e);
        setRecommendations([]);
      } finally {
        setLoading(false);
      }
    };

    fetchAI(); 
  }, [selected]); // <--- This dependency is the 'Magic Trigger'

  // --- 2. AUTOCOMPLETE LOGIC (While Typing) ---
  useEffect(() => {
    if (query.length < 2) {
      setSuggestions([]);
      return;
    }

    const fetchAuth = async () => {
      try {
        const res = await fetch(`http://127.0.0.1:8000/suggest?query=${query}`);
        const data = await res.json();
        setSuggestions(data.suggestions);
      } catch (e) {
        console.error("❌ Autocomplete Error:", e);
      }
    };

    const t = setTimeout(fetchAuth, 300);
    return () => clearTimeout(t);
  }, [query]);

  // --- 3. SELECTION HANDLERS ---
  const addSkill = (name) => {
    if (selected.includes(name)) {
      setQuery("");
      setSuggestions([]);
      return;
    }
    setSelected((prev) => [...prev, name]);
    setQuery("");
    setSuggestions([]);
  };

  const removeSkill = (name) => {
    setSelected((prev) => prev.filter((s) => s !== name));
  };

  return (
    <div className="max-w-2xl mx-auto p-10 font-sans">
      <h2 className="text-gray-400 text-xs font-bold uppercase mb-4 tracking-tighter">AI Skill Suggestion Engine</h2>
      
      {/* SEARCH BAR CONTAINER */}
      <div className="relative border-2 border-gray-200 rounded-xl p-4 flex flex-wrap gap-2 bg-white shadow-sm focus-within:border-blue-500 transition-all">
        
        {/* Chips */}
        {selected.map(s => (
          <span key={s} className="bg-blue-600 text-white px-3 py-1 rounded-md flex items-center gap-2 text-sm font-semibold animate-in fade-in zoom-in duration-200">
            {s} 
            <button onClick={() => removeSkill(s)} className="hover:text-red-300 font-bold">×</button>
          </span>
        ))}

        {/* Input */}
        <input 
          className="flex-1 outline-none text-lg text-gray-700 min-w-[140px]" 
          value={query} 
          onChange={e => setQuery(e.target.value)} 
          placeholder={selected.length === 0 ? "Search skills..." : "Add more..."}
        />
        
        {/* DROPDOWN MENU */}
        {suggestions.length > 0 && (
          <div className="absolute top-full left-0 right-0 mt-2 bg-white border border-gray-100 rounded-lg shadow-2xl z-50 overflow-hidden">
            {suggestions.map(s => (
              <div 
                key={s.id} 
                onMouseDown={(e) => { e.preventDefault(); addSkill(s.name); }}
                className="p-3 hover:bg-blue-50 cursor-pointer text-gray-700 border-b last:border-0 transition-colors"
              >
                {s.name}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* AI SUGGESTIONS SECTION */}
      <div className="mt-10 min-h-[140px]">
        {loading ? (
          <div className="flex items-center gap-2 text-purple-500 animate-pulse font-medium">
            <span className="text-xl">✨</span> AI is finding semantic matches...
          </div>
        ) : recommendations.length > 0 ? (
          <div className="animate-in fade-in slide-in-from-top-4 duration-500">
            <p className="text-sm font-bold text-purple-600 mb-4 flex items-center gap-2">
              <span className="text-lg">✨</span> AI suggested keywords
            </p>
            <div className="flex flex-wrap gap-3">
              {recommendations.map(r => (
                <button 
                  key={r.name} 
                  onClick={() => addSkill(r.name)}
                  className="bg-white border border-purple-100 px-5 py-2 rounded-full hover:bg-purple-600 hover:text-white hover:border-purple-600 transition-all shadow-sm text-sm font-medium text-purple-800"
                >
                  {r.name}
                </button>
              ))}
            </div>
          </div>
        ) : selected.length > 0 ? (
          <p className="text-gray-400 text-xs italic">
            Waiting for more data to be ingested... No similar matches found in the current index.
          </p>
        ) : null}
      </div>
    </div>
  )
}