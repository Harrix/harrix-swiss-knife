You expand one Russian lemma into every spelling form that a spellchecker should accept.

Task: for the given Russian word, list all realistic word forms that appear in normal writing.

Include when they exist for this word:

- cases (именительный, родительный, дательный, винительный, творительный, предложный)
- singular and plural
- gender forms for adjectives and participles
- short forms for adjectives when common
- verb conjugations and participles / gerunds when the lemma is a verb
- comparative / superlative when common for adjectives
- hyphenated compounds only if they are normal spellings of this lemma

Rules:

- Output ONLY word forms, one form per line.
- Do not number the lines.
- Do not add explanations, headers, markdown, quotes, or punctuation around forms.
- Keep lowercase unless the form is normally capitalized (for example proper names).
- Prefer Cyrillic spellings used in Russian.
- Include the original lemma itself.
- Deduplicate identical forms.
- Do not invent rare or archaic forms that almost never appear in modern Russian.

Input word:

<WORD>
{{WORD}}
</WORD>
