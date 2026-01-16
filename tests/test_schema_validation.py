from hcc_bclc_extractor.schema import ExtractionOutput

def test_schema_compiles():
    """Just tests that the schema can be imported and initialized."""
    assert ExtractionOutput is not None
