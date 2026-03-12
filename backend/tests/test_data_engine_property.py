import pytest
import polars as pl
from hypothesis import given, settings, HealthCheck, strategies as st
from engines.data_engine import DataEngine
import os
import tempfile

# Use explicit strategy functions to avoid any potential shadowing
text_strat = st.text
list_strat = st.lists
int_strat = st.integers
float_strat = st.floats
sampled_strat = st.sampled_from
composite_strat = st.composite

@composite_strat
def dataframe_strategy(draw):
    column_names = draw(list_strat(text_strat(alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd")), min_size=1, max_size=10), min_size=1, max_size=5, unique=True))
    num_rows = draw(int_strat(min_value=1, max_value=20))
    
    data = {}
    for col in column_names:
        col_type = draw(sampled_strat(["int", "float", "str"]))
        if col_type == "int":
            data[col] = draw(list_strat(int_strat(min_value=-1000, max_value=1000), min_size=num_rows, max_size=num_rows))
        elif col_type == "float":
            data[col] = draw(list_strat(float_strat(allow_nan=False, allow_infinity=False), min_size=num_rows, max_size=num_rows))
        else:
            # Avoid quotes and commas in row values for this basic property test to avoid complex CSV escaping bugs
            data[col] = draw(list_strat(text_strat(alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd", "Zs")), min_size=1, max_size=20), min_size=num_rows, max_size=num_rows))
            
    return pl.DataFrame(data)

@pytest.fixture
def engine():
    return DataEngine()

@settings(suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
@given(df=dataframe_strategy())
def test_load_data_robustness(engine, df):
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tmp:
        df.write_csv(tmp.name)
        tmp_path = tmp.name

    try:
        success = engine.load_data(tmp_path)
        assert success is True
        assert engine.df is not None
        
        loaded_cols = engine.metadata["columns"]
        for col in df.columns:
            assert col in loaded_cols
            
        summary = engine.get_summary()
        assert summary["status"] == "loaded"
        assert summary["row_count"] == len(df)
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

def test_load_non_existent_file(engine):
    success = engine.load_data("non_existent_file_xyz.csv")
    assert success is False

def test_execute_query_without_data(engine):
    result = engine.execute_query("SELECT * FROM table")
    assert result is None
