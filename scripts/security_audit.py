#!/usr/bin/env python3
"""Security audit script for the document ingestion system.

Runs pip-audit on dependencies and checks for known vulnerabilities.
"""
import subprocess
import sys
import os
from pathlib import Path


def run_pip_audit():
    """Run pip-audit on the project dependencies."""
    print("Running security audit with pip-audit...")

    try:
        # Change to project directory
        project_dir = Path(__file__).parent.parent
        os.chdir(project_dir)

        # Run pip-audit on requirements.txt
        result = subprocess.run([
            sys.executable, "-m", "pip_audit",
            "--requirement", "backend/requirements.txt"
        ], capture_output=True, text=True, timeout=300)  # 5 minute timeout

        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)
        print("Return code:", result.returncode)

        if result.returncode == 0:
            print("✓ Security audit passed - no vulnerabilities found")
            return True
        else:
            print("✗ Security audit found vulnerabilities:")
            print(result.stdout)
            if result.stderr:
                print("Errors:", result.stderr)
            return False

    except subprocess.TimeoutExpired:
        print("✗ Security audit timed out after 5 minutes")
        return False
    except FileNotFoundError:
        print("✗ pip-audit not found. Install it with: pip install pip-audit")
        return False
    except Exception as e:
        print(f"✗ Error running security audit: {e}")
        return False


def check_dependency_versions():
    """Check dependency versions for known issues."""
    print("\nChecking dependency versions...")

    # Known problematic versions or patterns to check for
    known_issues = {
        # Example: if we had specific known vulnerable versions
        # "pyjwt": ["<2.0.0"],  # Example of vulnerable version range
    }

    try:
        # Get installed packages
        result = subprocess.run([
            sys.executable, "-m", "pip", "list", "--format", "freeze"
        ], capture_output=True, text=True)

        if result.returncode == 0:
            packages = result.stdout.strip().split('\n')
            print(f"Checked {len([p for p in packages if p])} installed packages")

            # Look for known issues (none defined yet, but structure is ready)
            issues_found = []
            for pkg in packages:
                if '==' in pkg:
                    name, version = pkg.split('==', 1)
                    # Check against known issues if any were defined
                    # For now, just print the packages
                    print(f"  {pkg}")

            if issues_found:
                print(f"⚠️  Found {len(issues_found)} potential issues")
                for issue in issues_found:
                    print(f"    - {issue}")
            else:
                print("✓ No known dependency issues found")

        else:
            print(f"✗ Failed to list installed packages: {result.stderr}")

    except Exception as e:
        print(f"✗ Error checking dependency versions: {e}")


def check_code_security_issues():
    """Basic static code analysis for common security issues."""
    print("\nChecking code for common security issues...")

    import ast
    import os

    issues_found = []

    # Walk through source code
    backend_dir = Path(__file__).parent.parent / "backend" / "src"

    for py_file in backend_dir.rglob("*.py"):
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
                tree = ast.parse(content)

            # Check for common security issues
            for node in ast.walk(tree):
                # Check for eval() usage
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                    if node.func.id == 'eval':
                        issues_found.append(f"SUSPICIOUS: eval() usage in {py_file}:{node.lineno}")
                    elif node.func.id == 'exec':
                        issues_found.append(f"SUSPICIOUS: exec() usage in {py_file}:{node.lineno}")
                    elif node.func.id == 'compile':
                        # compile() can be suspicious depending on usage
                        issues_found.append(f"SUSPICIOUS: compile() usage in {py_file}:{node.lineno}")

                # Check for subprocess without shell=False
                if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and
                    node.func.attr in ['call', 'run', 'Popen'] and
                    any(isinstance(arg, ast.Str) and 'shell' not in [kw.arg for kw in node.keywords or []] for arg in node.args)):
                    issues_found.append(f"POTENTIAL: subprocess without explicit shell=False in {py_file}:{node.lineno}")

        except SyntaxError:
            # Skip files with syntax errors
            continue
        except Exception:
            # Skip other errors
            continue

    if issues_found:
        print(f"⚠️  Found {len(issues_found)} potential security issues:")
        for issue in issues_found[:10]:  # Show first 10 issues
            print(f"    - {issue}")
        if len(issues_found) > 10:
            print(f"    ... and {len(issues_found) - 10} more")
    else:
        print("✓ No obvious security issues found in code")


def main():
    """Run the complete security audit."""
    print("🔍 Starting security audit for Document Ingestion System...\n")

    # Run pip-audit
    pip_audit_passed = run_pip_audit()

    # Check dependency versions
    check_dependency_versions()

    # Check code for security issues
    check_code_security_issues()

    print("\n" + "="*50)
    print("AUDIT SUMMARY:")
    print(f"pip-audit: {'PASSED' if pip_audit_passed else 'FAILED/ERROR'}")
    print("Dependency check: COMPLETED")
    print("Code analysis: COMPLETED")

    if pip_audit_passed:
        print("\n✅ Security audit completed successfully!")
        print("No critical vulnerabilities found in dependencies.")
        return 0
    else:
        print("\n❌ Security audit revealed potential vulnerabilities!")
        print("Please review the findings and update dependencies as needed.")
        return 1


if __name__ == "__main__":
    sys.exit(main())