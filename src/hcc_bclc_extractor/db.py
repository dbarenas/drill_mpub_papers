import os
import json
import pathlib
import logging
from contextlib import contextmanager
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import Engine
from .schema import ExtractionOutput

# Configure logging
logger = logging.getLogger(__name__)

# This module maintains a global engine to allow for connection pooling across
# Lambda invocations.
_engine: Engine | None = None

def get_engine() -> Engine:
    """
    Returns a SQLAlchemy engine, creating one if it doesn't exist.
    This function is designed to be Lambda-friendly by reusing the engine
    across invocations.
    """
    global _engine
    if _engine is None:
        db_url = os.getenv("DATABASE_URL")
        if not db_url:
            logger.error("DATABASE_URL environment variable is not set.")
            raise ValueError("DATABASE_URL environment variable is not set.")

        logger.info("Creating new SQLAlchemy engine...")
        _engine = create_engine(db_url)
    return _engine

@contextmanager
def get_db_session():
    """
    Provides a transactional scope around a series of operations.
    """
    engine = get_engine()
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        yield session
        session.commit()
    except Exception as e:
        logger.error("Database session failed, rolling back. Error: %s", e, exc_info=True)
        session.rollback()
        raise
    finally:
        session.close()

def test_connection() -> bool:
    """
    Tests the connection to the database.
    """
    try:
        with get_db_session() as session:
            session.execute(text("SELECT 1"))
        logger.info("Database connection successful.")
        return True
    except Exception as e:
        logger.error("Database connection failed: %s", e)
        return False

def initialize_schema():
    """
    Reads the schema.sql file and executes it to initialize the database schema.
    """
    sql_file_path = pathlib.Path(__file__).parent / "sql" / "schema.sql"
    if not sql_file_path.is_file():
        raise FileNotFoundError(f"Schema file not found at: {sql_file_path}")

    with open(sql_file_path, "r") as f:
        schema_sql = f.read()

    try:
        with get_db_session() as session:
            session.execute(text(schema_sql))
        logger.info("Database schema initialized successfully.")
    except Exception as e:
        logger.error("Failed to initialize database schema: %s", e)
        raise

def insert_extraction(
    extraction_output: ExtractionOutput,
    pdf_path: str,
    article_type: str,
    schema_version: str = "1.0",
    extractor_bundle_version: str = "0.1.0"
) -> str:
    """
    Inserts a full extraction payload into the database, normalizing the data
    into the appropriate tables.
    """
    with get_db_session() as session:
        meta = extraction_output.study_metadata
        article_id = None

        find_clauses = []
        find_params = {}
        if meta.pmid:
            find_clauses.append("pmid = :pmid")
            find_params["pmid"] = meta.pmid
        if meta.doi:
            find_clauses.append("doi = :doi")
            find_params["doi"] = meta.doi

        if find_clauses:
            find_sql = text(f"SELECT id FROM articles WHERE {' OR '.join(find_clauses)}")
            result = session.execute(find_sql, find_params)
            article_id = result.scalar_one_or_none()

        if article_id:
            logger.info("Found existing article with ID: %s. Updating.", article_id)
            update_sql = text("""
                UPDATE articles
                SET pmid = :pmid, doi = :doi, title = :title, journal = :journal, year = :year, updated_at = NOW()
                WHERE id = :id
            """)
            session.execute(update_sql, {
                "id": article_id, "pmid": meta.pmid, "doi": meta.doi, "title": meta.title,
                "journal": meta.journal, "year": meta.year
            })
        else:
            logger.info("No existing article found. Inserting new one.")
            insert_sql = text("""
                INSERT INTO articles (pmid, doi, title, journal, year, article_type, pdf_path)
                VALUES (:pmid, :doi, :title, :journal, :year, :article_type, :pdf_path)
                RETURNING id;
            """)
            result = session.execute(insert_sql, {
                "pmid": meta.pmid, "doi": meta.doi, "title": meta.title, "journal": meta.journal,
                "year": meta.year, "article_type": article_type, "pdf_path": pdf_path
            })
            article_id = result.scalar_one()

        extraction_sql = text("""
            INSERT INTO extractions (article_id, schema_version, extractor_bundle_version, payload)
            VALUES (:article_id, :schema_version, :extractor_bundle_version, :payload)
            RETURNING id;
        """)
        payload_json = extraction_output.model_dump_json()
        result = session.execute(extraction_sql, {
            "article_id": article_id,
            "schema_version": schema_version,
            "extractor_bundle_version": extractor_bundle_version,
            "payload": payload_json
        })
        extraction_id = result.scalar_one()

        _insert_evidence_spans(session, extraction_id, extraction_output)
        _insert_outcomes_survival(session, extraction_id, extraction_output)

        logger.info("Successfully inserted extraction for article %s with extraction ID %s.", article_id, extraction_id)
        return extraction_id


def _insert_evidence_spans(session, extraction_id: str, extraction_output: ExtractionOutput):
    """
    Inserts evidence spans from the new `evidence_spans` list into the database.
    """
    span_sql = text("""
        INSERT INTO evidence_spans (
            extraction_id, field_path, value_json, evidence_section,
            evidence_page, table_figure, verbatim_excerpt, locator
        )
        VALUES (
            :extraction_id, :field_path, :value_json, :evidence_section,
            :evidence_page, :table_figure, :verbatim_excerpt, :locator
        );
    """)

    for span in extraction_output.evidence_spans:
        session.execute(span_sql, {
            "extraction_id": extraction_id,
            "field_path": span.field_path,
            "value_json": span.value_json,
            "evidence_section": span.evidence_section,
            "evidence_page": span.evidence_page,
            "table_figure": span.table_figure,
            "verbatim_excerpt": span.verbatim_excerpt,
            "locator": span.locator
        })

def _parse_numeric_value(value: str) -> float | None:
    """Helper to safely parse a numeric value from a string."""
    if not value:
        return None
    try:
        return float(str(value).strip().split()[0])
    except (ValueError, IndexError):
        return None

def _parse_p_value(p_str: str) -> float | None:
    """Helper to safely parse a p-value string like 'p<0.001'."""
    if not p_str:
        return None
    try:
        p_val_str = str(p_str).lower().replace("p", "").replace("<", "").replace("=", "").strip()
        return float(p_val_str)
    except (ValueError, IndexError):
        return None

def _parse_ci_value(ci_str: str) -> tuple[float | None, float | None]:
    """Helper to safely parse a CI string like '0.79-1.06'."""
    if not ci_str:
        return None, None
    try:
        low, high = map(float, str(ci_str).split('-'))
        return low, high
    except (ValueError, IndexError):
        return None, None

def _insert_outcomes_survival(session, extraction_id: str, extraction_output: ExtractionOutput):
    """
    Populates the outcomes_survival table from the extraction output,
    correctly handling comparative data.
    """
    outcome_sql = text("""
        INSERT INTO outcomes_survival (
            extraction_id, endpoint, group_a, group_b, median_a_months, median_b_months,
            p_value, hr, hr_ci_low, hr_ci_high, evidence_section, evidence_page, table_figure, verbatim_excerpt
        )
        VALUES (
            :extraction_id, :endpoint, :group_a, :group_b, :median_a_months, :median_b_months,
            :p_value, :hr, :hr_ci_low, :hr_ci_high, :evidence_section, :evidence_page, :table_figure, :verbatim_excerpt
        );
    """)

    comparator_name = extraction_output.study_metadata.comparator
    comparator_arm = None
    if comparator_name:
        for exp in extraction_output.experiments:
            if exp.arm_name == comparator_name:
                comparator_arm = exp
                break

    for exp in extraction_output.experiments:
        # Skip the comparator arm itself
        if exp.arm_name == comparator_name:
            continue

        group_a_name = exp.arm_name or "N/A"

        results_map = {"OS": exp.results.os, "PFS": exp.results.pfs, "TTP": exp.results.ttp}

        for endpoint, data_a in results_map.items():
            data_b = None
            if comparator_arm:
                if endpoint == "OS": data_b = comparator_arm.results.os
                elif endpoint == "PFS": data_b = comparator_arm.results.pfs
                elif endpoint == "TTP": data_b = comparator_arm.results.ttp

            median_a = _parse_numeric_value(data_a.value) if data_a else None
            median_b = _parse_numeric_value(data_b.value) if data_b else None
            p_value = _parse_p_value(data_a.p_value) if data_a else None
            hr_ci_low, hr_ci_high = _parse_ci_value(data_a.hr_ci) if data_a else (None, None)

            # Insert a row only if there's meaningful data to compare
            if median_a is not None:
                session.execute(outcome_sql, {
                    "extraction_id": extraction_id,
                    "endpoint": endpoint,
                    "group_a": group_a_name,
                    "group_b": comparator_name,
                    "median_a_months": median_a,
                    "median_b_months": median_b,
                    "p_value": p_value,
                    "hr": data_a.hr if data_a else None,
                    "hr_ci_low": hr_ci_low,
                    "hr_ci_high": hr_ci_high,
                    "evidence_section": data_a.evidence_section if data_a else None,
                    "evidence_page": data_a.evidence_page if data_a else None,
                    "table_figure": data_a.table_figure if data_a else None,
                    "verbatim_excerpt": data_a.verbatim_excerpt if data_a else None,
                })
