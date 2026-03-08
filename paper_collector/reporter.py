"""
Report generator for collected papers.
収集論文のレポート生成モジュール
"""

import os
import json
from datetime import datetime


def generate_text_report(papers, output_dir=None):
    """Generate a plain-text report of newly collected papers."""
    if not papers:
        return "No new papers found.\n"

    lines = []
    lines.append(f"=== Egypt Animal Cult Paper Report ===")
    lines.append(f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}")
    lines.append(f"Papers found: {len(papers)}")
    lines.append("=" * 50)
    lines.append("")

    for i, p in enumerate(papers, 1):
        lines.append(f"[{i}] {p.get('title', 'No title')}")
        if p.get("authors"):
            lines.append(f"    Authors: {p['authors']}")
        if p.get("published_date"):
            lines.append(f"    Published: {p['published_date']}")
        if p.get("doi"):
            lines.append(f"    DOI: https://doi.org/{p['doi']}")
        elif p.get("url"):
            lines.append(f"    URL: {p['url']}")
        if p.get("source"):
            lines.append(f"    Source: {p['source']}")
        if p.get("abstract"):
            abstract = p["abstract"][:300]
            if len(p["abstract"]) > 300:
                abstract += "..."
            lines.append(f"    Abstract: {abstract}")
        lines.append("")

    report = "\n".join(lines)

    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        filename = f"report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.txt"
        filepath = os.path.join(output_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(report)
        return filepath

    return report


def generate_json_report(papers, output_dir=None):
    """Generate a JSON report of newly collected papers."""
    data = {
        "generated_at": datetime.utcnow().isoformat(),
        "count": len(papers),
        "papers": papers,
    }

    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        filename = f"report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(output_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return filepath

    return json.dumps(data, ensure_ascii=False, indent=2)
