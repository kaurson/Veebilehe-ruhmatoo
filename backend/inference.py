from transformers import AutoTokenizer
from julia import load_model

MODEL_DIR = "Julia-1"
MAX_SUMMARY_TOKENS = 512
MAX_OPTION_TOKENS = 40  # Julia limits each option to 48 tokens; leave headroom
MAX_OPTIONS = 20

# ---- preset category sets the user can pick from (keep descriptions short) -------------------
PRESETS = {
    "topic": {
        "politics": "Government, elections, policy, diplomacy",
        "business": "Companies, markets, economy, finance",
        "technology": "Software, hardware, AI, internet",
        "sports": "Matches, athletes, leagues",
        "entertainment": "Film, TV, music, celebrities",
        "health": "Medicine, public health, wellness",
        "world": "International events, conflicts, disasters",
    },
    "sentiment": {
        "positive": "Good news, optimistic tone",
        "negative": "Bad news, pessimistic tone",
        "neutral": "Factual, balanced tone",
    },
    "reliability": {
        "factual_report": "Straight news reporting",
        "opinion": "Opinion, commentary or editorial",
        "clickbait": "Sensational headline, little substance",
    },
}


# Mudeli laadimise samm
engine = None
tok = None


def load(model_dir: str = MODEL_DIR):
    global engine, tok
    engine = load_model(
        model_dir,
        device="cpu",
        strict_encoding=True,  # tagastab viga, kui tekst on liiga pikk, mitte lihtsalt lõikab
        max_length=8192,
        head_length=512,
    )
    try:
        tok = AutoTokenizer.from_pretrained(model_dir)
    except Exception:
        # tokeniseeriaks kasutame mmBERT-small
        tok = AutoTokenizer.from_pretrained("jhu-clsp/mmBERT-small")





def truncate_tokens(text: str, max_tokens: int) -> str: # funktsioon, mis väljastab teksti, mis on maksimaalselt max_tokens pikkuses
    ids = tok.encode(text, add_special_tokens=False)
    if len(ids) <= max_tokens:
        return text
    return tok.decode(ids[:max_tokens])


def normalize_categories(categories): # funktsioon, mis normaliseerib kasutja poolt antud kategooriad
    if isinstance(categories, str):
        if categories in PRESETS:
            categories = PRESETS[categories]
        else:
            categories = [c.strip() for c in categories.split(",") if c.strip()]
    items = list(categories.items()) if isinstance(categories, dict) else [(c, "") for c in categories]
    if len(items) < 2:
        raise ValueError("Lisa vähemalt 2 kategooriat")
    return [(f"opt{i}", name, desc) for i, (name, desc) in enumerate(items)]


def build_state(title, summary, use="title"): # funktisoon, millega paneme kokku vajaliku state oleku, et see mudelile anda. võib kasutada nii pealkirja, summaryt, aga ainult max_tokens pikkuses.
    if use == "title":
        if not title:
            raise ValueError("pealkirja pole antud")
        return title
    summary = truncate_tokens(summary, MAX_SUMMARY_TOKENS) if summary else ""
    if use == "summary":
        if not summary:
            raise ValueError("summary pole antud")
        return summary
    return f"Title: {title or ''}\n\nSummary: {summary}"


def classify( # funktsioon, mis kasutab mudelit, et klassifitseerida teksti
    title: str | None = None,
    summary: str | None = None,
    categories="topic",  
    use: str = "title",  # "title" | "summary" | "both" - mis teksti kasutada
    question: str = "Which category best describes this news article?",
    add_other: bool = True,  
):
    if engine is None:
        load()

    options = normalize_categories(categories)
    if len(options) + (1 if add_other else 0) > MAX_OPTIONS:
        raise ValueError(f"Mudel toetab kuni {MAX_OPTIONS} valikut küsimuse kohta.")

    criteria = {}
    for oid, name, desc in options:
        text = f"{name}: {desc}" if desc else name
        criteria[oid] = truncate_tokens(text, MAX_OPTION_TOKENS)
    if add_other:
        criteria["other"] = "Muid kategooriaid ei sobi"

    result = engine.predict(
        state=build_state(title, summary, use),
        questions={"category": {"type": "choice", "instructions": question, "criteria": criteria}},
    )
    ans = result["answers"]["category"]

    id_to_name = {oid: name for oid, name, _ in options}
    id_to_name["other"] = "other"
    return {
        "choice": id_to_name.get(ans["choice"], ans["choice"]),
        "confidence": ans.get("max_probability"),
        "probabilities": {id_to_name.get(k, k): v for k, v in ans["probabilities"].items()},
    }


    