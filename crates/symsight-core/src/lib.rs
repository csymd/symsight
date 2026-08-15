// Copyright (c) 2026, PalEm Dynamics LLC
// Licensed under the Apache License, Version 2.0.

//! Domain core for the symsight insight generator.
//!
//! This crate is a scaffold in the first Rust PR. Domain types and I/O land
//! in follow-on PRs; Python remains the user-facing implementation until then.

/// Workspace package version, single-sourced from the root `Cargo.toml`.
pub fn version() -> &'static str {
    env!("CARGO_PKG_VERSION")
}

#[cfg(test)]
mod tests {
    #[test]
    fn version_matches_workspace() {
        assert_eq!(crate::version(), "0.1.0");
    }
}
