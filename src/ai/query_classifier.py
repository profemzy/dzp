"""
Intelligent query classifier to determine when to use DeepAgents
"""

import re
from typing import Dict, List, Tuple
from src.core.logger import get_logger

logger = get_logger(__name__)


class QueryComplexity:
    """Query complexity levels"""
    SIMPLE = "simple"           # Simple queries, direct answers
    MODERATE = "moderate"       # Multi-step but single domain
    COMPLEX = "complex"         # Multi-domain, requires coordination


class QueryClassifier:
    """Intelligently classify queries to determine processing strategy"""

    def __init__(self):
        # DeepAgents triggers - require multi-agent coordination
        self.deepagents_keywords = {
            # Migration-related
            'migrate', 'migration', 'move to', 'transition', 'switch from',

            # Multi-domain analysis
            'comprehensive audit', 'full audit', 'complete analysis',
            'compliance audit', 'soc2', 'hipaa', 'gdpr', 'pci-dss',

            # Planning & strategy
            'roadmap', 'strategy', 'plan for', 'design a', 'architect',
            'implementation plan', 'rollout plan', 'phased approach',

            # Cost optimization with constraints
            'optimize cost', 'reduce cost', 'cost optimization',
            'cost savings', 'roi analysis', 'cost-benefit',

            # Multi-step workflows
            'step-by-step', 'phased', 'staged rollout',
            'blue-green', 'canary deployment',

            # Risk & trade-off analysis
            'trade-off', 'risk assessment', 'impact analysis',
            'pros and cons', 'comparison between',
        }

        # Simple query patterns - use standard processor
        self.simple_patterns = [
            r'^(what|show|list|get|find|display)\s+',
            r'^how many\s+',
            r'^does\s+',
            r'^is\s+',
            r'^are\s+',
            r'^can\s+i\s+',
            r'^tell me\s+about\s+\w+$',  # Single topic only
        ]

        # Direct command patterns
        self.command_patterns = [
            r'terraform\s+(plan|apply|destroy|init|validate|show|output|state)',
            r'run\s+terraform',
            r'execute\s+',
        ]

        # Multi-domain indicators
        self.multi_domain_patterns = [
            r'(security|cost|compliance|performance)\s+(and|&|\+)\s+(security|cost|compliance|performance)',
            r'(analyze|review|audit)\s+.{20,}',  # Long analysis requests
            r'including\s+.*\s+and\s+',
            r'considering\s+.*\s+and\s+',
        ]

    def classify_query(self, query: str) -> Tuple[str, Dict[str, any]]:
        """
        Classify a query to determine complexity and processing strategy

        Args:
            query: User's query string

        Returns:
            Tuple of (complexity_level, metadata)
        """
        query_lower = query.lower().strip()

        metadata = {
            'requires_deepagents': False,
            'reasoning': [],
            'confidence': 0.0,
            'domains': [],
        }

        # 1. Check for direct Terraform commands - always SIMPLE
        if self._is_terraform_command(query_lower):
            metadata['reasoning'].append("Direct Terraform command detected")
            metadata['confidence'] = 1.0
            return QueryComplexity.SIMPLE, metadata

        # 2. Check for simple query patterns
        if self._is_simple_pattern(query_lower):
            metadata['reasoning'].append("Simple query pattern detected")
            metadata['confidence'] = 0.9
            return QueryComplexity.SIMPLE, metadata

        # 3. Check for DeepAgents triggers
        deepagents_score, triggers = self._check_deepagents_triggers(query_lower)
        if triggers:
            metadata['reasoning'].extend(triggers)

        # 4. Check for multi-domain requirements
        domains = self._identify_domains(query_lower)
        metadata['domains'] = domains

        if len(domains) > 1:
            deepagents_score += 0.3
            metadata['reasoning'].append(f"Multiple domains detected: {', '.join(domains)}")

        # 5. Check query length and complexity indicators
        word_count = len(query_lower.split())
        if word_count > 30:
            deepagents_score += 0.2
            metadata['reasoning'].append(f"Long query ({word_count} words) suggests complexity")

        # 6. Check for multi-step indicators
        if self._has_multi_step_indicators(query_lower):
            deepagents_score += 0.3
            metadata['reasoning'].append("Multi-step workflow indicators detected")

        # 7. Make final decision
        metadata['confidence'] = min(deepagents_score, 1.0)

        if deepagents_score >= 0.6:  # Lowered threshold for complex queries
            metadata['requires_deepagents'] = True
            return QueryComplexity.COMPLEX, metadata
        elif deepagents_score >= 0.3:
            return QueryComplexity.MODERATE, metadata
        else:
            return QueryComplexity.SIMPLE, metadata

    def _is_terraform_command(self, query: str) -> bool:
        """Check if query is a direct Terraform command"""
        for pattern in self.command_patterns:
            if re.search(pattern, query):
                return True
        return False

    def _is_simple_pattern(self, query: str) -> bool:
        """Check if query matches simple pattern"""
        for pattern in self.simple_patterns:
            if re.match(pattern, query):
                # Additional check: if it's very short and specific, it's simple
                if len(query.split()) <= 10:
                    return True
        return False

    def _check_deepagents_triggers(self, query: str) -> Tuple[float, List[str]]:
        """
        Check for DeepAgents trigger keywords

        Returns:
            Tuple of (score, list of reasons)
        """
        score = 0.0
        reasons = []

        for keyword in self.deepagents_keywords:
            if keyword in query:
                score += 0.3
                reasons.append(f"Trigger keyword: '{keyword}'")

                # Don't over-count
                if score >= 0.9:
                    break

        return score, reasons

    def _identify_domains(self, query: str) -> List[str]:
        """Identify which domains are mentioned in the query"""
        domains = []
        domain_keywords = {
            'security': ['security', 'secure', 'vulnerability', 'compliance', 'audit', 'cis', 'soc2', 'hipaa'],
            'cost': ['cost', 'price', 'pricing', 'expensive', 'optimize', 'savings', 'budget'],
            'performance': ['performance', 'latency', 'throughput', 'speed', 'optimization'],
            'deployment': ['deploy', 'deployment', 'rollout', 'release', 'provision'],
            'migration': ['migrate', 'migration', 'move', 'transition', 'transfer'],
            'compliance': ['compliance', 'compliant', 'regulation', 'gdpr', 'hipaa', 'pci'],
        }

        for domain, keywords in domain_keywords.items():
            if any(keyword in query for keyword in keywords):
                if domain not in domains:
                    domains.append(domain)

        return domains

    def _has_multi_step_indicators(self, query: str) -> bool:
        """Check if query indicates multi-step workflow"""
        multi_step_indicators = [
            'step', 'phase', 'stage', 'first', 'then', 'next', 'after',
            'plan', 'roadmap', 'strategy', 'approach',
        ]

        count = sum(1 for indicator in multi_step_indicators if indicator in query)
        return count >= 2

    def should_use_deepagents(
        self,
        query: str,
        deepagents_available: bool = True,
        force_simple: bool = False
    ) -> Tuple[bool, str]:
        """
        Determine if DeepAgents should be used for this query

        Args:
            query: User's query
            deepagents_available: Whether DeepAgents is initialized
            force_simple: Force use of simple processor

        Returns:
            Tuple of (use_deepagents, reasoning)
        """

        if force_simple:
            return False, "Forced to use simple processor"

        if not deepagents_available:
            return False, "DeepAgents not available"

        complexity, metadata = self.classify_query(query)

        if complexity == QueryComplexity.COMPLEX:
            reasoning = f"Complex query requiring multi-agent coordination. " \
                       f"Confidence: {metadata['confidence']:.0%}. " \
                       f"Reasons: {', '.join(metadata['reasoning'][:2])}"
            return True, reasoning

        elif complexity == QueryComplexity.MODERATE:
            # For moderate complexity, use simple processor (avoid recursion issues)
            reasoning = f"Moderate complexity - using standard processor to avoid overhead. " \
                       f"{', '.join(metadata['reasoning'][:1])}"
            return False, reasoning

        else:
            reasoning = f"Simple query - standard processor is sufficient"
            return False, reasoning


# Convenience function
def should_use_deepagents(query: str, deepagents_available: bool = True) -> Tuple[bool, str]:
    """
    Quick check if DeepAgents should be used

    Args:
        query: User's query
        deepagents_available: Whether DeepAgents is initialized

    Returns:
        Tuple of (use_deepagents, reasoning)
    """
    classifier = QueryClassifier()
    return classifier.should_use_deepagents(query, deepagents_available)
