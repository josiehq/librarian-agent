"""
JosieDesk Dependency Verification Script
Checks all components are properly configured and can communicate.
"""

import sys
import json
import subprocess
from pathlib import Path

def check_python_packages():
    """Verify all required Python packages are installed."""
    print("\n📦 Checking Python Dependencies...")
    
    required_packages = {
        'httpx': '0.24.0',
        'flask': '2.3.0',
        'pyautogen': '0.2.0',
        'llama_index': '0.9.0',
    }
    
    missing = []
    for package, min_version in required_packages.items():
        try:
            mod = __import__(package if package != 'pyautogen' else 'autogen')
            print(f"  ✅ {package:<15} installed")
        except ImportError:
            missing.append(package)
            print(f"  ❌ {package:<15} MISSING")
    
    return len(missing) == 0

def check_go_modules():
    """Verify Go module dependencies."""
    print("\n🔧 Checking Go Module Dependencies...")
    
    required_modules = {
        'github.com/gorilla/websocket': 'WebSocket support',
        'github.com/charmbracelet/bubbles': 'TUI bubbles',
        'github.com/charmbracelet/bubbletea': 'TUI framework',
        'github.com/charmbracelet/lipgloss': 'TUI styling',
    }
    
    go_mod_path = Path('go.mod')
    if not go_mod_path.exists():
        print("  ❌ go.mod not found")
        return False
    
    content = go_mod_path.read_text()
    all_found = True
    
    for module, description in required_modules.items():
        if module in content:
            print(f"  ✅ {module:<40} {description}")
        else:
            print(f"  ❌ {module:<40} MISSING")
            all_found = False
    
    return all_found

def check_file_structure():
    """Verify all required files exist."""
    print("\n📁 Checking File Structure...")
    
    required_files = {
        'types.go': 'Struct definitions',
        'kirktower.go': 'Control tower logic',
        'mcp_server.go': 'MCP server',
        'tower_cll.go': 'CLI interface',
        'josiedesk_core.py': 'Core orchestration',
        'josiedesk_hybrid.py': 'Hybrid runtime',
        'josiedesk_memory.py': 'Memory management',
        'setup.py': 'Python package config',
        'go.mod': 'Go module config',
    }
    
    all_found = True
    for filename, description in required_files.items():
        path = Path(filename)
        if path.exists():
            print(f"  ✅ {filename:<25} {description}")
        else:
            print(f"  ❌ {filename:<25} MISSING")
            all_found = False
    
    return all_found

def check_api_compatibility():
    """Verify Go and Python API contracts match."""
    print("\n🔗 Checking API Compatibility...")
    
    checks = [
        {
            "name": "MCP Server Handler",
            "go_file": "mcp_server.go",
            "py_file": "josiedesk_hybrid.py",
            "patterns": [
                ("ServeHTTP", "call_mcp_tool"),
                ("JSON-RPC", "jsonrpc"),
                ("container_exec", "container_exec"),
                ("memory_commit", "memory_commit"),
            ]
        }
    ]
    
    all_good = True
    for check in checks:
        print(f"\n  Checking {check['name']}...")
        
        go_path = Path(check['go_file'])
        py_path = Path(check['py_file'])
        
        if not (go_path.exists() and py_path.exists()):
            print(f"    ❌ Files not found")
            continue
        
        go_content = go_path.read_text()
        py_content = py_path.read_text()
        
        for go_pattern, py_pattern in check['patterns']:
            go_found = go_pattern in go_content
            py_found = py_pattern in py_content
            
            if go_found and py_found:
                print(f"    ✅ {go_pattern:<20} ↔ {py_pattern}")
            else:
                print(f"    ❌ Mismatch: {go_pattern} or {py_pattern}")
                all_good = False
    
    return all_good

def check_port_availability():
    """Check if required ports are available."""
    print("\n🌐 Checking Port Availability...")
    
    ports = {
        8080: "Kirktower Control Kernel",
        8081: "Diplo Memory Service",
    }
    
    for port, service in ports.items():
        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('127.0.0.1', port))
            sock.close()
            
            if result == 0:
                print(f"  ⚠️  Port {port:<5} IN USE (service may already be running)")
            else:
                print(f"  ✅ Port {port:<5} available - {service}")
        except Exception as e:
            print(f"  ❌ Port {port:<5} check failed: {e}")
    
    return True

def main():
    """Run all verification checks."""
    print("=" * 60)
    print("JosieDesk System Verification")
    print("=" * 60)
    
    results = {
        "Python Packages": check_python_packages(),
        "Go Modules": check_go_modules(),
        "File Structure": check_file_structure(),
        "API Compatibility": check_api_compatibility(),
        "Port Availability": check_port_availability(),
    }
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for check, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{check:<30} {status}")
    
    print(f"\nOverall: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n✅ All systems ready! Run: python3 josiedesk_core.py")
        return 0
    else:
        print(f"\n❌ {total - passed} issues found. Run: pip install -e .")
        return 1

if __name__ == "__main__":
    sys.exit(main())
