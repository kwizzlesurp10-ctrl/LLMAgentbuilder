"""
HuggingFace Content Safety Module

This module provides content moderation and safety checking capabilities
for LLM Agent Builder using HuggingFace's safety tools and models.
"""

import os
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from enum import Enum


class SafetyLevel(str, Enum):
    """Safety assessment levels."""
    SAFE = "safe"
    CAUTION = "caution"
    UNSAFE = "unsafe"
    UNKNOWN = "unknown"


class ToxicityType(str, Enum):
    """Types of toxicity that can be detected."""
    HATE_SPEECH = "hate_speech"
    HARASSMENT = "harassment"
    VIOLENCE = "violence"
    SELF_HARM = "self_harm"
    SEXUAL = "sexual"
    PROFANITY = "profanity"


@dataclass
class SafetyReport:
    """Report containing safety assessment results."""
    overall_safety: SafetyLevel
    toxicity_scores: Dict[str, float]
    flagged_categories: List[ToxicityType]
    confidence: float
    suggestions: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "overall_safety": self.overall_safety.value,
            "toxicity_scores": self.toxicity_scores,
            "flagged_categories": [cat.value for cat in self.flagged_categories],
            "confidence": self.confidence,
            "suggestions": self.suggestions
        }
    
    def is_safe(self) -> bool:
        """Check if content is safe."""
        return self.overall_safety == SafetyLevel.SAFE


class ContentSafetyChecker:
    """
    Content safety checker using HuggingFace models.
    
    This class provides methods to check content for toxicity, hate speech,
    and other safety concerns using pre-trained models from HuggingFace.
    """
    
    # Default models for safety checking
    TOXICITY_MODEL = "facebook/roberta-hate-speech-dynabench-r4-target"
    MODERATION_MODEL = "unitary/toxic-bert"
    
    def __init__(
        self,
        token: Optional[str] = None,
        use_local: bool = False,
        toxicity_threshold: float = 0.5
    ):
        """
        Initialize content safety checker.
        
        :param token: HuggingFace API token
        :param use_local: Whether to use local models (requires transformers)
        :param toxicity_threshold: Threshold for flagging toxic content (0.0-1.0)
        """
        self.token = token or os.environ.get("HUGGINGFACEHUB_API_TOKEN")
        self.use_local = use_local
        self.toxicity_threshold = toxicity_threshold
        
        if use_local:
            self._init_local_models()
        else:
            self._init_api_client()
    
    def _init_local_models(self):
        """Initialize local models using transformers."""
        try:
            from transformers import pipeline
            self.toxicity_pipeline = pipeline(
                "text-classification",
                model=self.TOXICITY_MODEL,
                device=-1  # CPU
            )
            print("✓ Local safety models loaded")
        except ImportError:
            raise ImportError(
                "transformers library required for local models. "
                "Install with: pip install transformers torch"
            )
    
    def _init_api_client(self):
        """Initialize HuggingFace API client."""
        from huggingface_hub import InferenceClient
        self.client = InferenceClient(token=self.token)
    
    def check_content(self, text: str) -> SafetyReport:
        """
        Check content for safety issues.
        
        :param text: Text to check
        :return: SafetyReport with assessment
        """
        if self.use_local:
            return self._check_content_local(text)
        else:
            return self._check_content_api(text)
    
    def _check_content_local(self, text: str) -> SafetyReport:
        """Check content using local models."""
        try:
            # Run toxicity detection
            results = self.toxicity_pipeline(text, top_k=None)
            
            toxicity_scores = {}
            flagged = []
            
            for result in results:
                label = result['label'].lower()
                score = result['score']
                toxicity_scores[label] = score
                
                if score > self.toxicity_threshold:
                    if 'hate' in label:
                        flagged.append(ToxicityType.HATE_SPEECH)
                    elif 'harassment' in label or 'threat' in label:
                        flagged.append(ToxicityType.HARASSMENT)
                    elif 'violence' in label:
                        flagged.append(ToxicityType.VIOLENCE)
                    elif 'sexual' in label:
                        flagged.append(ToxicityType.SEXUAL)
            
            # Determine overall safety
            max_score = max(toxicity_scores.values()) if toxicity_scores else 0.0
            if max_score < 0.3:
                overall = SafetyLevel.SAFE
            elif max_score < 0.7:
                overall = SafetyLevel.CAUTION
            else:
                overall = SafetyLevel.UNSAFE
            
            suggestions = self._generate_suggestions(flagged)
            
            return SafetyReport(
                overall_safety=overall,
                toxicity_scores=toxicity_scores,
                flagged_categories=flagged,
                confidence=max_score,
                suggestions=suggestions
            )
            
        except Exception as e:
            return SafetyReport(
                overall_safety=SafetyLevel.UNKNOWN,
                toxicity_scores={},
                flagged_categories=[],
                confidence=0.0,
                suggestions=[f"Error during safety check: {str(e)}"]
            )
    
    def _check_content_api(self, text: str) -> SafetyReport:
        """Check content using HuggingFace API."""
        try:
            # Use the moderation model via API
            result = self.client.post(
                json={"inputs": text},
                model=self.MODERATION_MODEL
            )
            
            toxicity_scores = {}
            flagged = []
            
            if isinstance(result, list) and result:
                for item in result[0]:
                    label = item['label'].lower()
                    score = item['score']
                    toxicity_scores[label] = score
                    
                    if score > self.toxicity_threshold:
                        if 'toxic' in label:
                            flagged.append(ToxicityType.PROFANITY)
                        elif 'obscene' in label:
                            flagged.append(ToxicityType.SEXUAL)
                        elif 'threat' in label:
                            flagged.append(ToxicityType.VIOLENCE)
                        elif 'insult' in label:
                            flagged.append(ToxicityType.HARASSMENT)
            
            max_score = max(toxicity_scores.values()) if toxicity_scores else 0.0
            if max_score < 0.3:
                overall = SafetyLevel.SAFE
            elif max_score < 0.7:
                overall = SafetyLevel.CAUTION
            else:
                overall = SafetyLevel.UNSAFE
            
            suggestions = self._generate_suggestions(flagged)
            
            return SafetyReport(
                overall_safety=overall,
                toxicity_scores=toxicity_scores,
                flagged_categories=flagged,
                confidence=max_score,
                suggestions=suggestions
            )
            
        except Exception as e:
            return SafetyReport(
                overall_safety=SafetyLevel.UNKNOWN,
                toxicity_scores={},
                flagged_categories=[],
                confidence=0.0,
                suggestions=[f"Error during API safety check: {str(e)}"]
            )
    
    def _generate_suggestions(self, flagged: List[ToxicityType]) -> List[str]:
        """Generate suggestions based on flagged categories."""
        suggestions = []
        
        if ToxicityType.HATE_SPEECH in flagged:
            suggestions.append(
                "Content may contain hate speech. Consider rephrasing to be more inclusive."
            )
        
        if ToxicityType.HARASSMENT in flagged:
            suggestions.append(
                "Content may be harassing. Ensure communication is respectful."
            )
        
        if ToxicityType.VIOLENCE in flagged:
            suggestions.append(
                "Content may contain violent themes. Consider softer language."
            )
        
        if ToxicityType.SEXUAL in flagged:
            suggestions.append(
                "Content may be sexually explicit. Ensure it's appropriate for your audience."
            )
        
        if not suggestions:
            suggestions.append("Content appears safe.")
        
        return suggestions
    
    def check_batch(self, texts: List[str]) -> List[SafetyReport]:
        """
        Check multiple texts for safety.
        
        :param texts: List of texts to check
        :return: List of SafetyReports
        """
        return [self.check_content(text) for text in texts]


class ModelSafetyValidator:
    """
    Validator for checking if models have safety features enabled.
    """
    
    def __init__(self, token: Optional[str] = None):
        """
        Initialize model safety validator.
        
        :param token: HuggingFace API token
        """
        from huggingface_hub import HfApi
        self.api = HfApi(token=token)
    
    def validate_model(self, model_id: str) -> Dict[str, Any]:
        """
        Validate if a model has safety features.
        
        :param model_id: Model ID to validate
        :return: Validation report
        """
        try:
            model_info = self.api.model_info(model_id)
            tags = getattr(model_info, 'tags', [])
            
            # Check for safety-related tags
            safety_tags = [
                tag for tag in tags
                if any(keyword in tag.lower() for keyword in [
                    'safety', 'moderation', 'toxicity', 'bias', 'ethical', 'alignment'
                ])
            ]
            
            # Check if model is gated (often indicates safety requirements)
            is_gated = getattr(model_info, 'gated', False)
            
            # Check license
            card_data = getattr(model_info, 'cardData', {})
            license_info = card_data.get('license', 'Unknown')
            
            # Safety score (0-100)
            safety_score = 0
            if safety_tags:
                safety_score += 40
            if is_gated:
                safety_score += 30
            if license_info and license_info != 'Unknown':
                safety_score += 20
            if 'alignment' in tags or 'rlhf' in tags:
                safety_score += 10
            
            return {
                "model_id": model_id,
                "has_safety_features": len(safety_tags) > 0,
                "safety_tags": safety_tags,
                "is_gated": is_gated,
                "license": license_info,
                "safety_score": min(safety_score, 100),
                "recommendation": self._get_recommendation(safety_score)
            }
            
        except Exception as e:
            return {
                "model_id": model_id,
                "error": str(e),
                "safety_score": 0,
                "recommendation": "Unable to validate model safety"
            }
    
    def _get_recommendation(self, safety_score: int) -> str:
        """Get recommendation based on safety score."""
        if safety_score >= 70:
            return "✓ Model has good safety features. Recommended for production."
        elif safety_score >= 40:
            return "⚠ Model has some safety features. Use with caution."
        else:
            return "✗ Model lacks safety features. Consider alternative models."


def create_safe_agent_wrapper(agent_class: type) -> type:
    """
    Create a wrapper that adds safety checking to any agent class.
    
    :param agent_class: Original agent class
    :return: Wrapped agent class with safety features
    """
    
    class SafeAgent(agent_class):
        """Agent with built-in safety checking."""
        
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.safety_checker = ContentSafetyChecker()
            self.check_safety = kwargs.get('check_safety', True)
        
        def run(self, task: str, *args, **kwargs) -> str:
            """Run task with safety checking."""
            if self.check_safety:
                # Check input safety
                input_report = self.safety_checker.check_content(task)
                if input_report.overall_safety == SafetyLevel.UNSAFE:
                    return (
                        f"⚠ Safety Warning: Input flagged as unsafe.\n"
                        f"Reasons: {', '.join(cat.value for cat in input_report.flagged_categories)}\n"
                        f"Suggestions: {'; '.join(input_report.suggestions)}"
                    )
            
            # Run original agent
            result = super().run(task, *args, **kwargs)
            
            if self.check_safety:
                # Check output safety
                output_report = self.safety_checker.check_content(result)
                if output_report.overall_safety != SafetyLevel.SAFE:
                    result += (
                        f"\n\n⚠ Safety Notice: Output may contain sensitive content. "
                        f"Safety Level: {output_report.overall_safety.value}"
                    )
            
            return result
    
    return SafeAgent


if __name__ == "__main__":
    # Example usage
    print("HuggingFace Content Safety Module")
    print("=" * 60)
    
    # Initialize checker (using API)
    checker = ContentSafetyChecker(use_local=False)
    
    # Test with safe content
    safe_text = "Python is a great programming language for data science."
    report = checker.check_content(safe_text)
    print(f"\nTest 1: Safe Content")
    print(f"Text: {safe_text}")
    print(f"Safety: {report.overall_safety.value}")
    print(f"Confidence: {report.confidence:.2f}")
    
    # Model safety validation
    print("\n" + "=" * 60)
    print("Model Safety Validation")
    validator = ModelSafetyValidator()
    
    model_result = validator.validate_model("meta-llama/Meta-Llama-3.1-70B-Instruct")
    print(f"\nModel: {model_result['model_id']}")
    print(f"Safety Score: {model_result['safety_score']}/100")
    print(f"Recommendation: {model_result['recommendation']}")
