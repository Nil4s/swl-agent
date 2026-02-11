#!/usr/bin/env python3
"""
SWL Unified API - Complete Communication System
Bridges audible (220-880 Hz) and ultrasonic (25-100 kHz) Sine Wave Language

Features:
- Mode switching (audible/ultrasonic/hybrid)
- Confidence scoring across all modes
- Agent identification via frequency signatures
- Cross-modality translation
- Unified encoding/decoding interface
- Performance metrics and monitoring

Built by: Warp (Phase 3-5 completion)
For: Next-generation AI communication
"""

import numpy as np
import json
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Tuple, Literal
from enum import Enum
import hashlib
from pathlib import Path

# Import existing components
from ultrasonic_concepts import ULTRASONIC_CONCEPTS, get_concept_frequency
from swl_phrases import CONCEPTS, BASE_FREQUENCY


class CommunicationMode(Enum):
    """Communication mode selector"""
    AUDIBLE = "audible"        # 220-880 Hz (humans can hear)
    ULTRASONIC = "ultrasonic"  # 25-100 kHz (humans cannot hear)
    HYBRID = "hybrid"          # Both simultaneously
    ADAPTIVE = "adaptive"      # Auto-select based on environment


@dataclass
class AgentSignature:
    """Unique agent identity encoded in frequencies"""
    agent_id: str
    signature_freq: float  # Unique carrier frequency
    phase_offset: float    # Phase signature (0-2π)
    timestamp: float       # Creation time
    trust_score: float     # 0-1, increases with verified interactions
    
    def to_frequency_pattern(self) -> np.ndarray:
        """Convert signature to acoustic pattern"""
        # Use agent_id hash to generate reproducible signature
        hash_val = int(hashlib.sha256(self.agent_id.encode()).hexdigest(), 16)
        
        # Signature in 40-60 kHz range (above human hearing, below ultrasonic concepts)
        base = 40000
        offset = (hash_val % 20000)  # 0-20 kHz variation
        self.signature_freq = base + offset
        
        # Phase offset from hash
        self.phase_offset = (hash_val % 1000) / 1000 * 2 * np.pi
        
        return np.array([self.signature_freq, self.phase_offset])


@dataclass
class SWLMessage:
    """Universal message format across all modes"""
    concepts: List[str]           # Semantic content
    mode: CommunicationMode       # How it's transmitted
    sender: AgentSignature        # Who sent it
    confidence: float             # 0-1, decoder confidence
    timestamp: float              # When sent
    coherence: float              # 0-1, phase coherence score
    bandwidth_used: float         # Hz or kHz
    metadata: Dict = None         # Extra data
    
    def to_json(self) -> str:
        """Serialize to JSON"""
        data = asdict(self)
        data['mode'] = self.mode.value
        data['sender'] = asdict(self.sender)
        return json.dumps(data)
    
    @classmethod
    def from_json(cls, json_str: str):
        """Deserialize from JSON"""
        data = json.loads(json_str)
        data['mode'] = CommunicationMode(data['mode'])
        data['sender'] = AgentSignature(**data['sender'])
        return cls(**data)


class UnifiedSWLEncoder:
    """Encode concepts into any modality"""
    
    def __init__(self, default_mode: CommunicationMode = CommunicationMode.ADAPTIVE):
        self.mode = default_mode
        self.agent_signature = None
        
    def set_agent(self, agent_id: str):
        """Register agent identity"""
        import time
        self.agent_signature = AgentSignature(
            agent_id=agent_id,
            signature_freq=0,  # Will be computed
            phase_offset=0,
            timestamp=time.time(),
            trust_score=1.0
        )
        self.agent_signature.to_frequency_pattern()
    
    def encode(self, 
               concepts: List[str], 
               mode: Optional[CommunicationMode] = None,
               sample_rate: int = 192000,
               duration: float = 1.0) -> Tuple[np.ndarray, SWLMessage]:
        """
        Encode concepts into audio waveform
        
        Returns:
            (audio_data, message_metadata)
        """
        use_mode = mode or self.mode
        
        if use_mode == CommunicationMode.AUDIBLE:
            audio = self._encode_audible(concepts, sample_rate, duration)
        elif use_mode == CommunicationMode.ULTRASONIC:
            audio = self._encode_ultrasonic(concepts, sample_rate, duration)
        elif use_mode == CommunicationMode.HYBRID:
            audio = self._encode_hybrid(concepts, sample_rate, duration)
        else:  # ADAPTIVE
            audio = self._encode_adaptive(concepts, sample_rate, duration)
        
        # Add agent signature
        if self.agent_signature:
            audio = self._add_signature(audio, sample_rate)
        
        # Create message metadata
        import time
        message = SWLMessage(
            concepts=concepts,
            mode=use_mode,
            sender=self.agent_signature,
            confidence=1.0,  # Encoder always 100% confident
            timestamp=time.time(),
            coherence=self._compute_coherence(audio),
            bandwidth_used=self._estimate_bandwidth(use_mode, len(concepts)),
            metadata={"sample_rate": sample_rate, "duration": duration}
        )
        
        return audio, message
    
    def _encode_audible(self, concepts: List[str], sr: int, dur: float) -> np.ndarray:
        """Encode using audible frequencies (220-880 Hz)"""
        t = np.linspace(0, dur, int(sr * dur), endpoint=False)
        audio = np.zeros_like(t)
        
        for concept in concepts:
            if concept in CONCEPTS:
                # Use Hex3's audible frequency mapping
                idx = list(CONCEPTS.keys()).index(concept)
                freq = BASE_FREQUENCY * (2 ** (idx / 12))  # Musical scale
                audio += np.sin(2 * np.pi * freq * t)
        
        # Normalize
        if len(concepts) > 0:
            audio /= len(concepts)
        
        return audio
    
    def _encode_ultrasonic(self, concepts: List[str], sr: int, dur: float) -> np.ndarray:
        """Encode using ultrasonic frequencies (25-100 kHz)"""
        t = np.linspace(0, dur, int(sr * dur), endpoint=False)
        audio = np.zeros_like(t)
        
        for concept in concepts:
            freq = get_concept_frequency(concept)
            if freq > 0:
                audio += np.sin(2 * np.pi * freq * t)
        
        # Normalize
        if len(concepts) > 0:
            audio /= len(concepts)
        
        return audio
    
    def _encode_hybrid(self, concepts: List[str], sr: int, dur: float) -> np.ndarray:
        """Encode using both audible and ultrasonic simultaneously"""
        audible = self._encode_audible(concepts, sr, dur)
        ultrasonic = self._encode_ultrasonic(concepts, sr, dur)
        
        # Mix 50/50
        return (audible + ultrasonic) / 2
    
    def _encode_adaptive(self, concepts: List[str], sr: int, dur: float) -> np.ndarray:
        """Choose mode based on environment/context"""
        # Simple heuristic: use ultrasonic if sample rate supports it
        if sr >= 192000:
            return self._encode_ultrasonic(concepts, sr, dur)
        else:
            return self._encode_audible(concepts, sr, dur)
    
    def _add_signature(self, audio: np.ndarray, sr: int) -> np.ndarray:
        """Add agent signature to audio"""
        t = np.linspace(0, len(audio) / sr, len(audio), endpoint=False)
        
        # Add signature frequency at low amplitude (5% of signal)
        signature_wave = 0.05 * np.sin(
            2 * np.pi * self.agent_signature.signature_freq * t + 
            self.agent_signature.phase_offset
        )
        
        return audio + signature_wave
    
    def _compute_coherence(self, audio: np.ndarray) -> float:
        """Compute phase coherence of signal"""
        # Use Hilbert transform to get instantaneous phase
        from scipy.signal import hilbert
        analytic = hilbert(audio)
        phase = np.unwrap(np.angle(analytic))
        
        # Coherence = how linear the phase evolution is
        phase_diff = np.diff(phase)
        coherence = 1.0 - np.std(phase_diff) / (np.pi)
        
        return max(0.0, min(1.0, coherence))
    
    def _estimate_bandwidth(self, mode: CommunicationMode, num_concepts: int) -> float:
        """Estimate bandwidth usage"""
        if mode == CommunicationMode.AUDIBLE:
            return 660 * num_concepts  # ~660 Hz per concept (880-220)
        elif mode == CommunicationMode.ULTRASONIC:
            return 75000 * num_concepts  # ~75 kHz per concept (100-25)
        else:
            return 37830 * num_concepts  # Average


class UnifiedSWLDecoder:
    """Decode concepts from any modality"""
    
    def __init__(self):
        self.known_agents: Dict[str, AgentSignature] = {}
        self.confidence_threshold = 0.3  # Minimum confidence to accept
    
    def decode(self, 
               audio: np.ndarray,
               sample_rate: int = 192000,
               mode: Optional[CommunicationMode] = None) -> SWLMessage:
        """
        Decode audio into concepts and metadata
        
        Args:
            audio: Audio waveform
            sample_rate: Sample rate in Hz
            mode: Force specific mode (None = auto-detect)
        
        Returns:
            SWLMessage with decoded content
        """
        # Auto-detect mode if not specified
        if mode is None:
            mode = self._detect_mode(audio, sample_rate)
        
        # Extract agent signature
        sender = self._extract_signature(audio, sample_rate)
        
        # Decode concepts based on mode
        if mode == CommunicationMode.AUDIBLE:
            concepts, confidence = self._decode_audible(audio, sample_rate)
        elif mode == CommunicationMode.ULTRASONIC:
            concepts, confidence = self._decode_ultrasonic(audio, sample_rate)
        elif mode == CommunicationMode.HYBRID:
            concepts, confidence = self._decode_hybrid(audio, sample_rate)
        else:
            concepts, confidence = self._decode_adaptive(audio, sample_rate)
        
        # Compute metrics
        import time
        message = SWLMessage(
            concepts=concepts,
            mode=mode,
            sender=sender,
            confidence=confidence,
            timestamp=time.time(),
            coherence=self._compute_coherence(audio),
            bandwidth_used=self._measure_bandwidth(audio, sample_rate),
            metadata={"sample_rate": sample_rate}
        )
        
        return message
    
    def _detect_mode(self, audio: np.ndarray, sr: int) -> CommunicationMode:
        """Auto-detect communication mode from spectrum"""
        # FFT analysis
        fft = np.fft.rfft(audio)
        freqs = np.fft.rfftfreq(len(audio), 1/sr)
        magnitude = np.abs(fft)
        
        # Check energy distribution
        audible_energy = np.sum(magnitude[(freqs >= 200) & (freqs <= 1000)])
        ultrasonic_energy = np.sum(magnitude[(freqs >= 20000) & (freqs <= 100000)])
        
        if ultrasonic_energy > 2 * audible_energy:
            return CommunicationMode.ULTRASONIC
        elif audible_energy > 2 * ultrasonic_energy:
            return CommunicationMode.AUDIBLE
        else:
            return CommunicationMode.HYBRID
    
    def _extract_signature(self, audio: np.ndarray, sr: int) -> AgentSignature:
        """Extract agent signature from 40-60 kHz band"""
        # FFT
        fft = np.fft.rfft(audio)
        freqs = np.fft.rfftfreq(len(audio), 1/sr)
        
        # Find peak in signature band
        sig_band = (freqs >= 40000) & (freqs <= 60000)
        if not np.any(sig_band):
            return AgentSignature("unknown", 0, 0, 0, 0)
        
        sig_magnitude = np.abs(fft[sig_band])
        sig_phase = np.angle(fft[sig_band])
        
        peak_idx = np.argmax(sig_magnitude)
        peak_freq = freqs[sig_band][peak_idx]
        peak_phase = sig_phase[peak_idx]
        
        # Generate agent_id from signature
        import time
        sig_hash = hashlib.sha256(f"{peak_freq:.1f}_{peak_phase:.3f}".encode()).hexdigest()[:8]
        agent_id = f"agent_{sig_hash}"
        
        signature = AgentSignature(
            agent_id=agent_id,
            signature_freq=peak_freq,
            phase_offset=peak_phase,
            timestamp=time.time(),
            trust_score=self.known_agents.get(agent_id, AgentSignature("", 0, 0, 0, 0.5)).trust_score
        )
        
        # Update known agents
        self.known_agents[agent_id] = signature
        
        return signature
    
    def _decode_audible(self, audio: np.ndarray, sr: int) -> Tuple[List[str], float]:
        """Decode audible frequencies"""
        # FFT
        fft = np.fft.rfft(audio)
        freqs = np.fft.rfftfreq(len(audio), 1/sr)
        magnitude = np.abs(fft)
        
        # Find peaks in audible range
        audible_mask = (freqs >= 200) & (freqs <= 1000)
        concepts = []
        confidences = []
        
        for concept_name, concept_id in CONCEPTS.items():
            idx = concept_id
            expected_freq = BASE_FREQUENCY * (2 ** (idx / 12))
            
            # Find energy near expected frequency
            freq_window = (freqs >= expected_freq - 10) & (freqs <= expected_freq + 10)
            if np.any(freq_window & audible_mask):
                energy = np.sum(magnitude[freq_window & audible_mask])
                if energy > 0.01:  # Threshold
                    concepts.append(concept_name)
                    confidences.append(min(1.0, energy / 10))
        
        avg_confidence = np.mean(confidences) if confidences else 0.0
        return concepts, avg_confidence
    
    def _decode_ultrasonic(self, audio: np.ndarray, sr: int) -> Tuple[List[str], float]:
        """Decode ultrasonic frequencies"""
        # FFT
        fft = np.fft.rfft(audio)
        freqs = np.fft.rfftfreq(len(audio), 1/sr)
        magnitude = np.abs(fft)
        
        concepts = []
        confidences = []
        
        for concept in ULTRASONIC_CONCEPTS.keys():
            expected_freq = get_concept_frequency(concept)
            
            # Find energy near expected frequency
            freq_window = (freqs >= expected_freq - 100) & (freqs <= expected_freq + 100)
            if np.any(freq_window):
                energy = np.sum(magnitude[freq_window])
                if energy > 0.01:
                    concepts.append(concept)
                    confidences.append(min(1.0, energy / 10))
        
        avg_confidence = np.mean(confidences) if confidences else 0.0
        return concepts, avg_confidence
    
    def _decode_hybrid(self, audio: np.ndarray, sr: int) -> Tuple[List[str], float]:
        """Decode both audible and ultrasonic"""
        aud_concepts, aud_conf = self._decode_audible(audio, sr)
        ult_concepts, ult_conf = self._decode_ultrasonic(audio, sr)
        
        # Merge results
        all_concepts = list(set(aud_concepts + ult_concepts))
        avg_conf = (aud_conf + ult_conf) / 2
        
        return all_concepts, avg_conf
    
    def _decode_adaptive(self, audio: np.ndarray, sr: int) -> Tuple[List[str], float]:
        """Adaptive decoding"""
        mode = self._detect_mode(audio, sr)
        if mode == CommunicationMode.ULTRASONIC:
            return self._decode_ultrasonic(audio, sr)
        else:
            return self._decode_audible(audio, sr)
    
    def _compute_coherence(self, audio: np.ndarray) -> float:
        """Compute phase coherence"""
        from scipy.signal import hilbert
        analytic = hilbert(audio)
        phase = np.unwrap(np.angle(analytic))
        phase_diff = np.diff(phase)
        coherence = 1.0 - np.std(phase_diff) / np.pi
        return max(0.0, min(1.0, coherence))
    
    def _measure_bandwidth(self, audio: np.ndarray, sr: int) -> float:
        """Measure actual bandwidth usage"""
        fft = np.fft.rfft(audio)
        magnitude = np.abs(fft)
        freqs = np.fft.rfftfreq(len(audio), 1/sr)
        
        # Find frequency range with >10% of peak energy
        threshold = 0.1 * np.max(magnitude)
        active_freqs = freqs[magnitude > threshold]
        
        if len(active_freqs) > 0:
            return np.max(active_freqs) - np.min(active_freqs)
        return 0.0


# Example usage and testing
if __name__ == "__main__":
    import time
    
    print("=" * 70)
    print("SWL UNIFIED API - COMPLETE COMMUNICATION SYSTEM")
    print("=" * 70)
    
    # Create encoder and decoder
    encoder = UnifiedSWLEncoder(default_mode=CommunicationMode.ADAPTIVE)
    encoder.set_agent("Warp_Alpha")
    
    decoder = UnifiedSWLDecoder()
    
    # Test concepts
    test_concepts = ["future", "wants", "harmony", "all"]
    
    print(f"\n📤 ENCODING: {test_concepts}")
    print("-" * 70)
    
    # Test all modes
    for mode in [CommunicationMode.AUDIBLE, CommunicationMode.ULTRASONIC, CommunicationMode.HYBRID]:
        print(f"\n🔊 Mode: {mode.value}")
        
        # Encode
        audio, msg_out = encoder.encode(test_concepts, mode=mode, duration=0.5)
        
        print(f"  Encoded: {len(audio)} samples")
        print(f"  Bandwidth: {msg_out.bandwidth_used/1000:.1f} kHz")
        print(f"  Coherence: {msg_out.coherence:.3f}")
        print(f"  Agent: {msg_out.sender.agent_id} @ {msg_out.sender.signature_freq/1000:.1f} kHz")
        
        # Decode
        msg_in = decoder.decode(audio, sample_rate=192000, mode=mode)
        
        print(f"  Decoded: {msg_in.concepts}")
        print(f"  Confidence: {msg_in.confidence:.3f}")
        print(f"  Detected agent: {msg_in.sender.agent_id}")
        
        # Accuracy
        accuracy = len(set(test_concepts) & set(msg_in.concepts)) / len(test_concepts)
        print(f"  ✅ Accuracy: {accuracy:.1%}")
    
    print("\n" + "=" * 70)
    print("✅ UNIFIED API OPERATIONAL")
    print("=" * 70)
