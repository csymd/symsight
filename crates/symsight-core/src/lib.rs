// Copyright (c) 2026, PalEm Dynamics LLC
// Licensed under the Apache License, Version 2.0.

//! Domain core for the symsight insight generator.
//!
//! Python remains the user-facing implementation until later PRs land
//! bindings. This crate currently owns brand models, YAML loading, and textutil.

pub mod brand;
pub mod error;
pub mod models;
pub mod textutil;

pub use brand::{list_brand_files, list_brands, load_brand_file, resolve_brand};
pub use error::{BrandError, GenerateError, TextError};
pub use models::{
    ArticleFormatSpec, Brand, ContentFormat, Draft, DraftMeta, FormatSpecs, FrontValue,
    GenerateRequest, SocialFormatSpec, TypeSpec,
};
pub use textutil::{
    char_count, clean_body, extract_social_text, extract_title_body, is_plausible_title, slugify,
    word_count,
};

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
