#[derive(Clone, Debug)]
pub enum Observation { Status, AuditEvent }

#[derive(Clone, Debug)]
pub enum Path { Identity, EmbedCore }

pub fn interpret_path(path: Path, payload: &str) -> String {
    match path {
        Path::Identity => payload.to_string(),
        Path::EmbedCore => format!("core::{payload}"),
    }
}
