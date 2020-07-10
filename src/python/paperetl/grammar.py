"""
Grammar module
"""

import en_core_sci_md

class Grammar(object):
    """
    Linguistic processing rules applied to sentences.
    """

    def __init__(self):
        # spaCy NLP
        self.nlp = en_core_sci_md.load()

    def parse(self, text):
        """
        Parses list of text elements to NLP tokens.

        Args:
            text: list of text elements

        Returns:
            tokenslist - list of token lists
        """

        results = None

        if text:
            # Run text through linguistic rules
            results = [self.applyRules(tokens) for tokens in self.nlp.pipe(text, batch_size=256)]

        return results

    def label(self, tokens):
        """
        Linguistic rules processing logic. Identifies non-informative sentences and labels them accordingly.

        Labels:
            - QUESTION: Any text ending in a question mark
            - FRAGMENT: Poorly structured sentences with limited information

        Args:
            tokens: parsed tokens

        Returns:
            label if detected else None
        """

        label = None

        if tokens:
            # Label non-informative sentences
            if self.isQuestion(tokens.text):
                label = "QUESTION"
            elif self.isFragment(tokens):
                label = "FRAGMENT"

        return label

    def applyRules(self, tokens):
        """
        Apply custom rules to the parsed tokens.

        Args:
            tokens: parsed tokens

        Returns:
            updated tokens with rules applied
        """

        # Override POS to NOUN for 2019-nCoV
        for token in tokens:
            if token.pos_ == "NUM" and token.text.lower() == "2019-ncov":
                token.pos_ = "NOUN"

        return tokens

    def isQuestion(self, text):
        """
        Determines if the text is a question

        Args:
            text: input text

        Returns:
            true if text is a question, false otherwise
        """

        # Questions have a ? mark at end
        return text.strip().endswith("?")

    def isFragment(self, tokens):
        """
        Run text against linguistic rules to determine if sentence is a fragment. Fragments are non descriptive.

        Args:
            tokens: nlp document tokens

        Returns:
            true if text is a sentence fragment, false otherwise
        """

        # Nominal subject Nouns/Proper Nouns
        nouns = any([t.pos_  in ["NOUN", "PROPN"]  and t.dep_ in ["nsubj", "nsubjpass"] for t in tokens])

        # Actions (adverb, auxiliary, verb)
        action = any([t.pos_ in ["ADV", "AUX", "VERB"] for t in tokens])

        # Consider root words with a nominal subject as an action word
        action = action or any([t.dep_ in ["appos", "ROOT"] and any([x.dep_ in ["nsubj", "nsubjpass"] for x in t.children]) for t in tokens])

        # Non-punctuation tokens and multi-character words (don't count single letters which are often variables used in equations)
        words = [t.text for t in tokens if t.pos_ not in ["PUNCT", "SPACE", "SYM"] and len(t.text) > 1]

        # Valid sentences take the following form:
        #  - At least one nominal subject noun/proper noun AND
        #  - At least one action/verb AND
        #  - At least 5 words
        valid = nouns and action and len(words) >= 5

        return not valid
