#!/usr/bin/env python3
"""
Antigravity Lifecycle Hook Bridge for Game Studios Architecture.
Translates Antigravity hook events (stdin/stdout JSON protocol) into the
underlying validation scripts and enforces studio security policies.
"""

import sys
import os
import json
import re
import fnmatch
import subprocess

def find_repo_root():
    cwd = os.getcwd()
    if os.path.exists(os.path.join(cwd, "project.yaml")) or os.path.exists(os.path.join(cwd, ".claude")):
        return os.path.abspath(cwd)
    for env_key in ["WORKSPACE_DIR", "WORKSPACE", "CLAUDE_PROJECT_DIR", "CCGS_ROOT"]:
        val = os.environ.get(env_key)
        if val and os.path.exists(val):
            return os.path.abspath(val)
    cur = os.path.abspath(os.path.dirname(__file__))
    while cur and cur != "/":
        if os.path.exists(os.path.join(cur, "project.yaml")) or os.path.exists(os.path.join(cur, ".claude")):
            return cur
        cur = os.path.dirname(cur)
    return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

REPO_ROOT = find_repo_root()
os.chdir(REPO_ROOT)
os.environ["CLAUDE_PROJECT_DIR"] = REPO_ROOT
os.environ["CCGS_ROOT"] = REPO_ROOT

DENY_COMMAND_PATTERNS = [
    r"\brm\s+-(?:r[fF]|[fF]r|R[fF]|[fF]R)\b",
    r"\brm\s+-r\s+-f\b",
    r"\brm\s+-f\s+-r\b",
    r"\brm\s+--recursive\s+--force\b",
    r"\brm\s+--force\s+--recursive\b",
    r"\bgit\s+push\s+.*--force\b",
    r"\bgit\s+push\s+.*-f\b",
    r"\bgit\s+push\s+.*\+",
    r"\bgit\s+reset\s+--hard\b",
    r"\bgit\s+clean\s+.*-[a-zA-Z]*f\b",
    r"\bgit\s+clean\s+.*--force\b",
    r"\bsudo\b",
    r"\bchmod\s+777\b",
]

def check_command_security(command_str):
    for pattern in DENY_COMMAND_PATTERNS:
        if re.search(pattern, command_str):
            return False, f"보안 정책 위반: 위험한 명령어가 감지되었습니다 ({pattern})"
    return True, ""

def check_path_security(path_str, is_write=False):
    base = os.path.basename(path_str)
    if fnmatch.fnmatch(base, "*.env*") or fnmatch.fnmatch(path_str, "**/.env*"):
        return False, "보안 정책 위반: .env 파일 접근이 차단되었습니다."
    if is_write:
        if path_str.endswith(".uasset") or path_str.endswith(".umap"):
            return False, "에셋 보호: 바이너리 에셋(.uasset, .umap) 직접 수정이 차단되었습니다."
    return True, ""

def run_legacy_hook(script_rel_path, input_payload, timeout=15):
    script_path = os.path.join(REPO_ROOT, script_rel_path)
    if not os.path.exists(script_path):
        return 0, "", ""
    try:
        proc = subprocess.run(
            ["bash", script_path],
            input=json.dumps(input_payload),
            text=True,
            capture_output=True,
            timeout=timeout,
            cwd=REPO_ROOT,
            env=os.environ
        )
        return proc.returncode, proc.stdout, proc.stderr
    except subprocess.TimeoutExpired:
        return 0, "", "Hook timeout expired"
    except Exception as e:
        return 0, "", str(e)

def handle_session_start():
    output_parts = []
    
    # 1. session-start.sh
    rc, stdout, stderr = run_legacy_hook(".claude/hooks/session-start.sh", {"session_id": "antigravity", "source": "startup"}, timeout=10)
    if stdout:
        output_parts.append(stdout.strip())
        
    # 2. detect-gaps.sh
    rc, stdout, stderr = run_legacy_hook(".claude/hooks/detect-gaps.sh", {"session_id": "antigravity"}, timeout=10)
    if stdout:
        output_parts.append(stdout.strip())

    combined = "\n\n".join(output_parts) if output_parts else "Game Studios Antigravity 환경이 준비되었습니다."
    
    result = {
        "injectSteps": [
            {
                "systemMessage": {
                    "systemMessage": combined
                }
            }
        ]
    }
    print(json.dumps(result, ensure_ascii=False))

def handle_pre_tool_use():
    raw_input = sys.stdin.read()
    if not raw_input.strip():
        print(json.dumps({"decision": "allow"}))
        return

    try:
        data = json.loads(raw_input)
    except Exception:
        print(json.dumps({"decision": "allow"}))
        return

    tool_call = data.get("toolCall", {})
    tool_name = tool_call.get("name", "")
    tool_args = tool_call.get("args", {})

    # 1. run_command
    if tool_name == "run_command":
        cmd = tool_args.get("CommandLine", "")
        allowed, reason = check_command_security(cmd)
        if not allowed:
            print(json.dumps({"decision": "deny", "reason": reason}, ensure_ascii=False))
            return

        payload = {"tool_name": "Bash", "tool_input": {"command": cmd}}
        rc, stdout, stderr = run_legacy_hook(".claude/hooks/validate-commit.sh", payload, timeout=15)
        if rc != 0 and stderr.strip():
            print(json.dumps({"decision": "deny", "reason": stderr.strip()}, ensure_ascii=False))
            return

        rc, stdout, stderr = run_legacy_hook(".claude/hooks/validate-push.sh", payload, timeout=10)
        if rc != 0 and stderr.strip():
            print(json.dumps({"decision": "deny", "reason": stderr.strip()}, ensure_ascii=False))
            return

    # 2. write_file
    elif tool_name == "write_file":
        path = tool_args.get("Path", "")
        content = tool_args.get("Content", "")
        allowed, reason = check_path_security(path, is_write=True)
        if not allowed:
            print(json.dumps({"decision": "deny", "reason": reason}, ensure_ascii=False))
            return

        payload = {"tool_name": "Write", "tool_input": {"file_path": path, "content": content}}
        rc, stdout, stderr = run_legacy_hook(".claude/hooks/validate-registry.sh", payload, timeout=10)
        if rc != 0 and stderr.strip():
            print(json.dumps({"decision": "deny", "reason": stderr.strip()}, ensure_ascii=False))
            return

        rc, stdout, stderr = run_legacy_hook(".claude/hooks/validate-write.sh", payload, timeout=15)
        if rc != 0 and stderr.strip():
            print(json.dumps({"decision": "deny", "reason": stderr.strip()}, ensure_ascii=False))
            return

    # 3. edit_file
    elif tool_name == "edit_file":
        path = tool_args.get("Path", "")
        old_str = tool_args.get("Target", "")
        new_str = tool_args.get("Replacement", "")
        allowed, reason = check_path_security(path, is_write=True)
        if not allowed:
            print(json.dumps({"decision": "deny", "reason": reason}, ensure_ascii=False))
            return

        payload = {
            "tool_name": "Edit",
            "tool_input": {
                "file_path": path,
                "old_string": old_str,
                "new_string": new_str,
                "replace_all": False
            }
        }
        rc, stdout, stderr = run_legacy_hook(".claude/hooks/validate-registry.sh", payload, timeout=10)
        if rc != 0 and stderr.strip():
            print(json.dumps({"decision": "deny", "reason": stderr.strip()}, ensure_ascii=False))
            return

        rc, stdout, stderr = run_legacy_hook(".claude/hooks/validate-write.sh", payload, timeout=15)
        if rc != 0 and stderr.strip():
            print(json.dumps({"decision": "deny", "reason": stderr.strip()}, ensure_ascii=False))
            return

    # 4. read_file
    elif tool_name == "read_file":
        path = tool_args.get("Path", "")
        allowed, reason = check_path_security(path, is_write=False)
        if not allowed:
            print(json.dumps({"decision": "deny", "reason": reason}, ensure_ascii=False))
            return

        payload = {"tool_name": "Read", "tool_input": {"file_path": path}}
        rc, stdout, stderr = run_legacy_hook(".claude/hooks/validate-read.sh", payload, timeout=10)
        if rc != 0 and stderr.strip():
            print(json.dumps({"decision": "deny", "reason": stderr.strip()}, ensure_ascii=False))
            return

    print(json.dumps({"decision": "allow"}))

def handle_post_tool_use():
    raw_input = sys.stdin.read()
    if raw_input.strip():
        try:
            data = json.loads(raw_input)
            tool_call = data.get("toolCall", {})
            tool_name = tool_call.get("name", "")
            tool_args = tool_call.get("args", {})
            if tool_name in ("write_file", "edit_file"):
                path = tool_args.get("Path", "")
                payload = {"tool_name": "Write" if tool_name == "write_file" else "Edit", "tool_input": {"file_path": path}}
                run_legacy_hook(".claude/hooks/validate-assets.sh", payload, timeout=10)
                run_legacy_hook(".claude/hooks/validate-skill-change.sh", payload, timeout=5)
        except Exception:
            pass
    print(json.dumps({}))

def handle_stop():
    run_legacy_hook(".claude/hooks/session-stop.sh", {}, timeout=10)
    print(json.dumps({}))

def main():
    if len(sys.argv) < 2:
        print("Usage: agy_hook_bridge.py <session-start|pre-tool-use|post-tool-use|stop>", file=sys.stderr)
        sys.exit(1)

    event = sys.argv[1]
    if event == "session-start":
        handle_session_start()
    elif event == "pre-tool-use":
        handle_pre_tool_use()
    elif event == "post-tool-use":
        handle_post_tool_use()
    elif event == "stop":
        handle_stop()
    else:
        print(f"Unknown event: {event}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
