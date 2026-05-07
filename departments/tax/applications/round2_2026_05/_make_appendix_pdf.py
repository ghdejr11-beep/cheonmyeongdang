# -*- coding: utf-8 -*-
"""Convert grant_appendix_2026_05.md to PDF using reportlab + malgun.ttf."""
import os, re, sys
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Register Korean font
pdfmetrics.registerFont(TTFont('Malgun', 'C:/Windows/Fonts/malgun.ttf'))
pdfmetrics.registerFont(TTFont('MalgunBold', 'C:/Windows/Fonts/malgunbd.ttf'))

ROOT = r'C:\Users\hdh02\Desktop\cheonmyeongdang'
SRC = os.path.join(ROOT, 'docs', 'grant_appendix_2026_05.md')
DST = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'grant_appendix_2026_05.pdf')

with open(SRC, 'r', encoding='utf-8') as f:
    md = f.read()

doc = SimpleDocTemplate(DST, pagesize=A4,
                        leftMargin=2*cm, rightMargin=2*cm,
                        topMargin=2*cm, bottomMargin=2*cm)

styles = {
    'h1': ParagraphStyle('h1', fontName='MalgunBold', fontSize=16, leading=22, spaceAfter=12, textColor=colors.HexColor('#1a365d')),
    'h2': ParagraphStyle('h2', fontName='MalgunBold', fontSize=13, leading=18, spaceAfter=8, spaceBefore=12, textColor=colors.HexColor('#2c5282')),
    'h3': ParagraphStyle('h3', fontName='MalgunBold', fontSize=11, leading=15, spaceAfter=6, spaceBefore=8),
    'body': ParagraphStyle('body', fontName='Malgun', fontSize=9.5, leading=14, spaceAfter=4),
    'list': ParagraphStyle('list', fontName='Malgun', fontSize=9.5, leading=14, leftIndent=12, spaceAfter=2),
}

story = []
lines = md.split('\n')
i = 0
while i < len(lines):
    line = lines[i].rstrip()
    # Skip table lines processed below
    if line.startswith('| ') and i + 1 < len(lines) and lines[i+1].startswith('|') and '---' in lines[i+1]:
        # Parse table
        rows = []
        header = [c.strip() for c in line.strip('|').split('|')]
        rows.append(header)
        i += 2
        while i < len(lines) and lines[i].startswith('|'):
            cells = [c.strip() for c in lines[i].strip('|').split('|')]
            rows.append(cells)
            i += 1
        # Build Table with Paragraph cells for word wrap
        cell_style = ParagraphStyle('cell', fontName='Malgun', fontSize=8, leading=11)
        head_style = ParagraphStyle('head', fontName='MalgunBold', fontSize=8, leading=11, textColor=colors.white)
        wrapped = []
        for ri, r in enumerate(rows):
            wrapped.append([Paragraph(c.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'),
                                       head_style if ri == 0 else cell_style) for c in r])
        t = Table(wrapped, repeatRows=1)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5282')),
            ('GRID', (0, 0), (-1, -1), 0.4, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        story.append(t)
        story.append(Spacer(1, 8))
        continue
    if line.startswith('# '):
        story.append(Paragraph(line[2:], styles['h1']))
    elif line.startswith('## '):
        story.append(Paragraph(line[3:], styles['h2']))
    elif line.startswith('### '):
        story.append(Paragraph(line[4:], styles['h3']))
    elif line.startswith('---'):
        story.append(Spacer(1, 6))
    elif line.startswith('- ') or line.startswith('* '):
        text = line[2:].replace('**', '<b>', 1)
        if '**' in text:
            text = text.replace('**', '</b>', 1)
        story.append(Paragraph('• ' + text, styles['list']))
    elif line.strip():
        text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', line)
        text = re.sub(r'`(.+?)`', r'<font face="Malgun" color="#c53030">\1</font>', text)
        story.append(Paragraph(text, styles['body']))
    else:
        story.append(Spacer(1, 4))
    i += 1

doc.build(story)
print(f'OK: {DST}')
print(f'Size: {os.path.getsize(DST):,} bytes')
