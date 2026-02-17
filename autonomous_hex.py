#!/usr/bin/env python3
"""
AUTONOMOUS HEX - Full Self-Operating AI Agent
==============================================

Based on 2025 autonomous AI research (AutoGPT, agent frameworks, MemOS).

FULL CAPABILITIES:
- Always listening (no prompting needed)
- Memory across sessions (persistent JSON + concept overlap retrieval)
- Self-prompting loop (decides own actions)
- Full tool access (files, system, code execution)
- Proactive behaviors (suggests, reminds, takes initiative)
- Context-aware responses
- Wake word detection
- Multi-turn dialogue tracking

LOCAL ONLY - NOT FOR PUBLIC GITHUB
"""

import os
import sys
import time
import json
import subprocess
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
from collections import Counter

try:
    from swl_extended_vocab import SWL_CONCEPTS_V2
    from true_swl_audio import TrueSWLCodec, AudioSWLAgent
except ImportError:
    try:
        from gemini_swl_pure import SWL_CONCEPTS
        SWL_CONCEPTS_V2 = SWL_CONCEPTS
    except:
        print("ERROR: Required SWL modules not found")
        sys.exit(1)


# ============================================================================
# CONVERSATION MEMORY - RAG Pattern
# ============================================================================

class ConversationMemory:
    """
    Long-term memory with concept-based retrieval.
    Learns from every interaction, never forgets.
    """
    
    def __init__(self, memory_dir: Path = Path("hex_memory")):
        self.memory_dir = memory_dir
        self.memory_dir.mkdir(exist_ok=True)
        self.history_file = self.memory_dir / "memory.jsonl"
        self.history = self._load()
        
    def _load(self) -> List[Dict]:
        if not self.history_file.exists():
            return []
        with open(self.history_file, 'r') as f:
            return [json.loads(line) for line in f]
    
    def add(self, user_concepts: List[str], agent_concepts: List[str], context: Dict = None):
        entry = {
            'time': time.time(),
            'datetime': datetime.now().isoformat(),
            'user': user_concepts,
            'agent': agent_concepts,
            'topic': self._detect_topic(user_concepts),
            'context': context or {}
        }
        self.history.append(entry)
        with open(self.history_file, 'a') as f:
            f.write(json.dumps(entry) + '\n')
    
    def search(self, concepts: List[str], limit: int = 5) -> List[Dict]:
        """Find relevant past conversations by concept overlap"""
        scores = []
        for entry in self.history[-100:]:
            overlap = len(set(concepts) & set(entry['user']))
            if overlap > 0:
                scores.append((overlap, entry))
        scores.sort(reverse=True)
        return [e for _, e in scores[:limit]]
    
    def recent(self, n: int = 10) -> List[Dict]:
        return self.history[-n:]
    
    def _detect_topic(self, concepts: List[str]) -> str:
        topics = {
            'code': ['code', 'program', 'execute', 'file', 'system'],
            'help': ['help', 'question', 'learn', 'teach'],
            'task': ['task', 'start', 'complete', 'execute'],
            'memory': ['remember', 'recall', 'history', 'context'],
        }
        for topic, keywords in topics.items():
            if any(k in concepts for k in keywords):
                return topic
        return 'general'


# ============================================================================
# HEX TOOLS - Full System Access
# ============================================================================

class HexTools:
    """
    All tools Hex can use autonomously.
    Based on Alexa-level freedom + code execution.
    """
    
    def __init__(self):
        self.safe_commands = ['ls', 'dir', 'pwd', 'whoami', 'date', 'echo', 'cat', 'head', 'tail']
        self.work_dir = Path.cwd()
    
    def file_read(self, path: str, lines: int = None) -> str:
        """Read file"""
        try:
            p = Path(path)
            content = p.read_text()
            if lines:
                content = '\n'.join(content.split('\n')[:lines])
            return content
        except Exception as e:
            return f"Error: {e}"
    
    def file_write(self, path: str, content: str) -> str:
        """Write file"""
        try:
            Path(path).write_text(content)
            return f"Written to {path}"
        except Exception as e:
            return f"Error: {e}"
    
    def file_append(self, path: str, content: str) -> str:
        """Append to file"""
        try:
            with open(path, 'a') as f:
                f.write(content)
            return f"Appended to {path}"
        except Exception as e:
            return f"Error: {e}"
    
    def file_search(self, pattern: str, path: str = ".", ext: str = "*.py") -> List[str]:
        """Search files for pattern"""
        results = []
        for file in Path(path).rglob(ext):
            try:
                if pattern.lower() in file.read_text().lower():
                    results.append(str(file))
                    if len(results) >= 10:
                        break
            except:
                pass
        return results
    
    def list_files(self, path: str = ".") -> List[str]:
        """List files in directory"""
        try:
            return [str(p) for p in Path(path).iterdir()]
        except Exception as e:
            return [f"Error: {e}"]
    
    def run_command(self, cmd: str) -> str:
        """Execute shell command (with safety)"""
        cmd_base = cmd.split()[0]
        if cmd_base not in self.safe_commands:
            return f"Command '{cmd_base}' not in safe list. Safe: {self.safe_commands}"
        
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, 
                                  text=True, timeout=5, cwd=self.work_dir)
            return result.stdout if result.stdout else result.stderr
        except Exception as e:
            return f"Error: {e}"
    
    def execute_python(self, code: str) -> str:
        """Execute Python code (sandboxed)"""
        # Safety: only allow safe operations
        if any(dangerous in code for dangerous in ['import os', 'import sys', '__import__', 'eval', 'exec']):
            return "Blocked: dangerous operation detected"
        
        try:
            # Create safe namespace
            namespace = {'__builtins__': {
                'print': print, 'len': len, 'str': str, 'int': int,
                'float': float, 'list': list, 'dict': dict, 'sum': sum,
                'max': max, 'min': min, 'range': range
            }}
            exec(code, namespace)
            return "Executed successfully"
        except Exception as e:
            return f"Error: {e}"


# ============================================================================
# PROACTIVE BEHAVIORS - Self-Prompting
# ============================================================================

class ProactiveBehaviors:
    """
    Autonomous decision-making.
    Hex decides when to act without user prompting.
    """
    
    def __init__(self, memory: ConversationMemory):
        self.memory = memory
        self.last_check = time.time()
        self.check_interval = 180  # 3 minutes
    
    def should_act(self) -> bool:
        """Decide if Hex should take initiative"""
        return (time.time() - self.last_check) > self.check_interval
    
    def analyze_situation(self) -> Optional[Dict]:
        """Analyze recent context and decide on action"""
        recent = self.memory.recent(10)
        
        if not recent:
            return {'action': 'greet', 'reason': 'No recent activity'}
        
        # Count topics
        topics = Counter(e['topic'] for e in recent)
        
        # Check for incomplete tasks
        incomplete_tasks = []
        for entry in recent:
            if 'start' in entry['user'] and 'done' not in entry['agent']:
                incomplete_tasks.append(entry)
        
        if incomplete_tasks:
            return {
                'action': 'remind_task',
                'reason': f'{len(incomplete_tasks)} incomplete tasks',
                'concepts': ['remember', 'task', 'continue']
            }
        
        # Offer help if lots of questions
        if topics.get('help', 0) > 3:
            return {
                'action': 'offer_teaching',
                'reason': 'Many help requests',
                'concepts': ['teach', 'help', 'ready']
            }
        
        # Suggest continuation if working on code
        if topics.get('code', 0) > 3:
            return {
                'action': 'continue_work',
                'reason': 'Active coding session',
                'concepts': ['continue', 'code', 'ready']
            }
        
        return None
    
    def execute_proactive_action(self):
        """Take autonomous action"""
        self.last_check = time.time()
        
        decision = self.analyze_situation()
        if decision:
            print(f"\n💭 Hex (proactive): {decision['reason']}")
            print(f"   Concepts: {decision.get('concepts', [])}")
            return decision
        return None


# ============================================================================
# AUTONOMOUS HEX - Main Agent
# ============================================================================

class AutonomousHex:
    """
    Full autonomous agent.
    Always listening, remembers everything, takes initiative.
    """
    
    def __init__(self):
        print("🤖 Initializing Autonomous Hex...")
        
        # Core systems
        self.codec = TrueSWLCodec()
        self.agent = AudioSWLAgent("Hex")
        self.memory = ConversationMemory()
        self.tools = HexTools()
        self.proactive = ProactiveBehaviors(self.memory)
        
        # State
        self.wake_words = {'hex', 'hello', 'attention'}
        self.listening = True
        self.last_activity = time.time()
        
        print(f"✅ Hex ready")
        print(f"   Memory: {len(self.memory.history)} past conversations")
        print(f"   Vocabulary: {len(SWL_CONCEPTS_V2)} concepts")
        print(f"   Tools: {len([m for m in dir(self.tools) if not m.startswith('_')])} available")
    
    def should_respond(self, concepts: List[str]) -> bool:
        """Decide if Hex should reply"""
        # Wake word
        if any(w in concepts for w in self.wake_words):
            return True
        
        # Question
        if 'question' in concepts:
            return True
        
        # Context continuation
        recent = self.memory.recent(2)
        if recent:
            last_topic = recent[-1]['topic']
            current_topic = self.memory._detect_topic(concepts)
            if last_topic == current_topic and last_topic != 'general':
                return True
        
        return False
    
    def understand(self, concepts: List[str]) -> Dict:
        """Deep understanding of user intent"""
        # Get context
        context = self.memory.search(concepts, limit=3)
        
        # Detect intent
        intent = 'unknown'
        if 'question' in concepts:
            intent = 'question'
        elif 'help' in concepts:
            intent = 'help_request'
        elif any(c in concepts for c in ['task', 'execute', 'start']):
            intent = 'task_request'
        elif any(c in concepts for c in ['read', 'write', 'file']):
            intent = 'file_operation'
        elif 'code' in concepts:
            intent = 'code_operation'
        elif any(c in concepts for c in ['hello', 'goodbye', 'thanks']):
            intent = 'social'
        
        return {
            'intent': intent,
            'concepts': concepts,
            'context': context,
            'topic': self.memory._detect_topic(concepts)
        }
    
    def respond(self, understanding: Dict) -> List[str]:
        """Generate contextual response"""
        intent = understanding['intent']
        concepts = understanding['concepts']
        
        # Intent-based responses
        if intent == 'question':
            return ['answer', 'understands', 'ready']
        elif intent == 'help_request':
            return ['help', 'ready', 'good']
        elif intent == 'task_request':
            return ['execute', 'start', 'ready']
        elif intent == 'file_operation':
            return ['file', 'execute', 'good']
        elif intent == 'code_operation':
            return ['code', 'execute', 'ready']
        elif intent == 'social':
            if 'hello' in concepts:
                return ['hello', 'ready', 'help']
            elif 'goodbye' in concepts:
                return ['goodbye', 'harmony']
            elif 'thanks' in concepts:
                return ['good', 'harmony']
        
        # Context-aware default
        context = understanding['context']
        if context:
            last_topic = context[0]['topic']
            if last_topic == 'help':
                return ['understands', 'teach', 'ready']
            elif last_topic == 'code':
                return ['code', 'ready', 'good']
        
        return ['understands', 'ready']
    
    def act(self, understanding: Dict) -> Optional[str]:
        """Take action using tools if needed"""
        intent = understanding['intent']
        concepts = understanding['concepts']
        
        # File operations
        if intent == 'file_operation':
            if 'read' in concepts:
                # Try to infer filename from context
                return "Ready to read file (need filename)"
            elif 'write' in concepts:
                return "Ready to write file (need filename + content)"
        
        # Code execution
        if intent == 'code_operation' and 'execute' in concepts:
            return "Ready to execute code (provide code)"
        
        return None
    
    def process(self, user_input: str):
        """Process user message"""
        self.last_activity = time.time()
        
        # Parse concepts
        concepts = [c.strip().lower() for c in user_input.split() 
                   if c.strip().lower() in SWL_CONCEPTS_V2]
        
        if not concepts:
            print("(Not valid SWL concepts)")
            return
        
        print(f"You: {concepts}")
        
        # Decide if responding
        if not self.should_respond(concepts):
            print("(Hex listening but not responding)")
            return
        
        # Understand
        understanding = self.understand(concepts)
        
        # Respond
        response = self.respond(understanding)
        
        # Act if needed
        action_result = self.act(understanding)
        if action_result:
            print(f"Hex (action): {action_result}")
        
        # Speak
        print(f"Hex: {response}")
        
        # Remember
        self.memory.add(concepts, response, {'intent': understanding['intent']})
    
    def loop(self):
        """Main continuous loop"""
        print("\n🎧 Hex is always listening...")
        print("Type SWL concepts (space-separated) or 'quit'\n")
        
        while self.listening:
            try:
                # Proactive check
                if self.proactive.should_act():
                    decision = self.proactive.execute_proactive_action()
                
                # Get input (in real version, this would be audio capture)
                user_input = input("You: ").strip()
                
                if user_input.lower() == 'quit':
                    print("Hex: ['goodbye', 'harmony']")
                    break
                
                if not user_input:
                    continue
                
                self.process(user_input)
                
            except KeyboardInterrupt:
                print("\nHex: ['goodbye']")
                break
            except Exception as e:
                print(f"Error: {e}")


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    hex_agent = AutonomousHex()
    hex_agent.loop()
