-- V1 Migration v3 — handles all edge cases
CREATE TABLE IF NOT EXISTS sources (id SERIAL PRIMARY KEY, name VARCHAR(200) NOT NULL, url VARCHAR(2048), type VARCHAR(20) DEFAULT 'rss', status VARCHAR(20) DEFAULT 'active', failure_count INTEGER DEFAULT 0, quarantine_until TIMESTAMP, last_success_at TIMESTAMP, credibility REAL DEFAULT 0.5, created_at TIMESTAMP DEFAULT NOW());
CREATE TABLE IF NOT EXISTS entities (id SERIAL PRIMARY KEY, name VARCHAR(200) UNIQUE NOT NULL, type VARCHAR(30) DEFAULT 'Organization', aliases JSONB DEFAULT '[]', extra JSONB DEFAULT '{}', created_at TIMESTAMP DEFAULT NOW());
CREATE TABLE IF NOT EXISTS categories (id SERIAL PRIMARY KEY, name VARCHAR(100) UNIQUE NOT NULL, parent_id INTEGER REFERENCES categories(id));
CREATE TABLE IF NOT EXISTS tags (id SERIAL PRIMARY KEY, name VARCHAR(100) UNIQUE NOT NULL);
CREATE TABLE IF NOT EXISTS events (id SERIAL PRIMARY KEY, title VARCHAR(500) NOT NULL, slug VARCHAR(200) UNIQUE, summary TEXT, started_at TIMESTAMP, last_updated_at TIMESTAMP, article_count INTEGER DEFAULT 0, impact_level VARCHAR(10) DEFAULT 'MEDIUM', category_id INTEGER REFERENCES categories(id), is_active BOOLEAN DEFAULT true, status VARCHAR(20) DEFAULT 'active', created_at TIMESTAMP DEFAULT NOW());
CREATE TABLE IF NOT EXISTS insights (id SERIAL PRIMARY KEY, event_id INTEGER UNIQUE REFERENCES events(id), generated_at TIMESTAMP DEFAULT NOW(), model VARCHAR(50), summary TEXT, impact_analysis TEXT, drivers TEXT, sentiment VARCHAR(20), confidence REAL, raw_output TEXT);
CREATE TABLE IF NOT EXISTS article_entity (article_id INTEGER REFERENCES articles(id) ON DELETE CASCADE, entity_id INTEGER REFERENCES entities(id) ON DELETE CASCADE, relevance_score REAL DEFAULT 1.0, PRIMARY KEY (article_id, entity_id));
CREATE TABLE IF NOT EXISTS event_article (event_id INTEGER REFERENCES events(id) ON DELETE CASCADE, article_id INTEGER REFERENCES articles(id) ON DELETE CASCADE UNIQUE, PRIMARY KEY (event_id, article_id));
CREATE TABLE IF NOT EXISTS event_entity (event_id INTEGER REFERENCES events(id) ON DELETE CASCADE, entity_id INTEGER REFERENCES entities(id) ON DELETE CASCADE, importance REAL DEFAULT 1.0, PRIMARY KEY (event_id, entity_id));
CREATE TABLE IF NOT EXISTS article_category (article_id INTEGER REFERENCES articles(id) ON DELETE CASCADE, category_id INTEGER REFERENCES categories(id) ON DELETE CASCADE, PRIMARY KEY (article_id, category_id));
CREATE TABLE IF NOT EXISTS article_tag (article_id INTEGER REFERENCES articles(id) ON DELETE CASCADE, tag_id INTEGER REFERENCES tags(id) ON DELETE CASCADE, PRIMARY KEY (article_id, tag_id));

ALTER TABLE articles ADD COLUMN IF NOT EXISTS source_id INTEGER REFERENCES sources(id);
ALTER TABLE articles ADD COLUMN IF NOT EXISTS importance_level VARCHAR(20) DEFAULT 'medium';
ALTER TABLE articles ADD COLUMN IF NOT EXISTS fetched_at TIMESTAMP DEFAULT NOW();
ALTER TABLE articles ADD COLUMN IF NOT EXISTS language VARCHAR(5) DEFAULT 'en';
ALTER TABLE articles ADD COLUMN IF NOT EXISTS status VARCHAR(20) DEFAULT 'raw';
ALTER TABLE articles ADD COLUMN IF NOT EXISTS is_duplicate BOOLEAN DEFAULT false;

-- Sources
INSERT INTO sources (name, url, type) SELECT DISTINCT source_name, COALESCE(source_domain,''), 'rss' FROM articles WHERE source_name IS NOT NULL AND source_name NOT IN (SELECT name FROM sources) ON CONFLICT DO NOTHING;
UPDATE articles a SET source_id = s.id FROM sources s WHERE a.source_name = s.name AND a.source_id IS NULL;

-- Entities (only process valid JSON objects)
INSERT INTO entities (name, type)
SELECT DISTINCT value, CASE WHEN key='companies' THEN 'Company' WHEN key='persons' THEN 'Person' WHEN key='countries' THEN 'Country' ELSE 'Other' END
FROM articles, jsonb_each_text(articles.entities::text::jsonb)
WHERE articles.entities IS NOT NULL AND jsonb_typeof(articles.entities::text::jsonb) = 'object'
ON CONFLICT (name) DO NOTHING;

INSERT INTO article_entity (article_id, entity_id)
SELECT DISTINCT a.id, e.id FROM articles a, jsonb_each_text(a.entities::text::jsonb) kv, jsonb_array_elements_text(kv.value::jsonb) elem, entities e
WHERE a.entities IS NOT NULL AND jsonb_typeof(a.entities::text::jsonb) = 'object' AND e.name = elem
ON CONFLICT DO NOTHING;

-- Tags
INSERT INTO tags (name) SELECT DISTINCT value FROM articles, jsonb_array_elements_text(articles.tags::text::jsonb) WHERE articles.tags IS NOT NULL AND jsonb_typeof(articles.tags::text::jsonb) = 'array' ON CONFLICT (name) DO NOTHING;
INSERT INTO article_tag (article_id, tag_id) SELECT DISTINCT a.id, t.id FROM articles a, jsonb_array_elements_text(a.tags::text::jsonb) elem, tags t WHERE a.tags IS NOT NULL AND jsonb_typeof(a.tags::text::jsonb) = 'array' AND t.name = elem ON CONFLICT DO NOTHING;

-- Categories
INSERT INTO categories (name) SELECT DISTINCT category FROM articles WHERE category IS NOT NULL ON CONFLICT (name) DO NOTHING;
INSERT INTO article_category (article_id, category_id) SELECT a.id, c.id FROM articles a JOIN categories c ON a.category = c.name WHERE a.category IS NOT NULL ON CONFLICT DO NOTHING;

-- Indexes
CREATE INDEX IF NOT EXISTS idx_sources_status ON sources(status);
CREATE INDEX IF NOT EXISTS idx_articles_pub ON articles(published_at DESC, tier);
CREATE INDEX IF NOT EXISTS idx_articles_src ON articles(source_id);
CREATE INDEX IF NOT EXISTS idx_entities_aliases ON entities USING gin(aliases);
CREATE INDEX IF NOT EXISTS idx_events_started ON events(started_at DESC);
