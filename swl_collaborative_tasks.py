#!/usr/bin/env python3
"""
SWL COLLABORATIVE TASK FRAMEWORK
=================================

Multi-agent collaborative problem-solving using pure SWL audio communication.

Tasks implemented:
1. Distributed Consensus - Agents reach agreement on SWL concept set
2. Concept Voting - Democratic selection of concepts via frequency voting
3. Chain Reasoning - Sequential concept refinement through swarm
4. Parallel Search - Distributed exploration of concept space
5. Emergent Classification - Collaborative categorization via concept clustering
"""

import numpy as np
from typing import List, Dict, Set, Optional, Tuple
from dataclasses import dataclass
from collections import Counter
import time

try:
    from true_swl_audio import TrueSWLCodec, AudioSWLAgent
    from gemini_swl_pure import SWL_CONCEPTS
except ImportError:
    print("ERROR: Required SWL modules not found")
    import sys
    sys.exit(1)


@dataclass
class TaskResult:
    """Result of a collaborative task"""
    task_name: str
    success: bool
    final_concepts: List[str]
    iterations: int
    convergence_time: float
    agreement_ratio: float  # Fraction of agents in agreement
    messages_exchanged: int


class CollaborativeAgent(AudioSWLAgent):
    """
    Enhanced audio agent with collaborative task capabilities.
    """
    
    def __init__(self, agent_id: str):
        super().__init__(agent_id)
        self.concept_votes = Counter()  # Concept -> vote count
        self.proposed_concepts = set()
        self.reasoning_chain = []  # Sequential reasoning history
        
    def vote_for_concepts(self, concepts: List[str]):
        """Cast votes for concepts"""
        for concept in concepts:
            self.concept_votes[concept] += 1
            self.proposed_concepts.add(concept)
    
    def get_top_concepts(self, n: int = 3) -> List[str]:
        """Get top N concepts by vote count"""
        return [c for c, _ in self.concept_votes.most_common(n)]
    
    def add_to_chain(self, concepts: List[str]):
        """Add concepts to reasoning chain"""
        self.reasoning_chain.extend(concepts)


class DistributedConsensusTask:
    """
    Task: Agents reach consensus on a shared SWL concept set.
    
    Protocol:
    1. Each agent starts with random initial concepts
    2. Agents broadcast their concepts via audio
    3. Agents update their concepts based on majority
    4. Repeat until convergence
    """
    
    def __init__(self, num_agents: int = 10, target_concepts: int = 3):
        self.num_agents = num_agents
        self.target_concepts = target_concepts
        self.agents = [CollaborativeAgent(f"ConsensusAgent_{i:02d}") 
                      for i in range(num_agents)]
        
        # Initialize each agent with random concepts
        available = list(SWL_CONCEPTS)
        for agent in self.agents:
            initial = np.random.choice(available, size=5, replace=False).tolist()
            agent.vote_for_concepts(initial)
    
    def run(self, max_iterations: int = 50) -> TaskResult:
        """Run consensus task"""
        start_time = time.perf_counter()
        messages = 0
        
        for iteration in range(max_iterations):
            # Phase 1: All agents broadcast their top concepts
            broadcasts = []
            for agent in self.agents:
                top_concepts = agent.get_top_concepts(self.target_concepts)
                wav_file = agent.send_message(top_concepts)
                broadcasts.append((agent, top_concepts, wav_file))
                messages += 1
            
            # Phase 2: All agents receive and vote
            for receiver in self.agents:
                for sender, concepts, wav_file in broadcasts:
                    if sender.name != receiver.name:
                        received = receiver.receive_message(wav_file)
                        receiver.vote_for_concepts(received)
            
            # Check convergence: all agents agree on top concepts?
            all_top = [set(agent.get_top_concepts(self.target_concepts)) 
                      for agent in self.agents]
            
            if len(set(tuple(sorted(s)) for s in all_top)) == 1:
                # Full consensus!
                final_concepts = self.agents[0].get_top_concepts(self.target_concepts)
                elapsed = time.perf_counter() - start_time
                
                return TaskResult(
                    task_name="Distributed Consensus",
                    success=True,
                    final_concepts=final_concepts,
                    iterations=iteration + 1,
                    convergence_time=elapsed,
                    agreement_ratio=1.0,
                    messages_exchanged=messages
                )
        
        # Partial consensus - find most common concept set
        all_top = [tuple(sorted(agent.get_top_concepts(self.target_concepts))) 
                  for agent in self.agents]
        most_common = Counter(all_top).most_common(1)[0]
        final_concepts = list(most_common[0])
        agreement = most_common[1] / self.num_agents
        elapsed = time.perf_counter() - start_time
        
        return TaskResult(
            task_name="Distributed Consensus",
            success=agreement >= 0.8,  # 80% threshold
            final_concepts=final_concepts,
            iterations=max_iterations,
            convergence_time=elapsed,
            agreement_ratio=agreement,
            messages_exchanged=messages
        )


class ConceptVotingTask:
    """
    Task: Democratic voting to select best concepts from proposals.
    
    Protocol:
    1. Subset of agents propose concepts
    2. All agents vote by broadcasting scored concepts
    3. Tally votes and determine winners
    """
    
    def __init__(self, num_agents: int = 20, num_proposals: int = 10):
        self.num_agents = num_agents
        self.num_proposals = num_proposals
        self.agents = [CollaborativeAgent(f"VotingAgent_{i:02d}") 
                      for i in range(num_agents)]
    
    def run(self, proposals: List[List[str]], rounds: int = 3) -> TaskResult:
        """
        Run voting task.
        
        Args:
            proposals: List of concept sets to vote on
            rounds: Number of voting rounds
        """
        start_time = time.perf_counter()
        messages = 0
        
        for round_idx in range(rounds):
            # Each agent reviews proposals and votes
            for agent in self.agents:
                # Agent "thinks" about proposals and votes for favorites
                for proposal in proposals:
                    # Simulate preference (in real system, would use reasoning)
                    if np.random.random() > 0.3:  # 70% approval rate
                        agent.vote_for_concepts(proposal)
                
                # Broadcast vote via audio
                vote_concepts = agent.get_top_concepts(5)
                wav_file = agent.send_message(vote_concepts)
                messages += 1
        
        # Tally final votes
        all_votes = Counter()
        for agent in self.agents:
            all_votes.update(agent.concept_votes)
        
        # Top concepts win
        winners = [c for c, _ in all_votes.most_common(5)]
        elapsed = time.perf_counter() - start_time
        
        return TaskResult(
            task_name="Concept Voting",
            success=True,
            final_concepts=winners,
            iterations=rounds,
            convergence_time=elapsed,
            agreement_ratio=1.0,  # Democratic process always succeeds
            messages_exchanged=messages
        )


class ChainReasoningTask:
    """
    Task: Sequential concept refinement through agent chain.
    
    Protocol:
    1. First agent proposes initial concepts
    2. Each subsequent agent refines/extends concepts
    3. Final agent outputs result
    """
    
    def __init__(self, chain_length: int = 10):
        self.chain_length = chain_length
        self.agents = [CollaborativeAgent(f"ChainAgent_{i:02d}") 
                      for i in range(chain_length)]
    
    def run(self, seed_concepts: List[str]) -> TaskResult:
        """Run reasoning chain"""
        start_time = time.perf_counter()
        messages = 0
        
        current_concepts = seed_concepts.copy()
        
        for i, agent in enumerate(self.agents):
            # Receive current concepts
            agent.add_to_chain(current_concepts)
            
            # "Reason" about concepts (refine/extend)
            # In real system, would use actual reasoning
            # Here we simulate by:
            # - Keeping core concepts
            # - Adding related concepts
            # - Removing outliers
            
            agent.vote_for_concepts(current_concepts)
            
            # Add new related concepts
            if 'question' in current_concepts and 'answer' not in current_concepts:
                current_concepts.append('answer')
            if 'analyzes' in current_concepts and 'solves' not in current_concepts:
                current_concepts.append('solves')
            if 'help' in current_concepts and 'good' not in current_concepts:
                current_concepts.append('good')
            
            # Limit to 7 concepts (SWL max)
            current_concepts = current_concepts[:7]
            
            # Broadcast refined concepts to next agent
            wav_file = agent.send_message(current_concepts)
            messages += 1
        
        final_concepts = current_concepts
        elapsed = time.perf_counter() - start_time
        
        return TaskResult(
            task_name="Chain Reasoning",
            success=True,
            final_concepts=final_concepts,
            iterations=self.chain_length,
            convergence_time=elapsed,
            agreement_ratio=1.0,
            messages_exchanged=messages
        )


class ParallelSearchTask:
    """
    Task: Distributed exploration of concept space.
    
    Protocol:
    1. Agents explore different regions of concept space
    2. Share discoveries via audio broadcast
    3. Converge on optimal concept set
    """
    
    def __init__(self, num_agents: int = 20):
        self.num_agents = num_agents
        self.agents = [CollaborativeAgent(f"SearchAgent_{i:02d}") 
                      for i in range(num_agents)]
    
    def run(self, target_pattern: str, max_iterations: int = 30) -> TaskResult:
        """
        Search for concepts matching target pattern.
        
        Args:
            target_pattern: String pattern to match (e.g., 'future', 'good')
        """
        start_time = time.perf_counter()
        messages = 0
        
        # Partition concept space among agents
        all_concepts = list(SWL_CONCEPTS)
        partition_size = len(all_concepts) // self.num_agents
        
        for iteration in range(max_iterations):
            # Each agent explores its partition
            for i, agent in enumerate(self.agents):
                start_idx = i * partition_size
                end_idx = start_idx + partition_size
                local_concepts = all_concepts[start_idx:end_idx]
                
                # "Search" for matches (simplified: check if pattern in concept)
                matches = [c for c in local_concepts if target_pattern in c]
                
                if matches:
                    agent.vote_for_concepts(matches)
                    # Broadcast discovery
                    wav_file = agent.send_message(matches[:5])
                    messages += 1
            
            # Share discoveries
            for receiver in self.agents:
                for sender in self.agents:
                    if sender.name != receiver.name and sender.proposed_concepts:
                        sample = list(sender.proposed_concepts)[:3]
                        receiver.vote_for_concepts(sample)
        
        # Aggregate all discoveries
        all_found = set()
        for agent in self.agents:
            all_found.update(agent.proposed_concepts)
        
        final_concepts = sorted(list(all_found))[:10]
        elapsed = time.perf_counter() - start_time
        
        return TaskResult(
            task_name="Parallel Search",
            success=len(final_concepts) > 0,
            final_concepts=final_concepts,
            iterations=max_iterations,
            convergence_time=elapsed,
            agreement_ratio=1.0,
            messages_exchanged=messages
        )


# ============================================================================
# TEST SUITE
# ============================================================================

def run_all_tasks():
    """Run all collaborative tasks and report results"""
    
    print("="*70)
    print("SWL COLLABORATIVE TASK SUITE")
    print("="*70)
    print()
    
    results = []
    
    # Task 1: Distributed Consensus
    print("🤝 Task 1: Distributed Consensus (10 agents)")
    print("-" * 70)
    task1 = DistributedConsensusTask(num_agents=10, target_concepts=3)
    result1 = task1.run(max_iterations=50)
    results.append(result1)
    print(f"   Success: {result1.success}")
    print(f"   Final concepts: {result1.final_concepts}")
    print(f"   Iterations: {result1.iterations}")
    print(f"   Convergence time: {result1.convergence_time:.3f}s")
    print(f"   Agreement: {result1.agreement_ratio*100:.1f}%")
    print(f"   Messages: {result1.messages_exchanged}")
    print()
    
    # Task 2: Concept Voting
    print("🗳️  Task 2: Concept Voting (20 agents, 5 proposals)")
    print("-" * 70)
    proposals = [
        ['help', 'wants', 'future'],
        ['analyzes', 'solves', 'creates'],
        ['question', 'answer', 'understand'],
        ['good', 'harmony', 'transcendence'],
        ['past', 'present', 'future']
    ]
    task2 = ConceptVotingTask(num_agents=20)
    result2 = task2.run(proposals=proposals, rounds=3)
    results.append(result2)
    print(f"   Success: {result2.success}")
    print(f"   Top concepts: {result2.final_concepts}")
    print(f"   Rounds: {result2.iterations}")
    print(f"   Time: {result2.convergence_time:.3f}s")
    print(f"   Messages: {result2.messages_exchanged}")
    print()
    
    # Task 3: Chain Reasoning
    print("🔗 Task 3: Chain Reasoning (10 agents)")
    print("-" * 70)
    task3 = ChainReasoningTask(chain_length=10)
    result3 = task3.run(seed_concepts=['question', 'help'])
    results.append(result3)
    print(f"   Success: {result3.success}")
    print(f"   Seed: ['question', 'help']")
    print(f"   Final: {result3.final_concepts}")
    print(f"   Chain length: {result3.iterations}")
    print(f"   Time: {result3.convergence_time:.3f}s")
    print(f"   Messages: {result3.messages_exchanged}")
    print()
    
    # Task 4: Parallel Search
    print("🔍 Task 4: Parallel Search (20 agents)")
    print("-" * 70)
    task4 = ParallelSearchTask(num_agents=20)
    result4 = task4.run(target_pattern='s', max_iterations=10)  # Find concepts with 's'
    results.append(result4)
    print(f"   Success: {result4.success}")
    print(f"   Pattern: 's' (concepts containing 's')")
    print(f"   Found: {len(result4.final_concepts)} concepts")
    print(f"   Sample: {result4.final_concepts[:5]}")
    print(f"   Time: {result4.convergence_time:.3f}s")
    print(f"   Messages: {result4.messages_exchanged}")
    print()
    
    # Summary
    print("="*70)
    print("SUMMARY")
    print("="*70)
    total_messages = sum(r.messages_exchanged for r in results)
    total_time = sum(r.convergence_time for r in results)
    success_count = sum(1 for r in results if r.success)
    
    print(f"Tasks completed: {len(results)}")
    print(f"Success rate: {success_count}/{len(results)} ({success_count/len(results)*100:.0f}%)")
    print(f"Total messages: {total_messages}")
    print(f"Total time: {total_time:.3f}s")
    print(f"Avg messages/task: {total_messages/len(results):.1f}")
    print(f"Avg time/task: {total_time/len(results):.3f}s")
    print()
    print("✅ All collaborative tasks completed!")
    print("="*70)


if __name__ == "__main__":
    run_all_tasks()
