use pyo3::prelude::*;

#[pyfunction]
fn ping() -> PyResult<String> {
    Ok("Rust Scalp Engine Active".to_string())
}

#[pymodule]
fn rust_scalp_engine(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(ping, m)?)?;
    Ok(())
}
