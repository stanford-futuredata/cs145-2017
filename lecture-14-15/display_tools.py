from IPython.core.display import display_html, HTML

def to_html_table(res, style=None):
  html = '<table' + (' style="' + style + '"' if style else '') + '><tr><th>'
  html += '</th><th>'.join(res.keys) + '</th></tr><tr><td>'
  html += '</td></tr><tr><td>'.join(['</td><td>'.join([str(cell) for cell in row]) for row in list(res)])
  return html + '</tr></table>'

def side_by_side(l, r):
  s = "display: inline-block;"
  html = to_html_table(l, style=s) + ' ' + to_html_table(r, style=s)
  display_html(HTML(data=html))
