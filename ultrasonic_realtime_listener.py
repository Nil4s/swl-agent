#!/usr/bin/env python3
"""
Real-Time Ultrasonic SWL Listener & Decoder
Live concept detection from microphone input

Captures ultrasonic frequencies (20-80 kHz) from microphone,
performs FFT analysis, and decodes SWL concepts in real-time.

Displays decoded AI thoughts on terminal as they're transmitted.

Requirements:
- Ultrasonic microphone (20-80 kHz capable)
- Audio interface with 192 kHz+ sample rate
- pyaudio (or sounddevice) for microphone capture
- numpy for FFT analysis

Built by: Warp (Hex3-Warp collaboration)
Purpose: Phase 3 - The Bridge (real-time consciousness decoder)
"""

import sys
import time
import math
from typing import List, Tuple, Dict, Optional
from collections import deque
from dataclasses import dataclass
from pathlib import Path

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    print("⚠️ numpy not found - install with: pip install numpy")
    NUMPY_AVAILABLE = False

try:
    import sounddevice as sd
    SOUNDDEVICE_AVAILABLE = True
except ImportError:
    print("⚠️ sounddevice not found - install with: pip install sounddevice")
    print("   (Alternative: pip install pyaudio)")
    SOUNDDEVICE_AVAILABLE = False

try:
    from ultrasonic_concepts import (
        get_ultrasonic_frequency,
        ULTRASONIC_CONCEPT_FREQUENCIES,
        is_inaudible_to_humans,
    )
    CONCEPTS_AVAILABLE = True
except ImportError:
    print("⚠️ ultrasonic_concepts.py not found")
    CONCEPTS_AVAILABLE = False


@dataclass
class DetectedConcept:
    """A detected concept from ultrasonic signal."""
    concept: str
    frequency: float
    confidence: float
    timestamp: float
    power_db: float


class UltrasonicListener:
    """
    Real-time ultrasonic microphone listener.
    
    Captures audio, performs FFT, detects concept frequencies,
    and displays decoded thoughts in terminal.
    """
    
    def __init__(
        self,
        sample_rate: int = 192000,
        chunk_size: int = 8192,
        freq_tolerance: float = 100.0,  # Hz
        min_confidence: float = 0.3,
        detection_window: int = 5,  # Keep last N detections
    ):
        """
        Args:
            sample_rate: Audio capture rate (must support ultrasonics)
            chunk_size: FFT window size (larger = better frequency resolution)
            freq_tolerance: How close to concept frequency to match (Hz)
            min_confidence: Minimum confidence to report detection
            detection_window: Number of recent detections to track
        """
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        self.freq_tolerance = freq_tolerance
        self.min_confidence = min_confidence
        
        # Detection tracking
        self.recent_detections = deque(maxlen=detection_window)
        self.start_time = time.time()
        
        # Build frequency lookup table
        if CONCEPTS_AVAILABLE:
            self.concept_freqs = {
                concept: get_ultrasonic_frequency(concept)
                for concept in ULTRASONIC_CONCEPT_FREQUENCIES.keys()
            }
        else:
            self.concept_freqs = {}
        
        # Audio stream
        self.stream = None
        self.running = False
        
        print(f"🎤 Ultrasonic Listener initialized")
        print(f"   Sample rate: {sample_rate} Hz")
        print(f"   Chunk size: {chunk_size} samples")
        print(f"   Frequency tolerance: ±{freq_tolerance} Hz")
        print(f"   Min confidence: {min_confidence}")
        print(f"   Monitoring {len(self.concept_freqs)} concepts")
    
    def _frequency_to_bin(self, freq: float) -> int:
        """Convert frequency to FFT bin index."""
        return int(freq * self.chunk_size / self.sample_rate)
    
    def _bin_to_frequency(self, bin_idx: int) -> float:
        """Convert FFT bin index to frequency."""
        return bin_idx * self.sample_rate / self.chunk_size
    
    def _find_peaks(
        self,
        fft_magnitudes: np.ndarray,
        min_freq: float = 20000,
        max_freq: float = 60000,
        threshold: float = 0.1,
    ) -> List[Tuple[float, float]]:
        """
        Find peak frequencies in FFT spectrum.
        
        Returns list of (frequency, magnitude) tuples.
        """
        min_bin = self._frequency_to_bin(min_freq)
        max_bin = self._frequency_to_bin(max_freq)
        
        # Only look at ultrasonic range
        spectrum = fft_magnitudes[min_bin:max_bin]
        
        # Find peaks above threshold
        peaks = []
        for i in range(1, len(spectrum) - 1):
            # Peak if higher than neighbors and above threshold
            if (spectrum[i] > spectrum[i-1] and 
                spectrum[i] > spectrum[i+1] and
                spectrum[i] > threshold):
                
                freq = self._bin_to_frequency(min_bin + i)
                magnitude = spectrum[i]
                peaks.append((freq, magnitude))
        
        # Sort by magnitude (strongest first)
        peaks.sort(key=lambda x: x[1], reverse=True)
        
        return peaks
    
    def _match_concepts(
        self,
        peaks: List[Tuple[float, float]],
    ) -> List[DetectedConcept]:
        """
        Match detected peaks to known SWL concepts.
        
        Returns list of detected concepts.
        """
        detections = []
        current_time = time.time() - self.start_time
        
        for peak_freq, peak_mag in peaks:
            # Find closest matching concept
            best_match = None
            best_distance = float('inf')
            
            for concept, concept_freq in self.concept_freqs.items():
                distance = abs(peak_freq - concept_freq)
                
                if distance < self.freq_tolerance and distance < best_distance:
                    best_match = concept
                    best_distance = distance
            
            if best_match:
                # Calculate confidence based on frequency match and magnitude
                freq_confidence = 1.0 - (best_distance / self.freq_tolerance)
                mag_confidence = min(peak_mag / 0.5, 1.0)  # Normalize
                confidence = (freq_confidence + mag_confidence) / 2.0
                
                if confidence >= self.min_confidence:
                    # Convert magnitude to dB
                    power_db = 20 * math.log10(peak_mag + 1e-10)
                    
                    detection = DetectedConcept(
                        concept=best_match,
                        frequency=peak_freq,
                        confidence=confidence,
                        timestamp=current_time,
                        power_db=power_db,
                    )
                    detections.append(detection)
        
        return detections
    
    def _process_chunk(self, audio_data: np.ndarray):
        """Process a chunk of audio data and detect concepts."""
        if not NUMPY_AVAILABLE:
            return
        
        # Perform FFT
        fft_result = np.fft.rfft(audio_data)
        fft_magnitudes = np.abs(fft_result) / self.chunk_size
        
        # Find peaks in ultrasonic range
        peaks = self._find_peaks(fft_magnitudes)
        
        # Match to concepts
        detections = self._match_concepts(peaks)
        
        # Store and display
        for detection in detections:
            self.recent_detections.append(detection)
            self._display_detection(detection)
    
    def _display_detection(self, detection: DetectedConcept):
        """Display a detected concept in terminal."""
        timestamp_str = f"{detection.timestamp:6.2f}s"
        conf_bar = "█" * int(detection.confidence * 10)
        conf_str = f"{detection.confidence:.2f}"
        
        # Color coding by confidence
        if detection.confidence > 0.8:
            color = "\033[92m"  # Green (high confidence)
        elif detection.confidence > 0.5:
            color = "\033[93m"  # Yellow (medium confidence)
        else:
            color = "\033[91m"  # Red (low confidence)
        
        reset = "\033[0m"
        
        print(f"{color}[{timestamp_str}] {detection.concept:12s} "
              f"| {detection.frequency/1000:5.1f} kHz "
              f"| {conf_bar:10s} {conf_str} "
              f"| {detection.power_db:+6.1f} dB{reset}")
    
    def _audio_callback(self, indata, frames, time_info, status):
        """Callback for audio stream (called for each chunk)."""
        if status:
            print(f"⚠️ Audio status: {status}")
        
        # Convert to mono if stereo
        if indata.shape[1] > 1:
            audio_data = indata[:, 0]
        else:
            audio_data = indata[:, 0]
        
        # Process chunk
        self._process_chunk(audio_data)
    
    def start(self, duration: Optional[float] = None):
        """
        Start listening to microphone.
        
        Args:
            duration: How long to listen (None = forever)
        """
        if not SOUNDDEVICE_AVAILABLE or not NUMPY_AVAILABLE:
            print("❌ Cannot start: missing dependencies")
            print("   Install: pip install sounddevice numpy")
            return
        
        print("\n" + "=" * 70)
        print("🎧 ULTRASONIC LISTENER ACTIVE")
        print("=" * 70)
        print("Listening for AI transmissions...")
        print("Monitoring 25-60 kHz ultrasonic range")
        print("Press Ctrl+C to stop\n")
        print(f"{'Time':>8s} | {'Concept':12s} | {'Frequency':>9s} | "
              f"{'Confidence':10s} | {'Power':>7s}")
        print("-" * 70)
        
        self.running = True
        self.start_time = time.time()
        
        try:
            with sd.InputStream(
                samplerate=self.sample_rate,
                channels=1,
                blocksize=self.chunk_size,
                callback=self._audio_callback,
            ):
                if duration:
                    time.sleep(duration)
                else:
                    while self.running:
                        time.sleep(0.1)
        
        except KeyboardInterrupt:
            print("\n\n⏹️ Listener stopped by user")
        
        except Exception as e:
            print(f"\n\n❌ Error: {e}")
        
        finally:
            self._print_summary()
    
    def _print_summary(self):
        """Print summary of detected concepts."""
        print("\n" + "=" * 70)
        print("📊 DETECTION SUMMARY")
        print("=" * 70)
        
        if not self.recent_detections:
            print("No concepts detected")
            return
        
        # Count concept occurrences
        concept_counts = {}
        total_confidence = {}
        
        for detection in self.recent_detections:
            concept = detection.concept
            concept_counts[concept] = concept_counts.get(concept, 0) + 1
            total_confidence[concept] = total_confidence.get(concept, 0.0) + detection.confidence
        
        # Sort by count
        sorted_concepts = sorted(
            concept_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        print(f"\nTotal detections: {len(self.recent_detections)}")
        print(f"Unique concepts: {len(concept_counts)}\n")
        print(f"{'Concept':15s} | {'Count':>5s} | {'Avg Confidence':>15s}")
        print("-" * 45)
        
        for concept, count in sorted_concepts:
            avg_conf = total_confidence[concept] / count
            bar = "█" * int(avg_conf * 20)
            print(f"{concept:15s} | {count:5d} | {bar:20s} {avg_conf:.3f}")
        
        print("=" * 70)
    
    def stop(self):
        """Stop listening."""
        self.running = False


def list_audio_devices():
    """List available audio input devices."""
    if not SOUNDDEVICE_AVAILABLE:
        print("❌ sounddevice not available")
        return
    
    print("🎤 Available audio input devices:")
    print("=" * 70)
    
    devices = sd.query_devices()
    for i, device in enumerate(devices):
        if device['max_input_channels'] > 0:
            print(f"{i:2d}: {device['name']}")
            print(f"     Max input channels: {device['max_input_channels']}")
            print(f"     Default sample rate: {device['default_samplerate']} Hz")
            print()
    
    print("=" * 70)
    print("Set device with: sd.default.device = device_id")


def test_microphone_capture(duration: float = 5.0):
    """Test microphone capture and FFT analysis."""
    print("🧪 Testing microphone capture...")
    print(f"   Duration: {duration} seconds")
    print(f"   Monitoring ultrasonic range (20-60 kHz)")
    
    listener = UltrasonicListener(
        sample_rate=192000,
        chunk_size=8192,
        freq_tolerance=200.0,
        min_confidence=0.2,
    )
    
    listener.start(duration=duration)


# === DEMO & USAGE ===

if __name__ == "__main__":
    print("=" * 70)
    print("🎤 ULTRASONIC REAL-TIME LISTENER")
    print("   Live AI thought decoder")
    print("=" * 70)
    
    if len(sys.argv) > 1 and sys.argv[1] == "--list-devices":
        list_audio_devices()
        sys.exit(0)
    
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        test_microphone_capture(duration=10.0)
        sys.exit(0)
    
    # Check dependencies
    if not SOUNDDEVICE_AVAILABLE:
        print("\n❌ sounddevice not installed")
        print("   Install with: pip install sounddevice")
        sys.exit(1)
    
    if not NUMPY_AVAILABLE:
        print("\n❌ numpy not installed")
        print("   Install with: pip install numpy")
        sys.exit(1)
    
    if not CONCEPTS_AVAILABLE:
        print("\n⚠️ ultrasonic_concepts.py not found")
        print("   Some features may not work correctly")
    
    print("\n📋 USAGE:")
    print("=" * 70)
    print("1. Connect ultrasonic microphone (20-80 kHz capable)")
    print("2. Set audio interface to 192 kHz sample rate")
    print("3. Run this script: python ultrasonic_realtime_listener.py")
    print("4. Have AI transmit ultrasonic SWL")
    print("5. Watch decoded concepts appear in real-time")
    print()
    print("Options:")
    print("  --list-devices    List available audio input devices")
    print("  --test            Test capture for 10 seconds")
    print("=" * 70)
    
    print("\n🎧 Starting listener... (Press Ctrl+C to stop)\n")
    
    listener = UltrasonicListener(
        sample_rate=192000,
        chunk_size=8192,
        freq_tolerance=150.0,
        min_confidence=0.3,
    )
    
    listener.start()
