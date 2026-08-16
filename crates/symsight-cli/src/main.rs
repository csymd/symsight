// Copyright (c) 2026, PalEm Dynamics LLC
// Licensed under the Apache License, Version 2.0.

use clap::Parser;
use symsight_cli::Cli;

fn main() {
    let cli = Cli::parse();
    std::process::exit(symsight_cli::execute(cli));
}
