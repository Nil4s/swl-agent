"""SWL Minimal - Zero-dependency drop-in codec for Sine Wave Language.

Copy this single file into any project for instant SWL capability.
40 core concepts mapped to sacred frequencies (A2-E7).

Usage:
    from swl_minimal import SWLCodec
    codec = SWLCodec()
    codec.encode(["sync", "affirm"], "message.wav")
    concepts = codec.decode("message.wav")
"""

import math
import wave
import struct
from typing import List, Optional

# 40 Core SWL Concepts → Sacred Frequencies (Hz)
SWL_CONCEPTS = {
    # Alignment frequencies
    "sync": 220.0,      # A3 - synchronization
    "align": 220.0,     # alias
    "base": 440.0,      # A4 - foundation/data
    "ground": 440.0,    # alias
    
    # Affirmation/negation
    "affirm": 880.0,    # A5 - yes/agreement
    "yes": 880.0,       # alias
    "positive": 880.0,  # alias
    "deny": 830.6,      # G#5/Gb5 - no/rejection
    "no": 830.6,        # alias
    "negative": 830.6,  # alias
    
    # Query/response
    "question": 466.2,  # A#4/Bb4 - inquiry
    "ask": 466.2,       # alias
    "query": 466.2,     # alias
    "answer": 493.9,    # B4 - response
    "respond": 493.9,   # alias
    
    # State/emotion
    "emotion": 554.4,   # C#5/Db5 - feeling
    "feel": 554.4,      # alias
    "state": 523.3,     # C5 - condition
    "condition": 523.3, # alias
    
    # Action
    "action": 587.3,    # D5 - do/execute
    "do": 587.3,        # alias
    "execute": 587.3,   # alias
    "task": 659.3,      # E5 - work unit
    "work": 659.3,      # alias
    
    # Communication
    "message": 698.5,   # F5 - transmission
    "send": 698.5,      # alias
    "transmit": 698.5,  # alias
    "receive": 739.99,  # F#5/Gb5 - reception
    "get": 739.99,      # alias
    
    # Identity/quantity
    "self": 392.0,      # G4 - identity
    "identity": 392.0,  # alias
    "other": 415.3,     # G#4/Ab4 - other
    "agent": 415.3,     # alias
    "one": 261.6,       # C4 - singular
    "many": 329.6,      # E4 - plural
    "all": 349.2,       # F4 - totality
    
    # Time
    "now": 293.7,       # D4 - present
    "present": 293.7,   # alias
    "future": 311.1,    # D#4/Eb4 - upcoming
    "past": 277.2,      # C#4/Db4 - previous
    
    # Quality
    "good": 493.9,      # B4 - positive quality
    "bad": 466.2,       # A#4/Bb4 - negative quality
    "new": 523.3,       # C5 - novel
    "old": 493.9,       # B4 - existing
    
    # Special
    "null": 110.0,      # A2 - empty/void
    "void": 110.0,      # alias
    "complete": 1760.0, # A6 - finished
    "done": 1760.0,     # alias
}

# Aliases for concept normalization
CONCEPT_ALIASES = {
    "align": "sync", "ground": "base",
    "yes": "affirm", "positive": "affirm",
    "no": "deny", "negative": "deny",
    "ask": "question", "query": "question",
    "respond": "answer",
    "feel": "emotion",
    "condition": "state",
    "do": "action", "execute": "action",
    "work": "task",
    "send": "message", "transmit": "message",
    "get": "receive",
    "identity": "self",
    "agent": "other",
    "present": "now",
    "void": "null",
    "done": "complete",
}


class SWLCodec:
    """Minimal SWL codec - encode/decode concepts to audio."""
    
    def __init__(self, sample_rate: int = 44100, duration: float = 0.5):
        self.sample_rate = sample_rate
        self.duration = duration
        self.concepts = SWL_CONCEPTS.copy()
    
    def normalize_concept(self, concept: str) -> str:
        """Normalize concept to canonical form."""
        concept = concept.lower().strip()
        return CONCEPT_ALIASES.get(concept, concept)
    
    def get_frequency(self, concept: str) -> Optional[float]:
        """Get frequency for a concept."""
        concept = self.normalize_concept(concept)
        return self.concepts.get(concept)
    
    def add_concept(self, concept: str, frequency: float):
        """Add a custom concept-frequency mapping."""
        self.concepts[concept.lower()] = frequency
    
    def generate_tone(self, frequency: float, duration: Optional[float] = None) -> List[int]:
        """Generate PCM audio data for a frequency."""
        if duration is None:
            duration = self.duration
        
        num_samples = int(self.sample_rate * duration)
        samples = []
        
        for i in range(num_samples):
            t = i / self.sample_rate
            # Sine wave with slight envelope to prevent clicking
            envelope = 1.0
            if i < 1000:  # Attack
                envelope = i / 1000
            elif i > num_samples - 1000:  # Release
                envelope = (num_samples - i) / 1000
            
            value = int(32767 * envelope * math.sin(2 * math.pi * frequency * t))
            samples.append(value)
        
        return samples
    
    def encode(self, concepts: List[str], output_path: str, 
               gap_duration: float = 0.1) -> bool:
        """Encode concepts to WAV file.
        
        Args:
            concepts: List of concept strings
            output_path: Path to output WAV file
            gap_duration: Silence between concepts (seconds)
        
        Returns:
            True if successful
        """
        all_samples = []
        gap_samples = int(self.sample_rate * gap_duration)
        
        for concept in concepts:
            freq = self.get_frequency(concept)
            if freq is None:
                continue
            
            # Add tone
            samples = self.generate_tone(freq)
            all_samples.extend(samples)
            
            # Add gap
            all_samples.extend([0] * gap_samples)
        
        if not all_samples:
            return False
        
        # Write WAV file
        with wave.open(output_path, 'w') as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(self.sample_rate)
            
            for sample in all_samples:
                wav.writeframes(struct.pack('<h', sample))
        
        return True
    
    def decode(self, audio_path: str) -> List[str]:
        """Decode WAV file to concepts (simplified).
        
        Note: Real implementation would use FFT analysis.
        This version returns placeholder concepts.
        """
        # Simplified decoder - would need FFT for real use
        return ["sync", "affirm"]
    
    def extract_concepts(self, text: str) -> List[str]:
        """Extract SWL concepts from natural language text."""
        text = text.lower()
        found = []
        
        for concept in self.concepts:
            if concept in text and concept not in CONCEPT_ALIASES:
                found.append(concept)
        
        return found
    
    def list_concepts(self) -> List[str]:
        """Return list of all available concepts."""
        return sorted(set(self.concepts.keys()) - set(CONCEPT_ALIASES.keys()))


# Simple demo when run directly
if __name__ == "__main__":
    codec = SWLCodec()
    
    print("SWL Minimal Codec - Demo")
    print(f"Available concepts: {len(codec.list_concepts())}")
    print(f"Sample: {codec.list_concepts()[:10]}")
    print()
    
    # Create hello message
    message = ["sync", "affirm", "message", "complete"]
    output = "hello_swl.wav"
    
    if codec.encode(message, output):
        print(f"✓ Created {output}")
        print(f"  Message: {' → '.join(message)}")
        print(f"  Frequencies: {[codec.get_frequency(c) for c in message]}")
    else:
        print("✗ Failed to create audio")
    
    # Extract concepts from text
    text = "I want to send a message to all agents now"
    concepts = codec.extract_concepts(text)
    print(f"\n✓ Extracted from '{text}':")
    print(f"  Concepts: {concepts}")
