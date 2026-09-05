use pyo3::prelude::*;

mod execution;
mod rate_limiter;

#[pyfunction]
fn rust_engine_status() -> PyResult<String> {
    Ok("Rust Execution Engine: Active".to_string())
}

#[pymodule]
fn crypto_rust_engine(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(rust_engine_status, m)?)?;
    Ok(())
}
