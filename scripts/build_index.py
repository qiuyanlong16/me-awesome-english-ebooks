"""Index Builder: generate the main index.html from all issue metadata."""

import os
import json


def build_index(issues_dir, output_path):
    """
    Scan all issue directories and generate index.html.

    Args:
        issues_dir: path to docs/issues/
        output_path: path to write index.html
    """
    # Collect metadata for all issues
    issues = []
    if os.path.exists(issues_dir):
        for name in sorted(os.listdir(issues_dir)):
            meta_path = os.path.join(issues_dir, name, 'meta.json')
            if os.path.exists(meta_path):
                with open(meta_path, 'r', encoding='utf-8') as f:
                    meta = json.load(f)
                meta['issue_dir'] = name
                issues.append(meta)

    # Sort by date descending
    issues.sort(key=lambda x: x.get('date', ''), reverse=True)

    # Generate HTML
    template_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'template', 'index.html')
    with open(template_path, 'r', encoding='utf-8') as f:
        template = f.read()

    # Build issue list HTML
    issues_html = ''
    for issue in issues:
        date = issue.get('date', 'unknown')
        total_days = issue.get('total_days', 0)
        last_read = issue.get('last_read_day', 1)

        # Generate day links
        day_links = ''
        for d in range(1, total_days + 1):
            cls = ''
            if d == last_read:
                cls = ' style="background:#fff3cd;font-weight:bold;"'
            elif d < last_read:
                cls = ' style="color:#999;"'
            day_links += f'<a href="issues/{date}/day{d}.html"{cls}>Day {d}</a> '

        progress_pct = int((last_read / total_days) * 100) if total_days else 0

        issues_html += f'''
<div class="issue-card">
  <h3>Issue: {date}</h3>
  <div class="progress-bar">
    <div class="progress-fill" style="width:{progress_pct}%"></div>
  </div>
  <p>{last_read} / {total_days} days read</p>
  <div class="day-links">{day_links}</div>
</div>
'''

    html = template.replace('{{ISSUES}}', issues_html)

    # Write index
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"Index generated: {len(issues)} issues")
