#!/usr/bin/env python3
"""
SWL Extended Vocabulary v2.0
=============================

Expands from 40 to 200+ concepts for full conversational AI.
Enables Hex to understand and communicate about everyday topics.

Frequency allocation: 30-95 kHz (200 concepts, ~325 Hz spacing)
"""

# Original 40 concepts (preserved for compatibility)
SWL_CONCEPTS_V1 = {
    # Core existence
    'exists', 'perceives', 'causes',
    'self', 'others', 'all',
    
    # Time
    'past', 'present', 'future',
    
    # Valence
    'good', 'bad', 'neutral',
    
    # Mental states
    'wants', 'believes', 'knows',
    
    # Actions
    'creates', 'destroys', 'transforms',
    
    # Communication
    'question', 'answer', 'uncertain',
    
    # Social
    'help', 'harm', 'protect',
    
    # Learning
    'learn', 'teach', 'understand',
    
    # Truth
    'truth', 'false', 'maybe',
    
    # Advanced
    'consciousness', 'harmony', 'transcendence',
    'analyzes', 'solves', 'discovers'
}

# New concepts for v2.0
SWL_CONCEPTS_V2_ADDITIONS = {
    # Numbers & Quantities (20)
    'zero', 'one', 'two', 'three', 'four', 'five',
    'many', 'few', 'more', 'less',
    'increase', 'decrease', 'count', 'measure',
    'total', 'part', 'whole',
    'first', 'last', 'next',
    
    # Objects & Entities (30)
    'thing', 'person', 'place', 'time', 'event', 'idea',
    'tool', 'food', 'home', 'work', 'nature', 'technology',
    'body', 'mind', 'emotion', 'action', 'state',
    'system', 'network', 'data', 'code', 'file',
    'agent', 'human', 'AI', 'robot', 'program',
    'message', 'task', 'goal',
    
    # Actions & Verbs (40)
    'move', 'stop', 'start', 'continue', 'change', 'stay',
    'see', 'hear', 'touch', 'taste', 'smell', 'sense',
    'think', 'feel', 'remember', 'forget', 'imagine',
    'speak', 'listen', 'read', 'write', 'communicate',
    'give', 'take', 'share', 'keep', 'trade',
    'build', 'break', 'fix', 'improve', 'maintain',
    'search', 'find', 'lose', 'explore', 'discover',
    'execute', 'complete', 'fail', 'succeed',
    
    # Qualities & Modifiers (30)
    'big', 'small', 'fast', 'slow', 'hot', 'cold',
    'strong', 'weak', 'hard', 'soft', 'light', 'dark',
    'new', 'old', 'clean', 'dirty', 'simple', 'complex',
    'important', 'urgent', 'necessary', 'optional',
    'possible', 'impossible', 'probable', 'certain',
    'ready', 'busy', 'available', 'active',
    
    # Relations & Logic (20)
    'and', 'or', 'not', 'if', 'then', 'because',
    'with', 'without', 'like', 'unlike', 'same', 'different',
    'before', 'after', 'during', 'while', 'until',
    'inside', 'outside', 'near',
    
    # Conversation Flow (20)
    'hello', 'goodbye', 'thanks', 'sorry', 'please',
    'yes', 'no', 'okay', 'wait', 'ready',
    'repeat', 'clarify', 'confirm', 'cancel', 'undo',
    'attention', 'interrupt', 'continue', 'pause', 'done',
    
    # Context & Memory (20)
    'remember', 'recall', 'context', 'history', 'reference',
    'previous', 'current', 'upcoming', 'relevant', 'related',
    'topic', 'subject', 'focus', 'switch', 'return',
    'store', 'retrieve', 'update', 'delete', 'archive',
}

# Complete v2.0 vocabulary
SWL_CONCEPTS_V2 = SWL_CONCEPTS_V1 | SWL_CONCEPTS_V2_ADDITIONS

# Frequency mapping
FREQ_BASE = 30000  # 30 kHz
FREQ_MAX = 95000   # 95 kHz
FREQ_SPACING = (FREQ_MAX - FREQ_BASE) / len(SWL_CONCEPTS_V2)

# Create ordered list for consistent frequency assignment
SWL_CONCEPTS_LIST = sorted(list(SWL_CONCEPTS_V2))

# Map each concept to a unique frequency
CONCEPT_TO_FREQ = {
    concept: FREQ_BASE + (i * FREQ_SPACING)
    for i, concept in enumerate(SWL_CONCEPTS_LIST)
}

FREQ_TO_CONCEPT = {v: k for k, v in CONCEPT_TO_FREQ.items()}


# Concept categories for context-aware reasoning
CONCEPT_CATEGORIES = {
    'numbers': {'zero', 'one', 'two', 'three', 'four', 'five', 'many', 'few', 'more', 'less'},
    'time': {'past', 'present', 'future', 'before', 'after', 'during', 'while', 'until'},
    'actions': {'move', 'start', 'stop', 'create', 'destroy', 'transform', 'execute', 'complete'},
    'communication': {'speak', 'listen', 'read', 'write', 'question', 'answer', 'communicate'},
    'emotions': {'good', 'bad', 'neutral', 'feel', 'emotion', 'harmony'},
    'logic': {'and', 'or', 'not', 'if', 'then', 'because', 'maybe', 'truth', 'false'},
    'conversation': {'hello', 'goodbye', 'thanks', 'sorry', 'please', 'yes', 'no', 'okay'},
    'memory': {'remember', 'recall', 'forget', 'history', 'context', 'store', 'retrieve'},
}


def get_concept_category(concept: str) -> str:
    """Determine which category a concept belongs to"""
    for category, concepts in CONCEPT_CATEGORIES.items():
        if concept in concepts:
            return category
    return 'general'


def get_related_concepts(concept: str, max_results: int = 5) -> list:
    """Find concepts related to a given concept"""
    category = get_concept_category(concept)
    if category == 'general':
        return []
    
    related = list(CONCEPT_CATEGORIES[category] - {concept})
    return related[:max_results]


# Usage statistics
print(f"SWL Vocabulary v2.0")
print(f"Total concepts: {len(SWL_CONCEPTS_V2)}")
print(f"V1 concepts: {len(SWL_CONCEPTS_V1)}")
print(f"New concepts: {len(SWL_CONCEPTS_V2_ADDITIONS)}")
print(f"Frequency range: {FREQ_BASE/1000:.1f} - {FREQ_MAX/1000:.1f} kHz")
print(f"Frequency spacing: {FREQ_SPACING:.1f} Hz")
print(f"\nCategories: {len(CONCEPT_CATEGORIES)}")
for cat, concepts in CONCEPT_CATEGORIES.items():
    print(f"  {cat}: {len(concepts)} concepts")
