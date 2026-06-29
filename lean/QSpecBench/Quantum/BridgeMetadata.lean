/-!
# Manifest-aligned metadata for kernel-checked codegen-trace bridges.

Hashes are **pinned from** `schema/bridge_theorem_manifest.json` at release time — not
exported from the Lean elaborator. Python `qspecbench bridge-metadata verify` cross-checks
these literals against the manifest on every CI run.
-/

namespace QSpecBench.Quantum.BridgeMetadata

/-- Manifest-aligned metadata for kernel-checked codegen-trace bridges. -/
structure BridgeMetadata where
  benchmarkId : String
  claimedLink : String
  artifactSha256 : String
  astSha256 : String
  generatedLeanSha256 : String
  theoremIdentifierSha256 : String
  theoremSourceStatementHash : String
  packageLeanSha256 : String
  deriving Repr

def bridge_cnot_metadata : BridgeMetadata := {
  benchmarkId := "cnot_self_inverse_cancellation"
  claimedLink := "kernel_checked_codegen_trace"
  artifactSha256 := "cb1e1e91496dd761ac2ec2c06b077e619452fd3804162aa646a054aa02a37354"
  astSha256 := "e3d3f42daa46d4d2a5c8f4c9857bf9d556df7ef6c9f530ce41ee61d6646bb7e9"
  generatedLeanSha256 := "af70d6950a1b6516d3a9399cc58268916da4ecd42eeda506cabf3feff4ed44d8"
  theoremIdentifierSha256 := "bc6c3f03aa3d48231df1690a92c692ea67c821d9f7c898185047fe53074f5b07"
  theoremSourceStatementHash := "90bad2d936dbcf09781fd10bb8bc32ccb0db645bbc946ad51c6892b4263ccef0"
  packageLeanSha256 := "7b04bd63e169cb1cce8e495dd0115d2e18ccdd1b4d5baecc0181e648ce1df69c"
}

def bridge_hadamard_metadata : BridgeMetadata := {
  benchmarkId := "hadamard_conjugates_x_to_z"
  claimedLink := "kernel_checked_codegen_trace"
  artifactSha256 := "1acd5d4a1200d4ab90a0f886c784c64d313cf4e3e9bb3304ca9f32349ed9ae78"
  astSha256 := "20ba11fb108eb7d9fd66258197818165202009cf9a8ddaf1534b7627320c131f"
  generatedLeanSha256 := "c1c67ba08ef38883edf2b3a494cfdce653c8ab5b55ccc90da43f958501a391a8"
  theoremIdentifierSha256 := "cb0ae0d2ef85d9df73c5005dad812d9466e47addbf96dde3f4901ecf8f98377c"
  theoremSourceStatementHash := "81071fc7bf13c241377641f4ea9c728c10b3afbbe897cc551fa6e7d90958eaae"
  packageLeanSha256 := "28ef8142b64fb8228df08717469ef12cbe0bbeb31a745bdeb58f0a5c34d97729"
}

def bridge_hadamard_cancel_metadata : BridgeMetadata := {
  benchmarkId := "single_qubit_gate_cancellation"
  claimedLink := "kernel_checked_codegen_trace"
  artifactSha256 := "0a616794427bddf2144952d60642bd81229975c1017bdffa850721caa0ccab8a"
  astSha256 := "f731f909a694e3cc30b96260cc4f25a88888e093ef952d7bc9e0cbeb9973d4d9"
  generatedLeanSha256 := "1b2abc850edd8ec2ec695aaabad7ec51b262536586d5f4871648d703920df23e"
  theoremIdentifierSha256 := "444609491c695c04095883ccbfb9bf1d5565ef4de94ab4111be3ed1f939750cc"
  theoremSourceStatementHash := "1a1e5daae2c6f128938cdfd74d1a76920e82681b6cc347f93ce1b806cc8267a0"
  packageLeanSha256 := "9f15ec7c4ee8db125efccbed4619b9f596e24122d92177f18e6c02268c72e452"
}

def bridge_bell_metadata : BridgeMetadata := {
  benchmarkId := "bell_state_preparation"
  claimedLink := "kernel_checked_codegen_trace"
  artifactSha256 := "ce49d4e871f80cc36e550cadd5559c84fb63af50a0cf3bf29a297d769ce723fa"
  astSha256 := "b10f78436f7d74bd4291c6a05cb415857f8102bcd4e12a22be0321eb6a34d635"
  generatedLeanSha256 := "dd5a8ce12f7c5ecc4769fc1fe7fa6186c7f52534af21b5d2b1e3fdb267ae3d95"
  theoremIdentifierSha256 := "d5b06e63a6d1a04ea12ec81b77f5a4d8697f6a97ab171a2e2923af64b6b19c40"
  theoremSourceStatementHash := "66e89587795528e78c0d4abb4c178b844da6f994b0cbfcb9bcd83175c499b1da"
  packageLeanSha256 := "c77694903d65b978dbb4ff2f85b8465d92e47d36b454e426658343df8020fd75"
}

def bridge_swap_metadata : BridgeMetadata := {
  benchmarkId := "swap_from_three_cx"
  claimedLink := "kernel_checked_codegen_trace"
  artifactSha256 := "7a86fe448088fb7bff5e67cc627a3b2c257b690b6e8ea3b8c47e6251744684b9"
  astSha256 := "f56ae68da29a95751c8273e8a97849139cf683ebdf9caa1a3061f219fd3962cc"
  generatedLeanSha256 := "7bca344aba34b71cf7cbc0d1d68db01c3f359f2c5e58391d42d5b693c81a9523"
  theoremIdentifierSha256 := "90673f619c0d5d06700e1f07c301e4dcea53e23d27facc5b1e03d399007c4972"
  theoremSourceStatementHash := "5ab0a29c12bac6bb5bea240295ac00e77f32392f814f13ade3bf585947f693d7"
  packageLeanSha256 := "8e9eacbceb895b9c9806cc79c6fe3ac6e0ee9618036ca0996c852d400ffbc229"
}

def bridge_toffoli_metadata : BridgeMetadata := {
  benchmarkId := "toffoli_decomposition_equivalence"
  claimedLink := "kernel_checked_codegen_trace"
  artifactSha256 := "d37ec11fdd1ff70e5f8debf1d392b8bad04ac650f57f06a67248da503f665511"
  astSha256 := "c0b49ec233d0558ae59549dacd41593a724394a64d9feef218407baa50557795"
  generatedLeanSha256 := "d081179341f6d920f77a537a3c634f46906af642d68d38c34fb6d45a733a4809"
  theoremIdentifierSha256 := "cac696170d47a44d717617f024fb31e44b38cdbd491d79ee9a5c87a9d60aca2d"
  theoremSourceStatementHash := "1855f4e15c5e2886901262e73b9bcc6336c7a06e84c7e991a3b6a3ae5baf215a"
  packageLeanSha256 := "7f4007e3c454390a4c69274f95a49ae93a7dff1635c8bf0947380be14db46b3a"
}

def allKernelBridgeMetadata : List BridgeMetadata := [
  bridge_cnot_metadata,
  bridge_hadamard_metadata,
  bridge_hadamard_cancel_metadata,
  bridge_bell_metadata,
  bridge_swap_metadata,
  bridge_toffoli_metadata,
]

def bridgeMetadataHonestyNote : String :=
  "theorem_source_statement_hash pins Lean theorem source text from manifest; not an elaborator export."

#check bridge_cnot_metadata
#check bridge_hadamard_metadata
#check bridge_bell_metadata
#check bridge_swap_metadata
#check bridgeMetadataHonestyNote

end QSpecBench.Quantum.BridgeMetadata
