"""Assemble the single-file app: dist/network-pulse.html (open it in a browser)."""
import os, json
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def read(*p):
    with open(os.path.join(root, *p), encoding="utf-8") as f: return f.read()
def pick(real, sample):
    return read("data", real) if os.path.exists(os.path.join(root, "data", real)) else read("data", sample)
tpl = read("src", "app_template.html")
contacts = pick("contacts.json", "contacts.sample.json").replace("</", "<\\/")
emails = pick("emails.json", "emails.sample.json").replace("</", "<\\/")
body = tpl.replace("__DATA__", contacts).replace("__EMAILS__", emails)
doc = ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
       '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">'
       '<style>:root{color-scheme:light}body{margin:0;font:14px system-ui,sans-serif}img{max-width:100%}</style>'
       '</head><body>' + body + '</body></html>')
os.makedirs(os.path.join(root, "dist"), exist_ok=True)
with open(os.path.join(root, "dist", "network-pulse.html"), "w", encoding="utf-8") as f: f.write(doc)
print("wrote dist/network-pulse.html with", len(json.loads(pick("contacts.json", "contacts.sample.json"))), "contacts")
