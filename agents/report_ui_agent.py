#!/usr/bin/env python3
"""
Report UI Agent — VIF Trading System
Converts raw JSON data into aesthetic, human-readable Markdown reports.
"""
import json
import sys
from pathlib import Path
from datetime import datetime


class ReportUIAgent:
    def __init__(self):
        self.raw_dir = Path("reports/raw")
        self.daily_dir = Path("reports/daily")
        self.options_dir = Path("reports/options")
        self._ensure_dirs()

    def _ensure_dirs(self):
        for d in [self.raw_dir, self.daily_dir, self.options_dir]:
            d.mkdir(parents=True, exist_ok=True)

    def convert_json_to_markdown(self, json_file: str | Path) -> str:
        """Convert raw JSON report to formatted Markdown."""
        json_path = Path(json_file) if isinstance(json_file, str) else json_file

        if not json_path.exists():
            return f"Error: {json_path} not found"

        try:
            with open(json_path) as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            return f"Error parsing JSON: {e}"

        title = data.get("title", "Analysis Report")
        timestamp = data.get("timestamp", datetime.now().isoformat())

        md = f"# {title}\n"
        md += f"**Generated:** {timestamp}\n\n"

        if "summary" in data:
            md += "## Summary\n"
            md += f"{data['summary']}\n\n"

        if "signals" in data and isinstance(data["signals"], dict):
            md += "## Signals\n"
            for key, value in data["signals"].items():
                md += f"- **{key}:** {value}\n"
            md += "\n"

        if "recommendations" in data and isinstance(data["recommendations"], list):
            md += "## Recommendations\n"
            for i, rec in enumerate(data["recommendations"], 1):
                if isinstance(rec, dict):
                    md += f"{i}. {rec.get('ticker', 'Unknown')} - {rec.get('action', 'Hold')}\n"
                    if "reason" in rec:
                        md += f"   - {rec['reason']}\n"
                else:
                    md += f"{i}. {rec}\n"
            md += "\n"

        if "technical_levels" in data and isinstance(data["technical_levels"], dict):
            md += "## Technical Levels\n"
            for key, value in data["technical_levels"].items():
                md += f"- **{key}:** {value}\n"
            md += "\n"

        if "catalysts" in data and isinstance(data["catalysts"], list):
            md += "## Catalysts\n"
            for catalyst in data["catalysts"]:
                if isinstance(catalyst, dict):
                    md += f"- {catalyst.get('event', 'Event')}: {catalyst.get('date', 'TBD')}\n"
                else:
                    md += f"- {catalyst}\n"
            md += "\n"

        if "metadata" in data and isinstance(data["metadata"], dict):
            md += "## Metadata\n"
            for key, value in data["metadata"].items():
                if key != "timestamp":
                    md += f"- {key}: {value}\n"

        return md

    def save_report(self, markdown: str, output_file: str | Path) -> bool:
        """Save markdown report to file."""
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(output_path, "w") as f:
                f.write(markdown)
            print(f"[UI] Report saved: {output_path}")
            return True
        except Exception as e:
            print(f"[UI] Error saving report: {e}")
            return False

    def process_all_reports(self) -> int:
        """Process all JSON files in reports/raw and save as Markdown."""
        if not self.raw_dir.exists():
            print(f"[UI] No raw reports directory at {self.raw_dir}")
            return 0

        json_files = list(self.raw_dir.glob("*.json"))
        if not json_files:
            print(f"[UI] No JSON reports found in {self.raw_dir}")
            return 0

        count = 0
        for json_file in json_files:
            print(f"[UI] Processing {json_file.name}...")
            md = self.convert_json_to_markdown(json_file)

            output_name = json_file.stem + ".md"
            output_path = self.daily_dir / output_name
            if self.save_report(md, output_path):
                count += 1

        print(f"[UI] Processed {count} reports")
        return count


if __name__ == "__main__":
    ui = ReportUIAgent()

    if len(sys.argv) > 1:
        json_file = sys.argv[1]
        md = ui.convert_json_to_markdown(json_file)
        output_file = Path(json_file).stem + ".md"
        ui.save_report(md, output_file)
    else:
        ui.process_all_reports()
