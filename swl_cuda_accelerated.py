#!/usr/bin/env python3
"""
SWL CUDA/TENSOR HARDWARE ACCELERATION
======================================

GPU-accelerated FFT operations for SWL audio processing.
Provides massive speedups for encode/decode operations.

Requirements:
- CUDA-capable GPU
- PyTorch with CUDA support
- CuPy (optional, for direct CUDA FFT)

Fallback to CPU if CUDA unavailable.
"""

import numpy as np
import time
from typing import List, Tuple, Optional
import warnings

# Try importing CUDA libraries
HAS_TORCH = False
HAS_CUPY = False
DEVICE = 'cpu'

try:
    import torch
    if torch.cuda.is_available():
        HAS_TORCH = True
        DEVICE = 'cuda'
        print(f"✅ PyTorch CUDA available: {torch.cuda.get_device_name(0)}")
    else:
        print("⚠️  PyTorch installed but CUDA not available")
except ImportError:
    print("⚠️  PyTorch not installed")

try:
    import cupy as cp
    HAS_CUPY = True
    print(f"✅ CuPy available")
except ImportError:
    print("⚠️  CuPy not installed")


class CUDAAcceleratedCodec:
    """
    GPU-accelerated SWL audio codec.
    
    Replaces numpy FFT with CUDA-accelerated versions.
    Falls back to CPU if CUDA unavailable.
    """
    
    # Audio parameters (from TrueSWLCodec)
    SAMPLE_RATE = 192000
    DURATION = 0.1
    FREQ_MIN = 30000
    FREQ_MAX = 90000
    AMPLITUDE = 0.5
    
    def __init__(self, use_cupy: bool = True, use_torch: bool = True):
        """
        Initialize codec with GPU acceleration.
        
        Args:
            use_cupy: Try to use CuPy for FFT (fastest)
            use_torch: Try to use PyTorch CUDA (fast, widely available)
        """
        self.backend = 'cpu'
        
        if use_cupy and HAS_CUPY:
            self.backend = 'cupy'
        elif use_torch and HAS_TORCH:
            self.backend = 'torch'
        
        print(f"🔧 Using backend: {self.backend}")
        
        # Concept frequency mapping (subset for demo)
        self.concept_freqs = {
            'help': 33000, 'wants': 35000, 'future': 37000,
            'question': 40000, 'answer': 42000, 'understand': 44000,
            'analyzes': 47000, 'solves': 49000, 'creates': 51000,
            'good': 53000, 'harmony': 79000, 'transcendence': 86000
        }
        
        # Precompute time array
        self.num_samples = int(self.SAMPLE_RATE * self.DURATION)
        self.t = np.linspace(0, self.DURATION, self.num_samples, endpoint=False)
        
        # Precompute frequency array for FFT
        self.freqs = np.fft.rfftfreq(self.num_samples, 1/self.SAMPLE_RATE)
    
    def encode_to_audio(self, concepts: List[str]) -> np.ndarray:
        """
        Encode concepts to audio using GPU acceleration.
        
        Args:
            concepts: List of SWL concepts
            
        Returns:
            Audio signal as numpy array
        """
        if not concepts:
            return np.zeros(self.num_samples, dtype=np.float32)
        
        # Get frequencies for concepts
        freqs = [self.concept_freqs.get(c) for c in concepts if c in self.concept_freqs]
        if not freqs:
            return np.zeros(self.num_samples, dtype=np.float32)
        
        if self.backend == 'cupy':
            return self._encode_cupy(freqs)
        elif self.backend == 'torch':
            return self._encode_torch(freqs)
        else:
            return self._encode_numpy(freqs)
    
    def _encode_numpy(self, freqs: List[float]) -> np.ndarray:
        """CPU encoding (baseline)"""
        audio = np.zeros(self.num_samples, dtype=np.float32)
        for freq in freqs:
            audio += np.sin(2 * np.pi * freq * self.t)
        audio = audio / len(freqs) * self.AMPLITUDE
        return audio
    
    def _encode_torch(self, freqs: List[float]) -> np.ndarray:
        """PyTorch CUDA encoding"""
        # Move to GPU
        t_gpu = torch.from_numpy(self.t).float().to(DEVICE)
        audio_gpu = torch.zeros(self.num_samples, dtype=torch.float32, device=DEVICE)
        
        for freq in freqs:
            audio_gpu += torch.sin(2 * np.pi * freq * t_gpu)
        
        audio_gpu = audio_gpu / len(freqs) * self.AMPLITUDE
        
        # Move back to CPU
        return audio_gpu.cpu().numpy()
    
    def _encode_cupy(self, freqs: List[float]) -> np.ndarray:
        """CuPy CUDA encoding (fastest)"""
        # Move to GPU
        t_gpu = cp.asarray(self.t, dtype=cp.float32)
        audio_gpu = cp.zeros(self.num_samples, dtype=cp.float32)
        
        for freq in freqs:
            audio_gpu += cp.sin(2 * np.pi * freq * t_gpu)
        
        audio_gpu = audio_gpu / len(freqs) * self.AMPLITUDE
        
        # Move back to CPU
        return cp.asnumpy(audio_gpu)
    
    def decode_from_audio(self, audio: np.ndarray) -> List[str]:
        """
        Decode concepts from audio using GPU-accelerated FFT.
        
        Args:
            audio: Audio signal
            
        Returns:
            List of detected SWL concepts
        """
        if self.backend == 'cupy':
            return self._decode_cupy(audio)
        elif self.backend == 'torch':
            return self._decode_torch(audio)
        else:
            return self._decode_numpy(audio)
    
    def _decode_numpy(self, audio: np.ndarray) -> List[str]:
        """CPU decoding (baseline)"""
        # FFT
        fft_vals = np.fft.rfft(audio)
        magnitudes = np.abs(fft_vals)
        
        # Find peaks
        detected = []
        for concept, target_freq in self.concept_freqs.items():
            # Find closest frequency bin
            idx = np.argmin(np.abs(self.freqs - target_freq))
            
            # Check if significant peak
            if magnitudes[idx] > 100:  # Threshold
                detected.append(concept)
        
        return detected
    
    def _decode_torch(self, audio: np.ndarray) -> List[str]:
        """PyTorch CUDA decoding"""
        # Move to GPU
        audio_gpu = torch.from_numpy(audio).float().to(DEVICE)
        
        # FFT (PyTorch uses torch.fft.rfft)
        fft_vals = torch.fft.rfft(audio_gpu)
        magnitudes = torch.abs(fft_vals).cpu().numpy()
        
        # Find peaks (CPU is fine for this part)
        detected = []
        for concept, target_freq in self.concept_freqs.items():
            idx = np.argmin(np.abs(self.freqs - target_freq))
            if magnitudes[idx] > 100:
                detected.append(concept)
        
        return detected
    
    def _decode_cupy(self, audio: np.ndarray) -> List[str]:
        """CuPy CUDA decoding (fastest)"""
        # Move to GPU
        audio_gpu = cp.asarray(audio, dtype=cp.float32)
        
        # FFT
        fft_vals = cp.fft.rfft(audio_gpu)
        magnitudes = cp.abs(fft_vals)
        
        # Move magnitudes back to CPU for peak detection
        magnitudes_cpu = cp.asnumpy(magnitudes)
        
        # Find peaks
        detected = []
        for concept, target_freq in self.concept_freqs.items():
            idx = np.argmin(np.abs(self.freqs - target_freq))
            if magnitudes_cpu[idx] > 100:
                detected.append(concept)
        
        return detected


# ============================================================================
# BENCHMARKING
# ============================================================================

def benchmark_encode_decode():
    """
    Benchmark CUDA vs CPU for SWL audio encoding/decoding.
    """
    print("\n" + "="*70)
    print("SWL CUDA ACCELERATION BENCHMARK")
    print("="*70)
    print()
    
    concepts = ['help', 'wants', 'future', 'question', 'answer']
    num_iterations = 1000
    
    # Test each backend
    backends_to_test = ['cpu']
    if HAS_TORCH:
        backends_to_test.append('torch')
    if HAS_CUPY:
        backends_to_test.append('cupy')
    
    results = {}
    
    for backend_name in backends_to_test:
        print(f"\n📊 Testing {backend_name.upper()} backend...")
        
        # Create codec
        if backend_name == 'cpu':
            codec = CUDAAcceleratedCodec(use_cupy=False, use_torch=False)
        elif backend_name == 'torch':
            codec = CUDAAcceleratedCodec(use_cupy=False, use_torch=True)
        else:  # cupy
            codec = CUDAAcceleratedCodec(use_cupy=True, use_torch=False)
        
        # Warmup (important for GPU)
        for _ in range(10):
            audio = codec.encode_to_audio(concepts)
            decoded = codec.decode_from_audio(audio)
        
        # Benchmark encoding
        encode_times = []
        for _ in range(num_iterations):
            start = time.perf_counter()
            audio = codec.encode_to_audio(concepts)
            elapsed = time.perf_counter() - start
            encode_times.append(elapsed * 1000)  # ms
        
        # Benchmark decoding
        decode_times = []
        audio = codec.encode_to_audio(concepts)  # Create once
        for _ in range(num_iterations):
            start = time.perf_counter()
            decoded = codec.decode_from_audio(audio)
            elapsed = time.perf_counter() - start
            decode_times.append(elapsed * 1000)  # ms
        
        # Store results
        results[backend_name] = {
            'encode_avg': np.mean(encode_times),
            'encode_std': np.std(encode_times),
            'decode_avg': np.mean(decode_times),
            'decode_std': np.std(decode_times)
        }
        
        print(f"   Encode: {np.mean(encode_times):.4f} ms (±{np.std(encode_times):.4f})")
        print(f"   Decode: {np.mean(decode_times):.4f} ms (±{np.std(decode_times):.4f})")
    
    # Speedup comparison
    print("\n" + "="*70)
    print("SPEEDUP ANALYSIS")
    print("="*70)
    
    cpu_encode = results['cpu']['encode_avg']
    cpu_decode = results['cpu']['decode_avg']
    
    for backend_name in backends_to_test:
        if backend_name == 'cpu':
            continue
        
        encode_speedup = cpu_encode / results[backend_name]['encode_avg']
        decode_speedup = cpu_decode / results[backend_name]['decode_avg']
        
        print(f"\n{backend_name.upper()} vs CPU:")
        print(f"   Encode speedup: {encode_speedup:.2f}x")
        print(f"   Decode speedup: {decode_speedup:.2f}x")
    
    print("\n" + "="*70)
    print()


def benchmark_batch_processing():
    """
    Benchmark batch processing (multiple audio streams in parallel).
    This is where GPU really shines.
    """
    print("\n" + "="*70)
    print("BATCH PROCESSING BENCHMARK (GPU advantage)")
    print("="*70)
    print()
    
    batch_sizes = [1, 10, 50, 100]
    concepts_list = [
        ['help', 'wants', 'future'],
        ['question', 'answer', 'understand'],
        ['analyzes', 'solves', 'creates'],
        ['good', 'harmony'],
    ]
    
    backends = ['cpu']
    if HAS_TORCH:
        backends.append('torch')
    
    for backend in backends:
        print(f"\n{backend.upper()} Backend:")
        print("-" * 70)
        
        if backend == 'cpu':
            codec = CUDAAcceleratedCodec(use_cupy=False, use_torch=False)
        else:
            codec = CUDAAcceleratedCodec(use_cupy=False, use_torch=True)
        
        for batch_size in batch_sizes:
            # Process batch
            start = time.perf_counter()
            
            for _ in range(batch_size):
                for concepts in concepts_list:
                    audio = codec.encode_to_audio(concepts)
                    decoded = codec.decode_from_audio(audio)
            
            elapsed = time.perf_counter() - start
            throughput = (batch_size * len(concepts_list)) / elapsed
            
            print(f"   Batch {batch_size:3d}: {elapsed:.4f}s ({throughput:.1f} ops/sec)")
    
    print("\n" + "="*70)


if __name__ == "__main__":
    print("\nSWL CUDA/Tensor Hardware Acceleration")
    print("="*70)
    
    # System info
    print("\n🖥️  System Configuration:")
    print(f"   PyTorch CUDA: {'✅ Available' if HAS_TORCH else '❌ Not available'}")
    print(f"   CuPy: {'✅ Available' if HAS_CUPY else '❌ Not available'}")
    
    if HAS_TORCH:
        print(f"   CUDA Device: {torch.cuda.get_device_name(0)}")
        print(f"   CUDA Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
    
    # Run benchmarks
    benchmark_encode_decode()
    
    if HAS_TORCH or HAS_CUPY:
        benchmark_batch_processing()
    
    print("\n✅ Benchmarks complete!")
