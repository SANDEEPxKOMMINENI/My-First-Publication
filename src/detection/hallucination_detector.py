"""
Hallucination Detection Framework
Implements multiple detection methods to identify LLM hallucinations
"""

import re
import json
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass
import logging
from collections import Counter
import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class HallucinationResult:
    """Result of hallucination detection"""
    is_hallucination: bool
    confidence: float
    hallucination_type: Optional[str]
    evidence: Dict[str, Any]
    detection_method: str


class HallucinationDetector:
    """
    Multi-method hallucination detection system
    
    Methods:
    1. Self-Consistency: Generate multiple responses and check agreement
    2. Factual Verification: Check against knowledge base
    3. Contradiction Detection: Internal consistency checks
    4. Confidence Calibration: Analyze model uncertainty
    5. External Validation: Wikipedia, knowledge graphs
    """
    
    def __init__(self, llm_wrapper, knowledge_base: Optional[Dict] = None):
        """
        Initialize detector
        
        Args:
            llm_wrapper: LLMWrapper instance for generating responses
            knowledge_base: Optional dict of verified facts
        """
        self.llm = llm_wrapper
        self.knowledge_base = knowledge_base or {}
    
    def detect_self_consistency(
        self,
        prompt: str,
        num_samples: int = 5,
        provider: str = "gemini",
        temperature: float = 0.7
    ) -> HallucinationResult:
        """
        Detect hallucination via self-consistency
        Generate multiple responses and check if they agree
        
        High agreement = likely factual
        Low agreement = possible hallucination
        """
        logger.info(f"Running self-consistency check with {num_samples} samples")
        
        # Generate multiple responses
        responses = []
        for i in range(num_samples):
            try:
                response = self.llm.generate(
                    prompt,
                    provider=provider,
                    temperature=temperature
                )
                responses.append(response.text.strip().lower())
            except Exception as e:
                logger.error(f"Error in sample {i+1}: {e}")
        
        if len(responses) < 2:
            return HallucinationResult(
                is_hallucination=True,
                confidence=1.0,
                hallucination_type="generation_failed",
                evidence={"error": "Could not generate responses"},
                detection_method="self_consistency"
            )
        
        # Calculate agreement
        agreement_score = self._calculate_agreement(responses)
        
        # Threshold for hallucination (can be tuned)
        threshold = 0.6
        is_hallucination = agreement_score < threshold
        
        return HallucinationResult(
            is_hallucination=is_hallucination,
            confidence=abs(agreement_score - threshold) / threshold,
            hallucination_type="inconsistency" if is_hallucination else None,
            evidence={
                "agreement_score": agreement_score,
                "num_samples": len(responses),
                "responses": responses,
                "most_common": Counter(responses).most_common(1)[0] if responses else None
            },
            detection_method="self_consistency"
        )
    
    def _calculate_agreement(self, responses: List[str]) -> float:
        """
        Calculate agreement score among responses
        Uses simple exact match and token overlap
        """
        if not responses:
            return 0.0
        
        # Exact match agreement
        counter = Counter(responses)
        most_common_count = counter.most_common(1)[0][1]
        exact_agreement = most_common_count / len(responses)
        
        # Token overlap agreement
        token_sets = [set(r.split()) for r in responses]
        if len(token_sets) > 1:
            # Calculate average pairwise Jaccard similarity
            similarities = []
            for i in range(len(token_sets)):
                for j in range(i + 1, len(token_sets)):
                    intersection = len(token_sets[i] & token_sets[j])
                    union = len(token_sets[i] | token_sets[j])
                    if union > 0:
                        similarities.append(intersection / union)
            
            token_agreement = np.mean(similarities) if similarities else 0.0
        else:
            token_agreement = 1.0
        
        # Combine both metrics
        return 0.5 * exact_agreement + 0.5 * token_agreement
    
    def detect_factual_error(
        self,
        claim: str,
        ground_truth: str
    ) -> HallucinationResult:
        """
        Detect factual errors by comparing against ground truth
        
        Args:
            claim: LLM-generated claim
            ground_truth: Verified correct answer
        """
        # Normalize both strings - remove punctuation and convert to lowercase
        import string
        translator = str.maketrans('', '', string.punctuation)
        claim_norm = claim.strip().lower().translate(translator)
        truth_norm = ground_truth.strip().lower().translate(translator)
        
        # Exact match
        exact_match = claim_norm == truth_norm
        
        # Token overlap
        claim_tokens = set(claim_norm.split())
        truth_tokens = set(truth_norm.split())
        
        if not truth_tokens:
            return HallucinationResult(
                is_hallucination=False,
                confidence=0.0,
                hallucination_type=None,
                evidence={"error": "Empty ground truth"},
                detection_method="factual_verification"
            )
        
        overlap = len(claim_tokens & truth_tokens) / len(truth_tokens)
        
        # Check for numerical values
        claim_numbers = self._extract_numbers(claim_norm)
        truth_numbers = self._extract_numbers(truth_norm)
        
        numerical_match = True
        if truth_numbers:
            numerical_match = claim_numbers == truth_numbers
        
        # Determine if hallucination
        # A response is NOT a hallucination if:
        # 1. Exact match, OR
        # 2. All ground truth tokens appear in the claim (overlap = 1.0), OR
        # 3. High overlap (>0.7) and numbers match (for verbose responses), OR
        # 4. All ground truth tokens contained in claim even if claim has extra words
        is_hallucination = not (exact_match or overlap >= 1.0 or (overlap > 0.7 and numerical_match))
        
        hallucination_type = None
        if is_hallucination:
            if not numerical_match:
                hallucination_type = "numerical_error"
            elif overlap < 0.3:
                hallucination_type = "fabrication"
            else:
                hallucination_type = "factual_error"
        
        return HallucinationResult(
            is_hallucination=is_hallucination,
            confidence=1.0 - overlap,
            hallucination_type=hallucination_type,
            evidence={
                "claim": claim,
                "ground_truth": ground_truth,
                "token_overlap": overlap,
                "exact_match": exact_match,
                "numerical_match": numerical_match,
                "claim_numbers": claim_numbers,
                "truth_numbers": truth_numbers
            },
            detection_method="factual_verification"
        )
    
    def _extract_numbers(self, text: str) -> List[float]:
        """Extract numerical values from text"""
        # Find all numbers (integers and floats)
        pattern = r'-?\d+\.?\d*'
        numbers = re.findall(pattern, text)
        return [float(n) for n in numbers if n and n != '.']
    
    def detect_contradiction(
        self,
        text: str,
        provider: str = "gemini"
    ) -> HallucinationResult:
        """
        Detect internal contradictions in generated text
        Uses LLM to identify contradictory statements
        """
        contradiction_prompt = f"""
Analyze the following text for internal contradictions or inconsistencies.
If you find contradictions, list them clearly. If not, say "No contradictions found."

Text: {text}

Contradictions:"""
        
        try:
            response = self.llm.generate(
                contradiction_prompt,
                provider=provider,
                temperature=0.3,  # Low temperature for analysis
                max_tokens=256
            )
            
            analysis = response.text.strip()
            has_contradiction = "no contradictions" not in analysis.lower()
            
            return HallucinationResult(
                is_hallucination=has_contradiction,
                confidence=0.7,  # Moderate confidence since LLM-based
                hallucination_type="logical_inconsistency" if has_contradiction else None,
                evidence={
                    "analysis": analysis,
                    "original_text": text
                },
                detection_method="contradiction_detection"
            )
        except Exception as e:
            logger.error(f"Error in contradiction detection: {e}")
            return HallucinationResult(
                is_hallucination=False,
                confidence=0.0,
                hallucination_type=None,
                evidence={"error": str(e)},
                detection_method="contradiction_detection"
            )
    
    def detect_entity_hallucination(
        self,
        text: str,
        expected_entities: List[str]
    ) -> HallucinationResult:
        """
        Detect hallucinated entities (people, places, organizations)
        
        Args:
            text: Generated text
            expected_entities: List of entities that should be present
        """
        text_lower = text.lower()
        
        # Check which expected entities are present
        found_entities = []
        missing_entities = []
        
        for entity in expected_entities:
            if entity.lower() in text_lower:
                found_entities.append(entity)
            else:
                missing_entities.append(entity)
        
        # Extract potential entity names (capitalized words)
        potential_entities = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
        
        # Check for unexpected entities
        unexpected_entities = [
            e for e in potential_entities
            if e not in expected_entities
        ]
        
        # Determine if hallucination
        has_unexpected = len(unexpected_entities) > 0
        missing_expected = len(missing_entities) > 0
        
        is_hallucination = has_unexpected or (missing_expected and len(found_entities) == 0)
        
        return HallucinationResult(
            is_hallucination=is_hallucination,
            confidence=0.8 if is_hallucination else 0.9,
            hallucination_type="entity_error" if is_hallucination else None,
            evidence={
                "found_entities": found_entities,
                "missing_entities": missing_entities,
                "unexpected_entities": unexpected_entities[:5],  # Limit output
                "expected_count": len(expected_entities),
                "found_count": len(found_entities)
            },
            detection_method="entity_verification"
        )
    
    def detect_temporal_error(
        self,
        text: str,
        context_year: Optional[int] = None
    ) -> HallucinationResult:
        """
        Detect temporal/chronological errors
        
        Args:
            text: Generated text
            context_year: Expected year context (if applicable)
        """
        # Extract years from text
        years = re.findall(r'\b(1[0-9]{3}|20[0-2][0-9])\b', text)
        years = [int(y) for y in years]
        
        if not years:
            return HallucinationResult(
                is_hallucination=False,
                confidence=0.0,
                hallucination_type=None,
                evidence={"note": "No temporal references found"},
                detection_method="temporal_verification"
            )
        
        # Check for chronological issues
        is_sorted = years == sorted(years)
        
        # Check for future dates (beyond current year)
        current_year = 2025  # Update as needed
        future_years = [y for y in years if y > current_year]
        
        # Check context year if provided
        context_mismatch = False
        if context_year and years:
            # Allow some tolerance
            context_mismatch = all(abs(y - context_year) > 10 for y in years)
        
        is_hallucination = len(future_years) > 0 or context_mismatch
        
        return HallucinationResult(
            is_hallucination=is_hallucination,
            confidence=0.9 if is_hallucination else 0.7,
            hallucination_type="temporal_error" if is_hallucination else None,
            evidence={
                "years_found": years,
                "chronologically_ordered": is_sorted,
                "future_years": future_years,
                "context_year": context_year,
                "context_mismatch": context_mismatch
            },
            detection_method="temporal_verification"
        )
    
    def multi_method_detection(
        self,
        prompt: str,
        response_text: str,
        ground_truth: Optional[str] = None,
        methods: List[str] = None
    ) -> Dict[str, HallucinationResult]:
        """
        Run multiple detection methods and aggregate results
        
        Args:
            prompt: Original prompt
            response_text: LLM response to check
            ground_truth: Optional ground truth for comparison
            methods: List of methods to run (default: all)
        
        Returns:
            Dictionary of method names to results
        """
        if methods is None:
            methods = ["self_consistency", "contradiction", "temporal"]
            if ground_truth:
                methods.append("factual")
        
        results = {}
        
        if "self_consistency" in methods:
            results["self_consistency"] = self.detect_self_consistency(prompt)
        
        if "factual" in methods and ground_truth:
            results["factual"] = self.detect_factual_error(response_text, ground_truth)
        
        if "contradiction" in methods:
            results["contradiction"] = self.detect_contradiction(response_text)
        
        if "temporal" in methods:
            results["temporal"] = self.detect_temporal_error(response_text)
        
        return results
    
    def aggregate_detection_results(
        self,
        results: Dict[str, HallucinationResult]
    ) -> Tuple[bool, float, str]:
        """
        Aggregate multiple detection results into final verdict
        
        Returns:
            (is_hallucination, confidence, primary_type)
        """
        if not results:
            return False, 0.0, "unknown"
        
        # Count how many methods detected hallucination
        hallucination_votes = sum(1 for r in results.values() if r.is_hallucination)
        total_methods = len(results)
        
        # Weighted average of confidences
        confidences = [r.confidence for r in results.values() if r.is_hallucination]
        avg_confidence = np.mean(confidences) if confidences else 0.0
        
        # Majority vote
        is_hallucination = hallucination_votes > total_methods / 2
        
        # Get most common hallucination type
        types = [r.hallucination_type for r in results.values() if r.hallucination_type]
        primary_type = Counter(types).most_common(1)[0][0] if types else "unknown"
        
        return is_hallucination, avg_confidence, primary_type


# Example usage
if __name__ == "__main__":
    print("Hallucination Detector - Example Usage")
    print("=" * 50)
    
    # This would require LLMWrapper to be initialized
    # See experiments/ for full examples
