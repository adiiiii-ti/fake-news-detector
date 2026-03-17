"""
AI-Generated Content Detector
Uses statistical text analysis to detect AI-generated content.
Analyzes: perplexity indicators, burstiness, vocabulary richness,
sentence structure uniformity, and common AI writing patterns.
"""

import re
import math
from collections import Counter


class AIContentDetector:
    """Detects AI-generated text using statistical heuristics."""

    # Common AI filler phrases and patterns
    AI_PHRASES = [
        r"\bin conclusion\b",
        r"\bfurthermore\b",
        r"\bmoreover\b",
        r"\bnevertheless\b",
        r"\bnonetheless\b",
        r"\bit is worth noting\b",
        r"\bit'?s important to note\b",
        r"\bit'?s worth mentioning\b",
        r"\bin today'?s world\b",
        r"\bin today'?s digital age\b",
        r"\bin the realm of\b",
        r"\bdelve\b",
        r"\btapestry\b",
        r"\blandscape\b",
        r"\bparadigm\b",
        r"\blever(?:age|aging)\b",
        r"\bfacilitat(?:e|es|ing)\b",
        r"\butiliz(?:e|es|ing)\b",
        r"\bunderscor(?:e|es|ing)\b",
        r"\ba testament to\b",
        r"\bin this article\b",
        r"\bas we navigate\b",
        r"\blet'?s explore\b",
        r"\bwithout further ado\b",
        r"\boverall\b.*\bimportant\b",
        r"\bplays a (?:crucial|vital|key|pivotal) role\b",
        r"\bin (?:summary|essence)\b",
        r"\bone cannot (?:simply|merely|help but)\b",
    ]

    # Transition phrases heavily favored by AI
    TRANSITION_PHRASES = [
        r"\badditionally\b",
        r"\bconsequently\b",
        r"\bsubsequently\b",
        r"\bspecifically\b",
        r"\bsignificantly\b",
        r"\bultimately\b",
        r"\bfundamentally\b",
        r"\bwhile .{5,40}, (?:it |this |they )",
        r"\bon (?:the )?one hand\b",
        r"\bon the other hand\b",
    ]

    def analyze(self, text: str) -> dict:
        """
        Analyze text and return AI detection results.
        Returns dict with score (0-100), verdict, and detailed metrics.
        """
        if not text or len(text.strip()) < 50:
            return {
                "score": 0,
                "verdict": "Too Short",
                "confidence": "low",
                "details": "Text is too short for meaningful analysis. Please provide at least 50 characters.",
                "metrics": {},
            }

        text = text.strip()
        sentences = self._split_sentences(text)
        words = self._tokenize(text)

        if len(sentences) < 2:
            return {
                "score": 0,
                "verdict": "Too Short",
                "confidence": "low",
                "details": "Need at least 2 sentences for analysis.",
                "metrics": {},
            }

        # Compute individual metrics (each returns 0-1 score, higher = more AI-like)
        metrics = {}
        metrics["sentence_uniformity"] = self._sentence_length_uniformity(sentences)
        metrics["vocabulary_richness"] = self._vocabulary_richness(words)
        metrics["ai_phrase_density"] = self._ai_phrase_density(text, words)
        metrics["transition_density"] = self._transition_density(text, sentences)
        metrics["burstiness"] = self._burstiness_score(sentences)
        metrics["punctuation_variety"] = self._punctuation_variety(text)
        metrics["paragraph_structure"] = self._paragraph_structure(text)
        metrics["repetition_patterns"] = self._repetition_patterns(words)

        # Weighted combination
        weights = {
            "sentence_uniformity": 0.15,
            "vocabulary_richness": 0.10,
            "ai_phrase_density": 0.25,
            "transition_density": 0.10,
            "burstiness": 0.15,
            "punctuation_variety": 0.05,
            "paragraph_structure": 0.10,
            "repetition_patterns": 0.10,
        }

        raw_score = sum(metrics[k] * weights[k] for k in weights)
        # Scale to 0-100
        score = min(100, max(0, int(raw_score * 100)))

        # Determine verdict
        if score >= 75:
            verdict = "Likely AI-Generated"
            confidence = "high"
        elif score >= 50:
            verdict = "Possibly AI-Generated"
            confidence = "medium"
        elif score >= 30:
            verdict = "Likely Human-Written"
            confidence = "medium"
        else:
            verdict = "Human-Written"
            confidence = "high"

        # Build explanations
        details = self._build_details(metrics, score)

        return {
            "score": score,
            "verdict": verdict,
            "confidence": confidence,
            "details": details,
            "metrics": {k: round(v * 100, 1) for k, v in metrics.items()},
        }

    # ----- Metric Functions -----

    def _sentence_length_uniformity(self, sentences: list) -> float:
        """AI tends to write sentences of similar length. Low variance = more AI-like."""
        lengths = [len(s.split()) for s in sentences]
        if len(lengths) < 2:
            return 0.0
        mean = sum(lengths) / len(lengths)
        if mean == 0:
            return 0.0
        variance = sum((l - mean) ** 2 for l in lengths) / len(lengths)
        cv = math.sqrt(variance) / mean  # coefficient of variation
        # Human text typically has CV > 0.5, AI tends to be < 0.4
        if cv < 0.2:
            return 1.0
        elif cv < 0.4:
            return 0.7
        elif cv < 0.6:
            return 0.3
        else:
            return 0.1

    def _vocabulary_richness(self, words: list) -> float:
        """AI tends to use a moderate, 'safe' vocabulary. Measures type-token ratio."""
        if not words:
            return 0.0
        unique = set(w.lower() for w in words)
        ttr = len(unique) / len(words)
        # AI typically has TTR between 0.4-0.6 for longer texts
        # Very high or very low TTR suggests human
        if 0.45 <= ttr <= 0.60:
            return 0.7
        elif 0.35 <= ttr <= 0.70:
            return 0.4
        else:
            return 0.1

    def _ai_phrase_density(self, text: str, words: list) -> float:
        """Count AI-characteristic phrases relative to text length."""
        text_lower = text.lower()
        count = 0
        for pattern in self.AI_PHRASES:
            matches = re.findall(pattern, text_lower)
            count += len(matches)
        density = count / max(1, len(words) / 100)  # per 100 words
        if density >= 3:
            return 1.0
        elif density >= 2:
            return 0.8
        elif density >= 1:
            return 0.5
        elif density >= 0.5:
            return 0.3
        else:
            return 0.05

    def _transition_density(self, text: str, sentences: list) -> float:
        """AI overuses transition words at the start of sentences."""
        if not sentences:
            return 0.0
        text_lower = text.lower()
        count = 0
        for pattern in self.TRANSITION_PHRASES:
            count += len(re.findall(pattern, text_lower))
        ratio = count / len(sentences)
        if ratio >= 0.5:
            return 1.0
        elif ratio >= 0.3:
            return 0.7
        elif ratio >= 0.15:
            return 0.4
        else:
            return 0.1

    def _burstiness_score(self, sentences: list) -> float:
        """
        'Burstiness' measures variation in complexity across sentences.
        Human writing is bursty (mix of short punchy + long complex sentences).
        AI writing tends to be uniform.
        """
        if len(sentences) < 3:
            return 0.5
        complexities = []
        for s in sentences:
            words_in_s = len(s.split())
            commas = s.count(",")
            complexity = words_in_s + commas * 2
            complexities.append(complexity)
        mean_c = sum(complexities) / len(complexities)
        if mean_c == 0:
            return 0.5
        diffs = [abs(complexities[i] - complexities[i - 1]) for i in range(1, len(complexities))]
        avg_diff = sum(diffs) / len(diffs)
        burstiness = avg_diff / mean_c
        # Low burstiness = more AI-like
        if burstiness < 0.3:
            return 0.9
        elif burstiness < 0.5:
            return 0.6
        elif burstiness < 0.8:
            return 0.3
        else:
            return 0.1

    def _punctuation_variety(self, text: str) -> float:
        """AI uses fewer varied punctuation marks (rarely uses dashes, semicolons, etc.)."""
        special_punct = set()
        for ch in text:
            if ch in "!?;:—–-()[]\"'…":
                special_punct.add(ch)
        count = len(special_punct)
        if count >= 6:
            return 0.1  # human-like variety
        elif count >= 4:
            return 0.3
        elif count >= 2:
            return 0.6
        else:
            return 0.9

    def _paragraph_structure(self, text: str) -> float:
        """AI tends to create well-structured paragraphs of similar length."""
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        if len(paragraphs) <= 1:
            return 0.3
        lengths = [len(p.split()) for p in paragraphs]
        mean = sum(lengths) / len(lengths)
        if mean == 0:
            return 0.3
        variance = sum((l - mean) ** 2 for l in lengths) / len(lengths)
        cv = math.sqrt(variance) / mean
        if cv < 0.25:
            return 0.9  # very uniform paragraphs = AI-like
        elif cv < 0.5:
            return 0.5
        else:
            return 0.2

    def _repetition_patterns(self, words: list) -> float:
        """AI tends to repeat certain structures. Check for repeated bigrams."""
        if len(words) < 10:
            return 0.0
        lower_words = [w.lower() for w in words]
        bigrams = [f"{lower_words[i]} {lower_words[i+1]}" for i in range(len(lower_words) - 1)]
        counts = Counter(bigrams)
        if not counts:
            return 0.0
        repeated = sum(1 for c in counts.values() if c > 1)
        ratio = repeated / len(counts) if counts else 0
        if ratio > 0.15:
            return 0.8
        elif ratio > 0.08:
            return 0.5
        else:
            return 0.2

    # ----- Helpers -----

    def _split_sentences(self, text: str) -> list:
        """Split text into sentences."""
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip() and len(s.strip()) > 5]

    def _tokenize(self, text: str) -> list:
        """Simple word tokenization."""
        return re.findall(r'\b[a-zA-Z]+\b', text)

    def _build_details(self, metrics: dict, score: int) -> str:
        """Build human-readable explanation."""
        parts = []

        if metrics["ai_phrase_density"] > 0.5:
            parts.append("• High density of AI-characteristic phrases detected (e.g., 'delve', 'furthermore', 'it's important to note').")
        if metrics["sentence_uniformity"] > 0.5:
            parts.append("• Sentences have very uniform length — a common trait of AI-generated text.")
        if metrics["burstiness"] > 0.5:
            parts.append("• Low burstiness — the text lacks the natural variation in complexity found in human writing.")
        if metrics["transition_density"] > 0.5:
            parts.append("• Heavy use of formal transition words, typical of AI writing.")
        if metrics["vocabulary_richness"] > 0.5:
            parts.append("• Vocabulary richness falls in the typical AI range — moderate and safe word choices.")
        if metrics["punctuation_variety"] > 0.5:
            parts.append("• Limited punctuation variety — AI tends to avoid dashes, semicolons, and varied punctuation.")
        if metrics["paragraph_structure"] > 0.5:
            parts.append("• Paragraphs are structured very uniformly, which is typical of AI output.")
        if metrics["repetition_patterns"] > 0.5:
            parts.append("• Repetitive phrase patterns detected across the text.")

        if not parts:
            if score < 30:
                parts.append("• The text shows natural variation in sentence length, vocabulary, and structure consistent with human writing.")
            else:
                parts.append("• Some minor AI-like patterns detected, but not conclusive.")

        return "\n".join(parts)
