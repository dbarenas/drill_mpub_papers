CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE articles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pmid TEXT UNIQUE,
    doi TEXT UNIQUE,
    title TEXT,
    journal TEXT,
    year INTEGER,
    article_type TEXT,
    pdf_path TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX ON articles (year);
CREATE INDEX ON articles (article_type);

CREATE TABLE extractions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    article_id UUID NOT NULL REFERENCES articles(id),
    schema_version TEXT,
    extractor_bundle_version TEXT,
    payload JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX ON extractions (article_id);
CREATE INDEX extractions_payload_gin ON extractions USING GIN (payload);

CREATE TABLE evidence_spans (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    extraction_id UUID NOT NULL REFERENCES extractions(id),
    field_path TEXT NOT NULL,
    value_json JSONB,
    evidence_section TEXT,
    evidence_page INTEGER,
    table_figure TEXT,
    verbatim_excerpt TEXT,
    locator TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX ON evidence_spans (extraction_id);
CREATE INDEX ON evidence_spans (field_path);
CREATE INDEX evidence_spans_value_json_gin ON evidence_spans USING GIN (value_json);


CREATE TABLE outcomes_survival (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    extraction_id UUID NOT NULL REFERENCES extractions(id),
    endpoint TEXT,
    group_a TEXT,
    group_b TEXT,
    median_a_months NUMERIC,
    median_b_months NUMERIC,
    hr NUMERIC,
    hr_ci_low NUMERIC,
    hr_ci_high NUMERIC,
    p_value NUMERIC,
    effect_direction TEXT,
    evidence_section TEXT,
    evidence_page INTEGER,
    table_figure TEXT,
    verbatim_excerpt TEXT
);

CREATE INDEX ON outcomes_survival (extraction_id);
CREATE INDEX ON outcomes_survival (endpoint);
