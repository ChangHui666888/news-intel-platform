"""migrate_data.py — V1 数据迁移 (entities/tags from JSON strings)"""
import psycopg2
import json

DSN = "postgresql://news_admin:news_pass@postgres:5432/news_intel"

conn = psycopg2.connect(DSN)
cur = conn.cursor()

# ── Sources ──
cur.execute("""
    DO $$ BEGIN
        ALTER TABLE sources ADD CONSTRAINT sources_name_key UNIQUE (name);
    EXCEPTION WHEN duplicate_table THEN NULL;
    END $$;
""")
cur.execute("""
    INSERT INTO sources (name, url, type)
    SELECT DISTINCT source_name, COALESCE(source_domain,''), 'rss'
    FROM articles WHERE source_name IS NOT NULL
      AND source_name NOT IN (SELECT name FROM sources)
""")
cur.execute("""
    UPDATE articles a SET source_id = s.id
    FROM sources s WHERE a.source_name = s.name AND a.source_id IS NULL
""")
print(f"sources: {cur.rowcount}")

# ── Entities ──
cur.execute("""
    DO $$ BEGIN
        ALTER TABLE entities ADD CONSTRAINT entities_name_key UNIQUE (name);
    EXCEPTION WHEN duplicate_table THEN NULL;
    END $$;
""")
conn.commit()
cur.execute("SELECT id, entities FROM articles WHERE entities IS NOT NULL")
rows = cur.fetchall()

entity_map = {}  # name → id
article_entities = []  # (article_id, entity_name)

for aid, raw in rows:
    if not raw or raw in ('null', '{}', '""', ''):
        continue
    try:
        # Handle double-encoded JSON: '"{\\"companies\\":[...]}"'
        if isinstance(raw, str):
            # Try parsing directly first
            data = json.loads(raw)
            if isinstance(data, str):
                data = json.loads(data)
            if not isinstance(data, dict):
                continue
        else:
            data = raw

        for key in ('companies', 'persons', 'countries'):
            items = data.get(key, [])
            if isinstance(items, list):
                for name in items:
                    if name and isinstance(name, str):
                        article_entities.append((aid, name, key))
                        if name not in entity_map:
                            etype = {'companies': 'Company', 'persons': 'Person', 'countries': 'Country'}.get(key, 'Other')
                            entity_map[name] = etype
    except (json.JSONDecodeError, TypeError, AttributeError):
        continue

print(f"entities parsed: {len(entity_map)} unique, {len(article_entities)} links")

# Insert entities
for name, etype in entity_map.items():
    cur.execute("INSERT INTO entities (name, type) VALUES (%s, %s) ON CONFLICT (name) DO NOTHING", (name, etype))

# Get entity IDs
cur.execute("SELECT id, name FROM entities")
eid_map = {name: eid for eid, name in cur.fetchall()}

# Insert article_entity links
for aid, name, key in article_entities:
    eid = eid_map.get(name)
    if eid:
        cur.execute("INSERT INTO article_entity (article_id, entity_id) VALUES (%s, %s) ON CONFLICT DO NOTHING", (aid, eid))

print(f"article_entity inserted")

# ── Tags ──
cur.execute("SELECT id, tags FROM articles WHERE tags IS NOT NULL")
tag_map = {}
article_tags = []

for aid, raw in cur.fetchall():
    if not raw or raw in ('null', '[]', '""', ''):
        continue
    try:
        if isinstance(raw, str):
            data = json.loads(raw)
            if isinstance(data, str):
                data = json.loads(data)
            if isinstance(data, list):
                for t in data:
                    if t and isinstance(t, str):
                        article_tags.append((aid, t))
                        tag_map[t] = True
        elif isinstance(raw, list):
            for t in raw:
                if t and isinstance(t, str):
                    article_tags.append((aid, t))
                    tag_map[t] = True
    except (json.JSONDecodeError, TypeError, AttributeError):
        continue

print(f"tags parsed: {len(tag_map)} unique, {len(article_tags)} links")

for name in tag_map:
    cur.execute("INSERT INTO tags (name) VALUES (%s) ON CONFLICT (name) DO NOTHING", (name,))

cur.execute("SELECT id, name FROM tags")
tid_map = {name: tid for tid, name in cur.fetchall()}

for aid, name in article_tags:
    tid = tid_map.get(name)
    if tid:
        cur.execute("INSERT INTO article_tag (article_id, tag_id) VALUES (%s, %s) ON CONFLICT DO NOTHING", (aid, tid))

# ── Categories ──
cur.execute("INSERT INTO categories (name) SELECT DISTINCT category FROM articles WHERE category IS NOT NULL ON CONFLICT (name) DO NOTHING")
cur.execute("SELECT id, name FROM categories")
cid_map = {name: cid for cid, name in cur.fetchall()}

cur.execute("SELECT id, category FROM articles WHERE category IS NOT NULL")
for aid, cat in cur.fetchall():
    cid = cid_map.get(cat)
    if cid:
        cur.execute("INSERT INTO article_category (article_id, category_id) VALUES (%s, %s) ON CONFLICT DO NOTHING", (aid, cid))

conn.commit()

# ── Final counts ──
cur.execute("""
    SELECT
        (SELECT COUNT(*) FROM sources) AS sources,
        (SELECT COUNT(*) FROM entities) AS entities,
        (SELECT COUNT(*) FROM tags) AS tags,
        (SELECT COUNT(*) FROM article_entity) AS art_ent,
        (SELECT COUNT(*) FROM article_tag) AS art_tag,
        (SELECT COUNT(*) FROM articles) AS articles
""")
print(f"Final: {dict(zip(['sources','entities','tags','art_ent','art_tag','articles'], cur.fetchone()))}")

cur.close()
conn.close()
print("Migration complete!")
