// Copyright (c) 2026, PalEm Dynamics LLC
// Licensed under the Apache License, Version 2.0.

//! Domain core for the symsight insight generator.
//!
//! Python remains the user-facing implementation until later PRs land
//! bindings. This crate currently owns brand models, YAML loading, textutil,
//! draft I/O, finalize, and brandcheck.

pub mod brand;
pub mod brandcheck;
pub mod draft_io;
pub mod error;
pub mod finalize;
pub mod models;
pub mod textutil;

pub use brand::{list_brand_files, list_brands, load_brand_file, resolve_brand};
pub use brandcheck::{check_path, check_text, find_hits, iter_scan_files, scan_paths};
pub use draft_io::{
    draft_meta_json, list_drafts, parse_front_matter, read_draft, render_front_matter,
    save_draft_body, set_status, strip_disclaimer_from_body, unique_draft_path,
    write_draft_content, write_meta_json, write_new_draft, WriteNewDraft,
};
pub use error::{BrandError, FinalizeError, GenerateError, TextError};
pub use finalize::{finalize_draft, list_final};
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
