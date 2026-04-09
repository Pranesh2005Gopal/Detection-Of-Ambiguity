import streamlit as st
import nltk
from nltk.corpus import wordnet
from nltk import word_tokenize, sent_tokenize
import re

# ---------- DOWNLOADS ----------
nltk.download('punkt', quiet=True)
nltk.download('punkt_tab', quiet=True)
nltk.download('averaged_perceptron_tagger', quiet=True)
nltk.download('averaged_perceptron_tagger_eng', quiet=True)
nltk.download('wordnet', quiet=True)

# ---------- UI ----------
st.set_page_config(page_title="Ambiguity Detector", layout="wide")

st.markdown("""
<style>
/* Force dark text everywhere inside cards */
.card {
    padding: 15px 20px;
    border-radius: 12px;
    margin-bottom: 15px;
    color: #111111 !important;
}
.card b, .card span, .card p {
    color: #111111 !important;
}

.lexical   { border-left: 5px solid #e6a800; background-color: #fff8cc; }
.syntactic { border-left: 5px solid #cc5500; background-color: #ffe8cc; }
.semantic  { border-left: 5px solid #1a6bbf; background-color: #cce0ff; }
.anaphoric { border-left: 5px solid #7b2fa8; background-color: #ead6ff; }
.pragmatic { border-left: 5px solid #c0392b; background-color: #ffd6d6; }

.card-title {
    font-size: 16px;
    font-weight: 700;
    margin-bottom: 10px;
    display: block;
    color: #111111 !important;
}

.card-body {
    font-size: 14px;
    line-height: 1.8;
    color: #222222 !important;
}

.highlight {
    background-color: #ffc107;
    padding: 2px 6px;
    border-radius: 5px;
    font-weight: bold;
    color: #000000 !important;
}

.sentence-box {
    background: #f0f0f0;
    border-radius: 8px;
    padding: 10px 14px;
    font-size: 16px;
    margin-bottom: 10px;
    color: #111111 !important;
}
</style>
""", unsafe_allow_html=True)

st.title("🔍 Linguistic Ambiguity Detector")
text = st.text_area("Enter a sentence or paragraph:", height=120)

# ---------- HIGHLIGHT ----------
def highlight_words(sentence, words):
    for w in words:
        pattern = r'\b' + re.escape(w) + r'\b'
        sentence = re.sub(
            pattern,
            lambda m: f"<span class='highlight'>{m.group()}</span>",
            sentence,
            flags=re.IGNORECASE
        )
    return sentence

# ---------- LEXICAL ----------
def detect_lexical(words):
    results = []
    highlight = []
    count = 0

    for word in words:
        synsets = wordnet.synsets(word)
        if len(synsets) > 2 and word.isalpha() and len(word) > 3:
            meanings = [syn.definition() for syn in synsets[:2]]
            results.append(
                f"<b>'{word}'</b> can mean:<br>"
                f"&nbsp;&nbsp;• {meanings[0]}<br>"
                f"&nbsp;&nbsp;• {meanings[1]}"
            )
            highlight.append(word)
            count += 1
            if count >= 3:
                break

    return results, highlight

# ---------- SYNTACTIC ----------
def detect_syntactic(sentence, words):
    words_lower = [w.lower() for w in words]

    if "with" in words_lower:
        idx = words_lower.index("with")
        before = " ".join(words[:idx])
        after = " ".join(words[idx + 1:])

        explanation = (
            "Ambiguity occurs at <b>'with'</b> phrase:<br>"
            f"&nbsp;&nbsp;• <i>{before}</i> <b>using</b> {after}<br>"
            f"&nbsp;&nbsp;• <i>{before}</i> <b>who has</b> {after}"
        )
        return explanation, True, ["with"]

    return None, False, []

# ---------- SEMANTIC ----------
def detect_semantic(words):
    results = []
    highlight = []
    words_lower = [w.lower() for w in words]
    joined = " ".join(words_lower)

    if "bat" in words_lower:
        results.append(
            "<b>'bat'</b> creates ambiguity → could mean:<br>"
            "&nbsp;&nbsp;• a flying animal (mammal)<br>"
            "&nbsp;&nbsp;• a cricket or baseball bat"
        )
        highlight.append("bat")

    if "it" in words_lower:
        results.append(
            "<b>'it'</b> creates ambiguity → unclear meaning depends on context"
        )
        highlight.append("it")

    if "visiting relatives" in joined:
        results.append(
            "<b>'Visiting relatives'</b> creates ambiguity → could mean:<br>"
            "&nbsp;&nbsp;• relatives who are visiting you<br>"
            "&nbsp;&nbsp;• the act of you visiting relatives"
        )
        highlight.extend(["visiting", "relatives"])

    return results, highlight

# ---------- ANAPHORIC ----------
def detect_anaphoric(words):
    pronouns = ["he", "she", "it", "they", "this", "that", "him"]
    results = []
    highlight = []

    for w in words:
        lw = w.lower()
        if lw in pronouns:
            if lw == "they":
                results.append(
                    f"<b>'{w}'</b> may refer to:<br>"
                    "&nbsp;&nbsp;• a previously mentioned group<br>"
                    "&nbsp;&nbsp;• the relatives"
                )
            elif lw == "it":
                results.append(
                    f"<b>'{w}'</b> may refer to:<br>"
                    "&nbsp;&nbsp;• the subject being discussed<br>"
                    "&nbsp;&nbsp;• an object mentioned earlier"
                )
            elif lw == "he":
                results.append(
                    f"<b>'{w}'</b> may refer to:<br>"
                    "&nbsp;&nbsp;• one male person<br>"
                    "&nbsp;&nbsp;• another male mentioned earlier"
                )
            elif lw == "she":
                results.append(
                    f"<b>'{w}'</b> may refer to:<br>"
                    "&nbsp;&nbsp;• one female person<br>"
                    "&nbsp;&nbsp;• another female mentioned earlier"
                )
            else:
                results.append(f"<b>'{w}'</b> has an unclear reference in context")

            highlight.append(w)

    return results, highlight

# ---------- PRAGMATIC ----------
def detect_pragmatic(sentence):
    cues = ["can you", "could you", "would you", "please"]
    results = []
    for cue in cues:
        if cue in sentence.lower():
            results.append(
                f"<b>'{cue}'</b> implies a polite request, not a literal question about ability"
            )
    return results

# ---------- RENDER CARD ----------
def render_card(css_class, emoji, title, items):
    body = "<br><br>".join(items)
    st.markdown(
        f'<div class="card {css_class}">'
        f'<span class="card-title">{emoji} {title}</span>'
        f'<div class="card-body">{body}</div>'
        f'</div>',
        unsafe_allow_html=True
    )

# ---------- MAIN ----------
if st.button("🔎 Analyze"):
    if text.strip():
        sentences = sent_tokenize(text)

        for i, sentence in enumerate(sentences, 1):
            st.markdown(f"### Sentence {i}")

            words = word_tokenize(sentence)

            lexical,  lex_h              = detect_lexical(words)
            semantic, sem_h              = detect_semantic(words)
            anaphoric, ana_h             = detect_anaphoric(words)
            syntactic, syn_flag, syn_h   = detect_syntactic(sentence, words)
            pragmatic                    = detect_pragmatic(sentence)

            all_high = list(set(lex_h + sem_h + ana_h + syn_h))
            highlighted = highlight_words(sentence, all_high)

            st.markdown(
                f'<div class="sentence-box">{highlighted}</div>',
                unsafe_allow_html=True
            )

            score = (
                len(lexical) + len(semantic) + len(anaphoric) +
                len(pragmatic) + (1 if syn_flag else 0)
            )
            st.write(f"📊 Ambiguity Score: **{score}**")

            if lexical:
                render_card("lexical", "🟡", "Lexical Ambiguity", lexical)
            if syntactic:
                render_card("syntactic", "🟠", "Syntactic Ambiguity", [syntactic])
            if semantic:
                render_card("semantic", "🔵", "Semantic Ambiguity", semantic)
            if anaphoric:
                render_card("anaphoric", "🟣", "Anaphoric Ambiguity", anaphoric)
            if pragmatic:
                render_card("pragmatic", "🔴", "Pragmatic Ambiguity", pragmatic)

            if score == 0:
                st.success("✅ No ambiguity detected in this sentence.")

            st.divider()

    else:
        st.warning("Please enter some text to analyze.")