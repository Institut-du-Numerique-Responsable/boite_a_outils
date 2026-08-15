import re, json, sys

DUMP = "/Users/ggallon/projects/sustainableit-tools/BDD/academicorser382_mysql_db (1).sql"
src = open(DUMP, encoding="utf-8", errors="replace").read()

def schema(table):
    m = re.search(r"CREATE TABLE `%s` \((.*?)\n\) ENGINE" % re.escape(table), src, re.S)
    return [c.group(1) for c in re.finditer(r"^\s*`([^`]+)`\s", m.group(1), re.M)]

def unescape(s):
    out, i = [], 0
    mapping = {"n": "\n", "t": "\t", "r": "\r", "0": "\0", "\\": "\\", "'": "'", '"': '"', "Z": "\x1a", "b": "\b"}
    while i < len(s):
        c = s[i]
        if c == "\\" and i + 1 < len(s):
            out.append(mapping.get(s[i + 1], s[i + 1])); i += 2
        else:
            out.append(c); i += 1
    return "".join(out)

def parse_values(blob):
    """Parse `(a,b),(c,d)` respecting quotes and escapes."""
    rows, cur, val = [], [], []
    i, n = 0, len(blob)
    in_str = False
    depth = 0
    while i < n:
        c = blob[i]
        if in_str:
            if c == "\\":
                val.append(c); val.append(blob[i + 1]); i += 2; continue
            if c == "'":
                in_str = False; i += 1; continue
            val.append(c); i += 1; continue
        if c == "'":
            in_str = True; val.append("\x00STR"); i += 1; continue
        if c == "(":
            depth += 1
            if depth == 1:
                cur, val = [], []
                i += 1; continue
        if c == ")" and depth == 1:
            depth -= 1
            cur.append("".join(val)); rows.append(cur); val = []
            i += 1; continue
        if c == "," and depth == 1:
            cur.append("".join(val)); val = []
            i += 1; continue
        if depth == 1:
            val.append(c)
        i += 1
    out = []
    for r in rows:
        rr = []
        for v in r:
            if "\x00STR" in v:
                rr.append(unescape(v.replace("\x00STR", "").strip() if v.strip() == "\x00STR" else v.split("\x00STR", 1)[1]))
            else:
                v = v.strip()
                rr.append(None if v.upper() == "NULL" else v)
        out.append(rr)
    return out

def table(name):
    cols = schema(name)
    rows = []
    for m in re.finditer(r"INSERT INTO `%s` (?:\([^)]*\) )?VALUES\s*(.*?);\s*\n" % re.escape(name), src, re.S):
        rows += parse_values(m.group(1))
    return [dict(zip(cols, r)) for r in rows]

data = {}
for t in ["tools_ifs_categorie", "tools_ifs_outils", "tools_ifs_outils_meta",
          "tools_ifs_en_categorie", "tools_ifs_en_outils", "tools_ifs_en_outils_meta"]:
    data[t] = table(t)
    print(f"{t}: {len(data[t])} rows")

json.dump(data, open("db_dump.json", "w"), ensure_ascii=False, indent=1)
