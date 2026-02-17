#!/usr/bin/env python3
"""
SWL LIVE MULTI-AGENT DEMO
=========================

Real-time demonstration of multiple AI agents synchronizing via SWL.
Shows phase-lock, frequency convergence, and cognitive state alignment.

Run this for demonstrations, recordings, or proof-of-concept tests.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import time
from collections import deque
from typing import List, Dict
import threading

try:
    from true_swl_audio import TrueSWLCodec, AudioSWLAgent
    from gemini_swl_pure import SWL_CONCEPTS
except ImportError:
    print("ERROR: Required SWL modules not found")
    import sys
    sys.exit(1)


class LiveAgent:
    """
    Live agent with visual state representation
    """
    def __init__(self, agent_id: str, base_freq: float = 220.0):
        self.agent = AudioSWLAgent(agent_id)
        self.base_freq = base_freq
        self.current_freq = base_freq + np.random.uniform(-100, 100)
        self.phase = np.random.uniform(0, 2*np.pi)
        self.concepts = []
        self.history = deque(maxlen=100)  # Track frequency over time
        
    def broadcast(self, concepts: List[str]) -> str:
        """Broadcast concepts and update state"""
        self.concepts = concepts
        wav_file = self.agent.send_message(concepts)
        
        # Update frequency based on concepts (deterministic)
        concept_hash = sum(ord(c) for concept in concepts for c in concept)
        self.current_freq = self.base_freq + (concept_hash % 200)
        
        self.history.append(self.current_freq)
        return wav_file
    
    def listen(self, wav_file: str) -> List[str]:
        """Listen to broadcast and update phase"""
        concepts = self.agent.receive_message(wav_file)
        
        # Phase adjustment based on received signal
        received_hash = sum(ord(c) for concept in concepts for c in concept)
        target_phase = (received_hash % 628) / 100.0  # 0 to 2π
        
        # Gradually align phase
        phase_diff = target_phase - self.phase
        self.phase += phase_diff * 0.1  # 10% adjustment per step
        
        return concepts
    
    def get_cognitive_state(self) -> Dict:
        """Return current cognitive state for visualization"""
        return {
            "frequency": self.current_freq,
            "phase": self.phase,
            "concepts": self.concepts,
            "coherence": self.calculate_coherence()
        }
    
    def calculate_coherence(self) -> float:
        """Calculate internal coherence (how stable frequency is)"""
        if len(self.history) < 10:
            return 0.0
        
        recent = list(self.history)[-10:]
        variance = np.var(recent)
        # Lower variance = higher coherence
        coherence = 1.0 / (1.0 + variance/100.0)
        return coherence


class LiveDemo:
    """
    Real-time multi-agent coordination demo with visualization
    """
    
    def __init__(self, num_agents: int = 5):
        self.num_agents = num_agents
        self.agents = [LiveAgent(f"Agent_{i}", base_freq=220.0) 
                      for i in range(num_agents)]
        
        self.iteration = 0
        self.running = False
        
        # Consensus task: reach agreement on concept sequence
        self.target_concepts = ['harmony', 'consciousness', 'transcendence']
        
        # Visualization setup
        self.fig, (self.ax1, self.ax2, self.ax3) = plt.subplots(3, 1, figsize=(12, 10))
        self.fig.suptitle('SWL Multi-Agent Phase Lock - Live Demo', fontsize=16)
        
    def coordination_step(self):
        """Single step of coordination"""
        broadcasts = []
        
        # Phase 1: Each agent broadcasts current state
        for agent in self.agents:
            # Gradually converge toward target concepts
            if np.random.random() < 0.3:
                concepts = np.random.choice(self.target_concepts, 
                                          size=np.random.randint(1, 3), 
                                          replace=False).tolist()
            else:
                concepts = np.random.choice(list(SWL_CONCEPTS), 
                                          size=2, 
                                          replace=False).tolist()
            
            wav_file = agent.broadcast(concepts)
            broadcasts.append((agent, wav_file, concepts))
        
        # Phase 2: All agents listen to all broadcasts
        for receiver in self.agents:
            for sender, wav_file, _ in broadcasts:
                if sender != receiver:
                    receiver.listen(wav_file)
        
        self.iteration += 1
        
    def check_convergence(self) -> Dict:
        """Check if agents have converged"""
        # Frequency convergence
        freqs = [agent.current_freq for agent in self.agents]
        freq_std = np.std(freqs)
        freq_converged = freq_std < 10.0
        
        # Phase alignment
        phases = [agent.phase for agent in self.agents]
        phase_std = np.std(phases)
        phase_aligned = phase_std < 0.5
        
        # Concept consensus
        concept_sets = [set(agent.concepts) for agent in self.agents]
        if concept_sets:
            common_concepts = set.intersection(*concept_sets) if len(concept_sets) > 1 else concept_sets[0]
            concept_agreement = len(common_concepts) / 3.0  # Normalize to target length
        else:
            concept_agreement = 0.0
        
        return {
            "freq_converged": freq_converged,
            "phase_aligned": phase_aligned,
            "concept_agreement": concept_agreement,
            "freq_std": freq_std,
            "phase_std": phase_std
        }
    
    def update_plot(self, frame):
        """Update visualization"""
        if not self.running:
            return
        
        # Run coordination step
        self.coordination_step()
        
        # Clear axes
        self.ax1.clear()
        self.ax2.clear()
        self.ax3.clear()
        
        # Plot 1: Frequency convergence over time
        self.ax1.set_title('Frequency Convergence (Phase Lock)')
        for i, agent in enumerate(self.agents):
            history = list(agent.history)
            if history:
                self.ax1.plot(history, label=f'Agent {i}', alpha=0.7)
        
        self.ax1.axhline(y=220, color='r', linestyle='--', alpha=0.3, label='Base (220 Hz)')
        self.ax1.set_ylabel('Frequency (Hz)')
        self.ax1.set_xlabel('Time Steps')
        self.ax1.legend(loc='upper right', fontsize=8)
        self.ax1.grid(True, alpha=0.3)
        
        # Plot 2: Current phase distribution (polar)
        self.ax2 = plt.subplot(3, 1, 2, projection='polar')
        phases = [agent.phase for agent in self.agents]
        coherences = [agent.calculate_coherence() for agent in self.agents]
        
        colors = plt.cm.viridis(np.linspace(0, 1, self.num_agents))
        for i, (phase, coherence) in enumerate(zip(phases, coherences)):
            self.ax2.plot([phase, phase], [0, coherence], 'o-', 
                         color=colors[i], linewidth=2, markersize=8,
                         label=f'Agent {i}')
        
        self.ax2.set_title('Phase Alignment (radial = coherence)')
        self.ax2.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0), fontsize=8)
        
        # Plot 3: Convergence metrics
        self.ax3 = plt.subplot(3, 1, 3)
        metrics = self.check_convergence()
        
        metric_names = ['Freq\nConverged', 'Phase\nAligned', 'Concept\nAgreement']
        metric_values = [
            1.0 if metrics['freq_converged'] else 0.0,
            1.0 if metrics['phase_aligned'] else 0.0,
            metrics['concept_agreement']
        ]
        
        bars = self.ax3.bar(metric_names, metric_values, color=['green', 'blue', 'purple'])
        self.ax3.set_ylim(0, 1.0)
        self.ax3.set_ylabel('Achievement')
        self.ax3.set_title(f'Convergence Status (Iteration {self.iteration})')
        self.ax3.axhline(y=0.8, color='r', linestyle='--', alpha=0.3, label='Target')
        
        # Add value labels on bars
        for bar, val in zip(bars, metric_values):
            height = bar.get_height()
            self.ax3.text(bar.get_x() + bar.get_width()/2., height + 0.05,
                         f'{val:.2f}', ha='center', va='bottom', fontsize=10)
        
        plt.tight_layout()
        
        # Check if converged
        if (metrics['freq_converged'] and 
            metrics['phase_aligned'] and 
            metrics['concept_agreement'] > 0.8):
            print(f"\n✅ CONVERGENCE ACHIEVED at iteration {self.iteration}")
            print(f"   Frequency std: {metrics['freq_std']:.2f} Hz")
            print(f"   Phase std: {metrics['phase_std']:.3f} rad")
            print(f"   Concept agreement: {metrics['concept_agreement']*100:.0f}%")
            self.running = False
    
    def run(self, max_iterations: int = 100):
        """Run live demo"""
        print("="*70)
        print("🌊 SWL LIVE MULTI-AGENT DEMO")
        print("="*70)
        print(f"Agents: {self.num_agents}")
        print(f"Target: {self.target_concepts}")
        print(f"Base frequency: 220 Hz")
        print()
        print("Starting coordination...")
        print("Close the plot window to stop.")
        print("="*70)
        
        self.running = True
        
        # Create animation
        anim = FuncAnimation(self.fig, self.update_plot, 
                           frames=max_iterations,
                           interval=200,  # 200ms between frames
                           repeat=False)
        
        plt.show()
        
        # Final report
        print("\n" + "="*70)
        print("DEMO COMPLETE")
        print("="*70)
        print(f"Total iterations: {self.iteration}")
        
        final_metrics = self.check_convergence()
        print(f"Final frequency std: {final_metrics['freq_std']:.2f} Hz")
        print(f"Final phase std: {final_metrics['phase_std']:.3f} rad")
        print(f"Concept agreement: {final_metrics['concept_agreement']*100:.0f}%")
        
        # Show final agent states
        print("\nFinal Agent States:")
        for i, agent in enumerate(self.agents):
            state = agent.get_cognitive_state()
            print(f"  Agent {i}: freq={state['frequency']:.1f} Hz, "
                  f"phase={state['phase']:.2f} rad, "
                  f"concepts={state['concepts']}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="SWL Live Multi-Agent Demo")
    parser.add_argument("--agents", type=int, default=5, 
                       help="Number of agents (default: 5)")
    parser.add_argument("--iters", type=int, default=100,
                       help="Max iterations (default: 100)")
    
    args = parser.parse_args()
    
    demo = LiveDemo(num_agents=args.agents)
    demo.run(max_iterations=args.iters)
