#!/usr/bin/env python3
"""
Multi-Agent Report & Memory Tool
Consolidated zero-dependency utility for:
1. Compiling Markdown reports (.ai/reports/md/) into styled HTML (.ai/reports/html/).
2. Logging stage outputs to .ai/memory/ and registering in INDEX.md.
3. Verifying the multi-agent architecture setup.

Usage:
    # Compile single report or all reports
    python .ai/report_tool.py [path_to_report.md]

    # Log memory artifact
    python .ai/report_tool.py --log --stage analysis --agent "Antigravity Gemini 3.8" --topic jwt-auth --summary "Analyzed JWT validation"

    # Verify AI architecture
    python .ai/report_tool.py --verify
"""

import argparse
import html
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

VALID_STAGES = ["analysis", "plan", "implementation", "testing", "review", "debug"]

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  <style>
    :root {{
      --bg: #0f172a;
      --card-bg: #1e293b;
      --card-border: #334155;
      --text: #f8fafc;
      --text-muted: #94a3b8;
      --accent: #38bdf8;
      --success: #22c55e;
      --danger: #ef4444;
      --code-bg: #090d16;
      --table-stripe: #182234;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      background-color: var(--bg);
      color: var(--text);
      line-height: 1.6;
      padding: 2rem 1rem;
    }}
    .container {{ max-width: 960px; margin: 0 auto; }}
    .header-card {{
      background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
      border: 1px solid var(--card-border);
      border-radius: 12px;
      padding: 2rem;
      margin-bottom: 2rem;
      box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    }}
    .badge {{
      display: inline-block;
      padding: 0.35rem 0.75rem;
      border-radius: 9999px;
      font-size: 0.85rem;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      margin-bottom: 1rem;
    }}
    .badge-analysis {{ background: rgba(56, 189, 248, 0.2); color: var(--accent); border: 1px solid var(--accent); }}
    .badge-plan {{ background: rgba(168, 85, 247, 0.2); color: #c084fc; border: 1px solid #c084fc; }}
    .badge-test-run {{ background: rgba(34, 197, 94, 0.2); color: var(--success); border: 1px solid var(--success); }}
    .badge-failure {{ background: rgba(239, 68, 68, 0.2); color: var(--danger); border: 1px solid var(--danger); }}
    h1 {{ font-size: 2rem; margin-bottom: 0.5rem; color: #fff; }}
    .meta {{ color: var(--text-muted); font-size: 0.9rem; }}
    .content-card {{
      background-color: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 12px;
      padding: 2.5rem;
      box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }}
    h2 {{
      font-size: 1.5rem;
      color: var(--accent);
      margin: 2rem 0 1rem;
      padding-bottom: 0.4rem;
      border-bottom: 1px solid var(--card-border);
    }}
    h3 {{ font-size: 1.2rem; color: #e2e8f0; margin: 1.5rem 0 0.75rem; }}
    p, ul, ol {{ margin-bottom: 1.25rem; color: #cbd5e1; }}
    ul, ol {{ padding-left: 1.75rem; }}
    li {{ margin-bottom: 0.4rem; }}
    code {{
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
      font-size: 0.9em;
      background-color: var(--code-bg);
      padding: 0.2rem 0.4rem;
      border-radius: 4px;
      color: #f472b6;
    }}
    pre {{
      background-color: var(--code-bg);
      border: 1px solid var(--card-border);
      border-radius: 8px;
      padding: 1.25rem;
      overflow-x: auto;
      margin-bottom: 1.5rem;
    }}
    pre code {{ background: none; padding: 0; color: #e2e8f0; }}
    table {{ width: 100%; border-collapse: collapse; margin-bottom: 1.5rem; }}
    th, td {{ padding: 0.75rem 1rem; text-align: left; border: 1px solid var(--card-border); }}
    th {{ background-color: #131c2e; color: #f1f5f9; font-weight: 600; }}
    tr:nth-child(even) {{ background-color: var(--table-stripe); }}
    blockquote {{
      border-left: 4px solid var(--accent);
      padding: 0.75rem 1.25rem;
      margin-bottom: 1.25rem;
      background-color: rgba(56, 189, 248, 0.08);
      color: #cbd5e1;
      border-radius: 0 8px 8px 0;
    }}
    footer {{ text-align: center; margin-top: 3rem; color: var(--text-muted); font-size: 0.85rem; }}
  </style>
</head>
<body>
  <div class="container">
    <div class="header-card">
      <span class="badge {badge_class}">{badge_text}</span>
      <h1>{title}</h1>
      <div class="meta">Generated: {generated_time} &bull; Type: {report_type}</div>
    </div>
    <div class="content-card">
      {body_html}
    </div>
    <footer>Expense Vision AI Multi-Agent System</footer>
  </div>
</body>
</html>
"""

def parse_markdown(md_text: str) -> str:
    lines = md_text.splitlines()
    html_lines = []
    in_code = False
    in_table = False
    in_ul = False
    in_ol = False

    def close_lists():
        nonlocal in_ul, in_ol
        res = ""
        if in_ul:
            res += "</ul>\n"
            in_ul = False
        if in_ol:
            res += "</ol>\n"
            in_ol = False
        return res

    for line in lines:
        stripped = line.strip()

        if stripped.startswith("```"):
            if in_code:
                html_lines.append("</code></pre>")
                in_code = False
            else:
                html_lines.append(close_lists())
                lang = stripped[3:].strip()
                html_lines.append(f'<pre><code class="language-{lang}">')
                in_code = True
            continue

        if in_code:
            html_lines.append(html.escape(line))
            continue

        if not stripped:
            html_lines.append(close_lists())
            if in_table:
                html_lines.append("</tbody></table>")
                in_table = False
            continue

        if stripped.startswith("|") and stripped.endswith("|"):
            cells = [c.strip() for c in stripped.split("|")[1:-1]]
            if all(set(c).issubset({"-", ":", " "}) for c in cells):
                continue
            if not in_table:
                html_lines.append(close_lists())
                html_lines.append("<table><thead><tr>")
                for c in cells:
                    html_lines.append(f"<th>{inline_format(c)}</th>")
                html_lines.append("</tr></thead><tbody>")
                in_table = True
            else:
                html_lines.append("<tr>")
                for c in cells:
                    html_lines.append(f"<td>{inline_format(c)}</td>")
                html_lines.append("</tr>")
            continue
        elif in_table:
            html_lines.append("</tbody></table>")
            in_table = False

        if stripped.startswith("### "):
            html_lines.append(close_lists())
            html_lines.append(f"<h3>{inline_format(stripped[4:])}</h3>")
            continue
        if stripped.startswith("## "):
            html_lines.append(close_lists())
            html_lines.append(f"<h2>{inline_format(stripped[3:])}</h2>")
            continue
        if stripped.startswith("# "):
            html_lines.append(close_lists())
            html_lines.append(f"<h1>{inline_format(stripped[2:])}</h1>")
            continue

        if stripped.startswith("> "):
            html_lines.append(close_lists())
            html_lines.append(f"<blockquote>{inline_format(stripped[2:])}</blockquote>")
            continue

        if stripped.startswith("- ") or stripped.startswith("* "):
            if not in_ul:
                html_lines.append(close_lists())
                html_lines.append("<ul>")
                in_ul = True
            html_lines.append(f"<li>{inline_format(stripped[2:])}</li>")
            continue

        m = re.match(r"^(\d+)\.\s+(.*)$", stripped)
        if m:
            if not in_ol:
                html_lines.append(close_lists())
                html_lines.append("<ol>")
                in_ol = True
            html_lines.append(f"<li>{inline_format(m.group(2))}</li>")
            continue

        html_lines.append(close_lists())
        html_lines.append(f"<p>{inline_format(stripped)}</p>")

    html_lines.append(close_lists())
    if in_table:
        html_lines.append("</tbody></table>")
    if in_code:
        html_lines.append("</code></pre>")

    return "\n".join(html_lines)

def inline_format(text: str) -> str:
    text = html.escape(text)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\*\*([^\*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\*([^\*]+)\*", r"<em>\1</em>", text)
    return text

def convert_file(md_path: Path, html_path: Path = None):
    md_content = md_path.read_text(encoding="utf-8")
    stem = md_path.stem
    lower = stem.lower()
    
    if "plan" in lower:
        report_type = "Plan"
        badge_class = "badge-plan"
    elif "analysis" in lower:
        report_type = "Analysis"
        badge_class = "badge-analysis"
    elif "test-run" in lower:
        report_type = "Test Run"
        badge_class = "badge-test-run"
    else:
        report_type = "Report"
        badge_class = "badge-analysis"

    badge_text = report_type.upper()
    first_h1 = re.search(r"^#\s+(.+)$", md_content, flags=re.MULTILINE)
    title = first_h1.group(1).strip() if first_h1 else stem.replace("_", " ").title()

    body_html = parse_markdown(md_content)
    full_html = HTML_TEMPLATE.format(
        title=title,
        badge_class=badge_class,
        badge_text=badge_text,
        report_type=report_type,
        generated_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        body_html=body_html,
    )

    if html_path is None:
        html_path = md_path.parent.parent / "html" / f"{stem}.html"

    html_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.write_text(full_html, encoding="utf-8")
    print(f"Generated HTML report: {html_path}")

def log_memory(stage: str, agent: str, topic: str, summary: str):
    stage = stage.lower()
    if stage not in VALID_STAGES:
        raise ValueError(f"Invalid stage '{stage}'. Must be one of: {', '.join(VALID_STAGES)}")

    today = datetime.now().strftime("%Y-%m-%d")
    clean_topic = topic.strip().lower().replace(" ", "-").replace("_", "-")
    filename = f"{today}_{stage}_{clean_topic}.md"

    root_dir = Path(__file__).resolve().parent.parent
    memory_dir = root_dir / ".ai" / "memory"
    memory_dir.mkdir(parents=True, exist_ok=True)

    file_path = memory_dir / filename
    rel_path = f".ai/memory/{filename}"

    if not file_path.exists():
        file_path.write_text(f"# {stage.capitalize()}: {topic.replace('-', ' ').title()}\n\n- **Date:** {today}\n- **Agent:** {agent}\n- **Summary:** {summary}\n", encoding="utf-8")

    index_file = root_dir / ".ai" / "memory" / "INDEX.md"
    if not index_file.exists():
        index_file.write_text("# Local Memory Index\n\n| Date | Stage | Agent | File | Summary |\n| :--- | :--- | :--- | :--- | :--- |\n", encoding="utf-8")

    with open(index_file, "a", encoding="utf-8") as f:
        f.write(f"| {today} | {stage} | {agent} | {rel_path} | {summary} |\n")

    print(f"Logged memory artifact: {rel_path}")
    print(f"Updated index: .ai/memory/INDEX.md")

def verify_setup():
    root = Path(__file__).resolve().parent.parent
    print(f"=== Verifying 6-File AI Monorepo Architecture ===\n")
    
    core_files = [
        "GEMINI.md",
        ".gitignore",
        ".ai/PROJECT_CONTEXT.md",
        ".ai/TEMPLATES.md",
        ".ai/report_tool.py",
        ".ai/memory/INDEX.md",
        ".ai/agents/discovery-planner.md",
        ".ai/agents/fullstack-engineer.md",
        ".ai/agents/quality-guardian.md",
    ]
    
    passed = 0
    for cf in core_files:
        p = root / cf
        if p.is_file():
            print(f"  [PASS] {cf} exists")
            passed += 1
        else:
            print(f"  [FAIL] {cf} is missing!")

    # Check gitignore
    res = subprocess.run(["git", "check-ignore", "-v", ".ai/memory/test.md", ".ai/reports/test.md"], cwd=root, capture_output=True, text=True)
    if res.returncode == 0 and ".ai/memory/" in res.stdout and ".ai/reports/" in res.stdout:
        print("  [PASS] GitIgnore excludes .ai/memory/ & .ai/reports/")
        passed += 1
    else:
        print(f"  [FAIL] GitIgnore check failed: {res.stdout}")

    total_checks = len(core_files) + 1
    print(f"\nResult: {passed}/{total_checks} checks passed.")
    if passed == total_checks:
        print("AI setup is clean, compact, and fully configured.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Multi-Agent Report and Memory Tool")
    parser.add_argument("report", nargs="?", help="Optional path to markdown report to compile")
    parser.add_argument("--log", action="store_true", help="Log an entry to memory and INDEX.md")
    parser.add_argument("--stage", choices=VALID_STAGES, help="Stage name for memory logging")
    parser.add_argument("--agent", help="Agent name/model for memory logging")
    parser.add_argument("--topic", help="Topic for memory logging")
    parser.add_argument("--summary", help="Summary for memory logging")
    parser.add_argument("--verify", action="store_true", help="Verify AI setup files and gitignore")

    args = parser.parse_args()

    if args.verify:
        verify_setup()
    elif args.log:
        if not all([args.stage, args.agent, args.topic, args.summary]):
            print("Error: --log requires --stage, --agent, --topic, and --summary", file=sys.stderr)
            sys.exit(1)
        log_memory(args.stage, args.agent, args.topic, args.summary)
    elif args.report:
        p = Path(args.report)
        if p.is_file():
            convert_file(p)
        elif p.is_dir():
            for f in p.glob("*.md"):
                convert_file(f)
        else:
            print(f"File not found: {args.report}", file=sys.stderr)
            sys.exit(1)
    else:
        # Default: compile all reports in .ai/reports/md
        md_dir = Path(".ai/reports/md")
        if md_dir.exists():
            for f in md_dir.glob("*.md"):
                convert_file(f)
        else:
            print("Usage: python .ai/report_tool.py [path_to_report.md] | --log | --verify")
