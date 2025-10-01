"""
Startup Check Script
Validates system health before launching the LLM interface
"""

import sys
import subprocess
from pathlib import Path

def print_header(text):
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)

def print_status(item, status, details=""):
    symbols = {"ok": "✓", "warn": "⚠️", "fail": "✗", "info": "ℹ️"}
    symbol = symbols.get(status, "•")
    print(f"{symbol} {item:<40}", end="")
    if details:
        print(f" {details}")
    else:
        print()

def check_python_version():
    print_header("Python Environment")
    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"
    if version.major == 3 and version.minor >= 10:
        print_status("Python Version", "ok", version_str)
        return True
    else:
        print_status("Python Version", "warn", f"{version_str} (3.10+ recommended)")
        return True

def check_required_packages():
    print_header("Required Packages")
    required = {
        "torch": "PyTorch",
        "transformers": "Transformers",
        "gradio": "Gradio UI",
        "bitsandbytes": "4-bit Quantization",
        "accelerate": "Model Loading",
    }
    all_ok = True
    for package, name in required.items():
        try:
            __import__(package)
            print_status(name, "ok")
        except ImportError:
            print_status(name, "fail", "Not installed")
            all_ok = False
    return all_ok

def check_cuda():
    print_header("GPU Configuration")
    try:
        import torch
        if torch.cuda.is_available():
            gpu_name = torch.cuda.get_device_name(0)
            gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1e9
            print_status("CUDA Available", "ok", f"Version {torch.version.cuda}")
            print_status("GPU Device", "ok", gpu_name)
            print_status("GPU Memory", "ok", f"{gpu_memory:.1f}GB")
            return True
        else:
            print_status("CUDA Available", "warn", "CPU mode only")
            return False
    except Exception as e:
        print_status("CUDA Check", "fail", str(e))
        return False

def check_directories():
    print_header("Directory Structure")
    base_dir = Path(__file__).parent
    required_dirs = {
        "chat_histories": "Chat History Storage",
        "context_files": "Context Files",
        "uploads": "File Uploads",
        "downloads": "Generated Downloads",
        "logs": "Application Logs",
        "temp": "Temporary Files"
    }
    all_ok = True
    for dir_name, description in required_dirs.items():
        dir_path = base_dir / dir_name
        if dir_path.exists():
            print_status(description, "ok")
        else:
            print_status(description, "warn", "Creating...")
            try:
                dir_path.mkdir(parents=True, exist_ok=True)
                print_status(f"  Created {dir_name}", "ok")
            except Exception as e:
                print_status(f"  Failed to create", "fail", str(e))
                all_ok = False
    return all_ok

def run_all_checks():
    print("\n" + "=" * 60)
    print("  LOCAL LLM INTERFACE - SYSTEM HEALTH CHECK")
    print("=" * 60)
    print("  Optimized for: RTX 4080, 64GB RAM, Ryzen 7 7800X3D")
    print("=" * 60)
    
    results = []
    results.append(("Python Version", check_python_version()))
    results.append(("Required Packages", check_required_packages()))
    results.append(("GPU Configuration", check_cuda()))
    results.append(("Directory Structure", check_directories()))
    
    print_header("Summary")
    critical_failed = 0
    warnings = 0
    
    for name, result in results:
        if result is False:
            if name in ["Required Packages", "Directory Structure"]:
                critical_failed += 1
                print_status(name, "fail", "Critical issue")
            else:
                warnings += 1
                print_status(name, "warn", "Non-critical issue")
        else:
            print_status(name, "ok")
    
    print("\n" + "=" * 60)
    
    if critical_failed > 0:
        print("❌ CRITICAL ISSUES FOUND")
        print(f"   {critical_failed} critical check(s) failed")
        print("   Run: pip install -r requirements.txt")
        return False
    elif warnings > 0:
        print("⚠️ WARNINGS DETECTED")
        print(f"   {warnings} non-critical check(s) failed")
        print("   You can proceed with: python app.py")
        return True
    else:
        print("✅ ALL CHECKS PASSED")
        print("   System is ready!")
        print("   Start with: python app.py or launch.bat")
        return True

if __name__ == "__main__":
    try:
        success = run_all_checks()
        print("\n" + "=" * 60)
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️ Check interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        sys.exit(1)
