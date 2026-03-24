import streamlit as st
import nltk
from nltk.corpus import wordnet
from nltk import pos_tag, word_tokenize, sent_tokenize

# Downloads
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('wordnet')

st.title("🧠 Linguistic Ambiguity Detector (Advanced)")

text = st.text_area("Enter a sentence or paragraph:")

# ---------- LEXICAL ----------
def detect_lexical(words):
    results = []
    for word in words:
        synsets = wordnet.synsets(word)
        if len(synsets) > 1:
            meanings = [syn.definition() for syn in synsets[:2]]
            reason = f"'{word}' has multiple dictionary meanings → {meanings[0]} / {meanings[1]}"
            results.append(reason)
    return results

# ---------- SYNTACTIC ----------
def detect_syntactic(sentence, pos_tags):
    tags = [tag for _, tag in pos_tags]

    # Example pattern: VBG + NN → "Flying planes"
    if "VBG" in tags and "NN" in tags:
        return f"Structure allows multiple interpretations → e.g., 'Flying planes' can mean planes that fly OR the act of flying planes"

    # Prepositional phrase ambiguity
    if "IN" in tags and "NN" in tags:
        return f"Prepositional phrase attachment unclear → phrase may modify different parts of sentence"

    return None

# ---------- SEMANTIC ----------
def detect_semantic(words):
    vague_words = ["thing", "stuff", "something", "anything", "it"]
    results = []
    for w in words:
        if w.lower() in vague_words:
            results.append(f"'{w}' is vague → meaning depends on missing context")
    return results

# ---------- ANAPHORIC ----------
def detect_anaphoric(words):
    pronouns = ["he", "she", "it", "they", "this", "that", "his", "her", "their"]
    results = []

    if any(p in [w.lower() for w in words] for p in pronouns):
        results.append("Pronoun reference unclear → could refer to multiple nouns in sentence")

    return results

# ---------- PRAGMATIC ----------
def detect_pragmatic(sentence):
    results = []
    cues = ["can you", "could you", "would you", "maybe", "please"]

    for cue in cues:
        if cue in sentence.lower():
            results.append(f"'{cue}' implies indirect meaning → request vs literal question")

    return results

# ---------- MAIN ----------
if st.button("Analyze"):
    if text:
        sentences = sent_tokenize(text)

        for i, sentence in enumerate(sentences, 1):
            st.subheader(f"Sentence {i}: {sentence}")

            words = word_tokenize(sentence)
            pos_tags = pos_tag(words)

            found = False

            # Lexical
            lexical = detect_lexical(words)
            if lexical:
                st.write("🟡 **Lexical Ambiguity**")
                for r in lexical:
                    st.write("•", r)
                found = True

            # Syntactic
            syntactic = detect_syntactic(sentence, pos_tags)
            if syntactic:
                st.write("🟠 **Syntactic Ambiguity**")
                st.write("•", syntactic)
                found = True

            # Semantic
            semantic = detect_semantic(words)
            if semantic:
                st.write("🔵 **Semantic Ambiguity**")
                for r in semantic:
                    st.write("•", r)
                found = True

            # Anaphoric
            anaphoric = detect_anaphoric(words)
            if anaphoric:
                st.write("🟣 **Anaphoric Ambiguity**")
                for r in anaphoric:
                    st.write("•", r)
                found = True

            # Pragmatic
            pragmatic = detect_pragmatic(sentence)
            if pragmatic:
                st.write("🔴 **Pragmatic Ambiguity**")
                for r in pragmatic:
                    st.write("•", r)
                found = True

            if not found:
                st.success("✅ No ambiguity detected")

    else:
        st.warning("Please enter text")