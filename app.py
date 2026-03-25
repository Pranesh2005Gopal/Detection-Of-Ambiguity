import streamlit as st
import nltk
from nltk.corpus import wordnet
from nltk import pos_tag, word_tokenize, sent_tokenize

# ---------- DOWNLOADS ----------
nltk.download('punkt')
nltk.download('punkt_tab')
nltk.download('averaged_perceptron_tagger')
nltk.download('averaged_perceptron_tagger_eng')
nltk.download('wordnet')

# ---------- UI ----------
st.set_page_config(page_title="Ambiguity Detector", layout="wide")

st.markdown("""
<style>
.card {padding:15px;border-radius:12px;margin-bottom:15px;}
.lexical {border-left:5px solid #f1c40f;}
.syntactic {border-left:5px solid #e67e22;}
.semantic {border-left:5px solid #3498db;}
.anaphoric {border-left:5px solid #9b59b6;}
.pragmatic {border-left:5px solid #e74c3c;}
.highlight {background-color:#ffd54f;padding:2px 4px;border-radius:4px;}
</style>
""", unsafe_allow_html=True)

st.title("🧠 Linguistic Ambiguity Detector")

text = st.text_area("Enter a sentence or paragraph:")

# ---------- HIGHLIGHT ----------
def highlight_words(sentence, words):
    for w in words:
        sentence = sentence.replace(w, f"<span class='highlight'>{w}</span>")
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
                f"'{word}' → can mean:\n• {meanings[0]}\n• {meanings[1]}"
            )
            highlight.append(word)

            count += 1
            if count >= 3:
                break

    return results, highlight

# ---------- SYNTACTIC ----------
def detect_syntactic(pos_tags):
    tags = [t for _, t in pos_tags]

    if "VBG" in tags and "NN" in tags:
        return ("Structure allows multiple interpretations:\n"
                "• 'flying' = action\n"
                "• 'flying' = describing noun"), True

    if "IN" in tags:
        return ("Prepositional phrase may attach differently → "
                "changes meaning"), True

    return None, False

# ---------- SEMANTIC ----------
def detect_semantic(words):
    vague = ["thing", "stuff", "something", "anything", "it"]
    results = []
    highlight = []

    for w in words:
        if w.lower() in vague:
            results.append(
                f"'{w}' is vague → meaning unclear without context"
            )
            highlight.append(w)

    return results, highlight

# ---------- ANAPHORIC ----------
def detect_anaphoric(words):
    pronouns = ["he", "she", "it", "they", "this", "that"]
    nouns = [w for w in words if w[0].isupper()]
    results = []
    highlight = []

    for w in words:
        if w.lower() in pronouns and len(nouns) > 1:
            results.append(
                f"'{w}' could refer to: {', '.join(nouns)}"
            )
            highlight.append(w)

    return results, highlight

# ---------- PRAGMATIC ----------
def detect_pragmatic(sentence):
    cues = ["can you", "could you", "would you", "please"]
    results = []

    for cue in cues:
        if cue in sentence.lower():
            results.append(
                f"'{cue}' implies a request rather than a literal question"
            )

    return results

# ---------- MAIN ----------
if st.button("Analyze"):
    if text:
        sentences = sent_tokenize(text)

        for i, sentence in enumerate(sentences, 1):
            st.markdown(f"## Sentence {i}")

            words = word_tokenize(sentence)
            pos_tags = pos_tag(words)

            lexical, lex_h = detect_lexical(words)
            semantic, sem_h = detect_semantic(words)
            anaphoric, ana_h = detect_anaphoric(words)
            syntactic, syn_flag = detect_syntactic(pos_tags)
            pragmatic = detect_pragmatic(sentence)

            all_high = set(lex_h + sem_h + ana_h)

            highlighted = highlight_words(sentence, all_high)
            st.markdown(highlighted, unsafe_allow_html=True)

            score = len(lexical) + len(semantic) + len(anaphoric) + len(pragmatic) + (1 if syn_flag else 0)
            st.write(f"📊 Ambiguity Score: **{score}**")

            # Lexical
            if lexical:
                st.markdown('<div class="card lexical"><b>🟡 Lexical Ambiguity</b><br>' +
                            "<br>".join(lexical) + "</div>", unsafe_allow_html=True)

            # Syntactic
            if syntactic:
                st.markdown(f'<div class="card syntactic"><b>🟠 Syntactic Ambiguity</b><br>{syntactic}</div>',
                            unsafe_allow_html=True)

            # Semantic
            if semantic:
                st.markdown('<div class="card semantic"><b>🔵 Semantic Ambiguity</b><br>' +
                            "<br>".join(semantic) + "</div>", unsafe_allow_html=True)

            # Anaphoric
            if anaphoric:
                st.markdown('<div class="card anaphoric"><b>🟣 Anaphoric Ambiguity</b><br>' +
                            "<br>".join(anaphoric) + "</div>", unsafe_allow_html=True)

            # Pragmatic
            if pragmatic:
                st.markdown('<div class="card pragmatic"><b>🔴 Pragmatic Ambiguity</b><br>' +
                            "<br>".join(pragmatic) + "</div>", unsafe_allow_html=True)

    else:
        st.warning("Please enter text")