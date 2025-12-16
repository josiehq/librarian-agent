#!/usr/bin/env python
"""
Librarian Agent - Main entry point
Orchestrates the entire multi-agent swarm system.
"""

import sys
import argparse
import os

# Add py/ to path so imports work
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'py'))

def main():
    parser = argparse.ArgumentParser(description='Librarian Agent - Multi-Agent Swarm')
    parser.add_argument('--mode', choices=['josie', 'memory', 'both'], default='josie',
                       help='Run mode: josie (orchestration), memory (Diplo service), or both')
    parser.add_argument('--task', type=str, default='Build a simple test script.',
                       help='Task to execute (for josie mode)')
    parser.add_argument('--api-key', type=str, help='Override LLM API key (sets AGENT_API_KEY env var)')
    parser.add_argument('--model', type=str, help='Override LLM model (sets AGENT_MODEL env var)')
    
    args = parser.parse_args()
    
    # Set environment variables if provided
    if args.api_key:
        os.environ['AGENT_API_KEY'] = args.api_key
    if args.model:
        os.environ['AGENT_MODEL'] = args.model
    
    if args.mode in ('josie', 'both'):
        print(f"\n>>> Starting Vertical Orchestration (Josie)...")
        try:
            from orchestration.josie import Josie
            import asyncio
            
            josie = Josie()
            result = asyncio.run(josie.run(args.task))
            print(f"\n>>> Orchestration Result: {result}")
        except Exception as e:
            print(f"ERROR: {e}", file=sys.stderr)
            sys.exit(1)
    
    if args.mode in ('memory', 'both'):
        print(f"\n>>> Starting Diplo Memory Service...")
        try:
            from memory.diplo import start_memory_service
            start_memory_service()
        except Exception as e:
            print(f"ERROR: {e}", file=sys.stderr)
            sys.exit(1)

if __name__ == '__main__':
    main()
