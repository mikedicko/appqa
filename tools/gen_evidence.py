#!/usr/bin/env python3
"""Generate an annotated QA evidence HTML page from a JSON config.

Config format:
{
  "title": "...", "ticket": "notion url", "ref": "QA-2026-07-02",
  "summary": "one-paragraph plain description",
  "panels": [
    {"img": "file.png", "label": "Live app — Example screen", "w": 393, "h": 852,
     "annos": [
        {"type": "issue", "x":24,"y":600,"w":345,"h":60, "label":"Value renders wrong"},
        {"type": "target","x":24,"y":600,"w":345,"h":60, "label":"Expected per design"}
     ]}
  ],
  "notes": ["bullet", ...]
}
Annotation coords are in image CSS px (393x852 viewport = image px).
"""
import base64, json, sys, html

def svg_annos(annos, w, h):
    out = [f'<svg viewBox="0 0 {w} {h}" preserveAspectRatio="none" style="position:absolute;inset:0;width:100%;height:100%;pointer-events:none">']
    for a in annos:
        color = '#d0342c' if a['type'] == 'issue' else '#1d8a4a'
        x, y, bw, bh = a['x'], a['y'], a['w'], a['h']
        out.append(f'<rect x="{x}" y="{y}" width="{bw}" height="{bh}" fill="none" stroke="{color}" stroke-width="3" rx="4"/>')
        lbl = html.escape(a.get('label', ''))
        if lbl:
            # label above the box if room, else below; arrow from label to box edge
            above = (y > 46) and not a.get('labelBelow')
            ly = y - 14 if above else y + bh + 26
            ax1, ay1 = x + 8, (ly + 4 if above else ly - 16)
            ax2, ay2 = x + 8, (y if above else y + bh)
            tw = min(max(len(lbl) * 7.2 + 12, 60), w - 8)
            lx = min(max(x - 2, 4), w - tw - 4)
            out.append(f'<line x1="{ax1}" y1="{ay1}" x2="{ax2}" y2="{ay2}" stroke="{color}" stroke-width="2.5"/>')
            out.append(f'<polygon points="{ax2-5},{ay2-8 if above else ay2+8} {ax2+5},{ay2-8 if above else ay2+8} {ax2},{ay2}" fill="{color}"/>' if False else '')
            out.append(f'<rect x="{lx}" y="{ly-16}" width="{tw}" height="21" fill="{color}" rx="3"/>')
            out.append(f'<text x="{lx+6}" y="{ly-1}" font-family="-apple-system,Helvetica,sans-serif" font-size="12.5" font-weight="600" fill="#fff">{lbl}</text>')
    out.append('</svg>')
    return ''.join(out)

def main(cfg_path, out_path):
    cfg = json.load(open(cfg_path))
    panels_html = []
    for p in cfg['panels']:
        b64 = base64.b64encode(open(p['img'], 'rb').read()).decode()
        w, h = p.get('w', 393), p.get('h', 852)
        overlay = svg_annos(p.get('annos', []), w, h)
        panels_html.append(f'''<div style="flex:0 0 auto">
  <div style="font:600 13px/1.4 -apple-system,Helvetica,sans-serif;color:#3a3630;margin:0 0 8px 2px">{html.escape(p['label'])}</div>
  <div style="position:relative;width:{w}px;max-width:100%;border:1px solid #d8d2c6;border-radius:10px;overflow:hidden">
    <img src="data:image/png;base64,{b64}" style="display:block;width:100%;height:auto"/>
    {overlay}
  </div>
</div>''')
    notes = ''.join(f'<li style="margin:4px 0">{n}</li>' for n in cfg.get('notes', []))
    doc = f'''<meta charset="utf-8"><title>{html.escape(cfg["title"])}</title>
<div style="font-family:-apple-system,Helvetica,sans-serif;color:#2b2823;max-width:900px;margin:0 auto;padding:24px 16px">
<h1 style="font-size:20px;margin:0 0 4px">{html.escape(cfg['title'])}</h1>
<p style="font-size:13px;color:#6b6558;margin:0 0 14px">EZ Ref {html.escape(cfg.get('ref',''))} · <a href="{cfg.get('ticket','#')}" style="color:#0b6bcb">Notion ticket</a></p>
<p style="font-size:14.5px;line-height:1.55;margin:0 0 18px">{cfg['summary']}</p>
<div style="display:flex;gap:20px;flex-wrap:wrap;align-items:flex-start">{''.join(panels_html)}</div>
<div style="margin-top:18px;font-size:13.5px;line-height:1.5">
  <span style="display:inline-block;width:12px;height:12px;border:3px solid #d0342c;border-radius:3px;vertical-align:-1px"></span> issue&nbsp;&nbsp;
  <span style="display:inline-block;width:12px;height:12px;border:3px solid #1d8a4a;border-radius:3px;vertical-align:-1px"></span> expected / target
  <ul style="margin:10px 0 0;padding-left:20px;color:#3a3630">{notes}</ul>
</div>
</div>'''
    open(out_path, 'w').write(doc)
    print(f'wrote {out_path} ({len(doc)//1024} KB)')

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
