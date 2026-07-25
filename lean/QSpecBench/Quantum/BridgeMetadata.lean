/-!
# Manifest-aligned metadata for kernel-checked bridges.

Hashes are **pinned from** `schema/bridge_theorem_manifest.json` at release time.
`theorem_source_statement_hash` is syntactic Lean source extraction (not elaborator export).
`theoremElaboratorHash` is the v0.3 normalized type-signature hash pilot.
Python `qspecbench bridge-metadata verify` cross-checks these literals on every CI run.
-/

namespace QSpecBench.Quantum.BridgeMetadata

/-- Manifest-aligned metadata for kernel-checked bridges. -/
structure BridgeMetadata where
  benchmarkId : String
  claimedLink : String
  artifactSha256 : String
  astSha256 : String
  generatedLeanSha256 : String
  theoremIdentifierSha256 : String
  theoremSourceStatementHash : String
  theoremElaboratorHash : String
  packageLeanSha256 : String
  deriving Repr

def bridge_cnot_metadata : BridgeMetadata := {
  benchmarkId := "cnot_self_inverse_cancellation"
  claimedLink := "kernel_checked_artifact_semantics"
  artifactSha256 := "cb1e1e91496dd761ac2ec2c06b077e619452fd3804162aa646a054aa02a37354"
  astSha256 := "e3d3f42daa46d4d2a5c8f4c9857bf9d556df7ef6c9f530ce41ee61d6646bb7e9"
  generatedLeanSha256 := "af70d6950a1b6516d3a9399cc58268916da4ecd42eeda506cabf3feff4ed44d8"
  theoremIdentifierSha256 := "bc6c3f03aa3d48231df1690a92c692ea67c821d9f7c898185047fe53074f5b07"
  theoremSourceStatementHash := "90bad2d936dbcf09781fd10bb8bc32ccb0db645bbc946ad51c6892b4263ccef0"
  theoremElaboratorHash := "d5eb7ecbb9f29f95f7bff4887de8997cb34815e1e3012733afc3b1e6c5242f44"
  packageLeanSha256 := "7b04bd63e169cb1cce8e495dd0115d2e18ccdd1b4d5baecc0181e648ce1df69c"
}

def bridge_hadamard_metadata : BridgeMetadata := {
  benchmarkId := "hadamard_conjugates_x_to_z"
  claimedLink := "kernel_checked_artifact_semantics"
  artifactSha256 := "1acd5d4a1200d4ab90a0f886c784c64d313cf4e3e9bb3304ca9f32349ed9ae78"
  astSha256 := "20ba11fb108eb7d9fd66258197818165202009cf9a8ddaf1534b7627320c131f"
  generatedLeanSha256 := "c1c67ba08ef38883edf2b3a494cfdce653c8ab5b55ccc90da43f958501a391a8"
  theoremIdentifierSha256 := "cb0ae0d2ef85d9df73c5005dad812d9466e47addbf96dde3f4901ecf8f98377c"
  theoremSourceStatementHash := "81071fc7bf13c241377641f4ea9c728c10b3afbbe897cc551fa6e7d90958eaae"
  theoremElaboratorHash := "d19b731099df836f7b6e3387306fa0d82a85a57658dbb7e2fe50dd4fbfda1e30"
  packageLeanSha256 := "28ef8142b64fb8228df08717469ef12cbe0bbeb31a745bdeb58f0a5c34d97729"
}

def bridge_hadamard_cancel_metadata : BridgeMetadata := {
  benchmarkId := "single_qubit_gate_cancellation"
  claimedLink := "kernel_checked_artifact_semantics"
  artifactSha256 := "0a616794427bddf2144952d60642bd81229975c1017bdffa850721caa0ccab8a"
  astSha256 := "f731f909a694e3cc30b96260cc4f25a88888e093ef952d7bc9e0cbeb9973d4d9"
  generatedLeanSha256 := "1b2abc850edd8ec2ec695aaabad7ec51b262536586d5f4871648d703920df23e"
  theoremIdentifierSha256 := "444609491c695c04095883ccbfb9bf1d5565ef4de94ab4111be3ed1f939750cc"
  theoremSourceStatementHash := "1a1e5daae2c6f128938cdfd74d1a76920e82681b6cc347f93ce1b806cc8267a0"
  theoremElaboratorHash := "7baa6f6317bee71629f295e1f602e0e5ed06224ae38cae50b48c08855164f720"
  packageLeanSha256 := "9f15ec7c4ee8db125efccbed4619b9f596e24122d92177f18e6c02268c72e452"
}

def bridge_bell_metadata : BridgeMetadata := {
  benchmarkId := "bell_state_preparation"
  claimedLink := "kernel_checked_artifact_semantics"
  artifactSha256 := "ce49d4e871f80cc36e550cadd5559c84fb63af50a0cf3bf29a297d769ce723fa"
  astSha256 := "b10f78436f7d74bd4291c6a05cb415857f8102bcd4e12a22be0321eb6a34d635"
  generatedLeanSha256 := "dd5a8ce12f7c5ecc4769fc1fe7fa6186c7f52534af21b5d2b1e3fdb267ae3d95"
  theoremIdentifierSha256 := "d5b06e63a6d1a04ea12ec81b77f5a4d8697f6a97ab171a2e2923af64b6b19c40"
  theoremSourceStatementHash := "66e89587795528e78c0d4abb4c178b844da6f994b0cbfcb9bcd83175c499b1da"
  theoremElaboratorHash := "0857f84b49f7b7d5522811279ba3024dff365f34613a4e9df7f07c03c0cbf202"
  packageLeanSha256 := "c77694903d65b978dbb4ff2f85b8465d92e47d36b454e426658343df8020fd75"
}

def bridge_swap_metadata : BridgeMetadata := {
  benchmarkId := "swap_from_three_cx"
  claimedLink := "kernel_checked_artifact_semantics"
  artifactSha256 := "7a86fe448088fb7bff5e67cc627a3b2c257b690b6e8ea3b8c47e6251744684b9"
  astSha256 := "f56ae68da29a95751c8273e8a97849139cf683ebdf9caa1a3061f219fd3962cc"
  generatedLeanSha256 := "7bca344aba34b71cf7cbc0d1d68db01c3f359f2c5e58391d42d5b693c81a9523"
  theoremIdentifierSha256 := "90673f619c0d5d06700e1f07c301e4dcea53e23d27facc5b1e03d399007c4972"
  theoremSourceStatementHash := "5ab0a29c12bac6bb5bea240295ac00e77f32392f814f13ade3bf585947f693d7"
  theoremElaboratorHash := "b3f11063a041dcecf8401c3626fa161bfb83096177cb1cfa773e79cc5ade8bff"
  packageLeanSha256 := "8e9eacbceb895b9c9806cc79c6fe3ac6e0ee9618036ca0996c852d400ffbc229"
}

def bridge_toffoli_metadata : BridgeMetadata := {
  benchmarkId := "native_ccx_artifact_denotes_toffoli_unitary"
  claimedLink := "kernel_checked_artifact_semantics"
  artifactSha256 := "d37ec11fdd1ff70e5f8debf1d392b8bad04ac650f57f06a67248da503f665511"
  astSha256 := "c0b49ec233d0558ae59549dacd41593a724394a64d9feef218407baa50557795"
  generatedLeanSha256 := "5b20b2248452752eb707da5c515a50912dddebde4bc66e893e3f63b5640c707a"
  theoremIdentifierSha256 := "cac696170d47a44d717617f024fb31e44b38cdbd491d79ee9a5c87a9d60aca2d"
  theoremSourceStatementHash := "1855f4e15c5e2886901262e73b9bcc6336c7a06e84c7e991a3b6a3ae5baf215a"
  theoremElaboratorHash := "cc4952cf279c0b991de8b051148aaeba742f748f2f8fbd2fddcc8d70db7783a6"
  packageLeanSha256 := "7f4007e3c454390a4c69274f95a49ae93a7dff1635c8bf0947380be14db46b3a"
}

def bridge_toffoli_pair_metadata : BridgeMetadata := {
  benchmarkId := "toffoli_decomposition_equivalence"
  claimedLink := "kernel_checked_artifact_semantics"
  artifactSha256 := "d37ec11fdd1ff70e5f8debf1d392b8bad04ac650f57f06a67248da503f665511"
  astSha256 := "c0b49ec233d0558ae59549dacd41593a724394a64d9feef218407baa50557795"
  generatedLeanSha256 := "d081179341f6d920f77a537a3c634f46906af642d68d38c34fb6d45a733a4809"
  theoremIdentifierSha256 := "490e177553421771aca85d50b38a707fbbce17a903c39d107cafe4923941a4ce"
  theoremSourceStatementHash := "f00e3bb817902ee291bc017bfa9aad7897faed07dc9f7a26f89f62702a48b100"
  theoremElaboratorHash := "e213fe8f4169874802ed34e5615ae9ab8d75ce1a40810d64d592656979193e74"
  packageLeanSha256 := "7f4007e3c454390a4c69274f95a49ae93a7dff1635c8bf0947380be14db46b3a"
}

def bridge_teleport_metadata : BridgeMetadata := {
  benchmarkId := "teleportation_preserves_state_up_to_pauli_correction"
  claimedLink := "kernel_checked_artifact_semantics"
  artifactSha256 := "4dcc0c1b7fe0a92f3be82332241535377b8005cce5bad6dfa62941868f28c898"
  astSha256 := "2dd1807377ae7ec0677c7deeee471d29e53041b3d78d397bfa762c348857aab3"
  generatedLeanSha256 := "2d8c81ed223e8c9b7f40a11d2457945d84ea0548455016ba205d6a26faffb568"
  theoremIdentifierSha256 := "b2f4d0df0c4ffad9cf822c70186821c80b56ca83695f21c51cc34216371270ef"
  theoremSourceStatementHash := "d4ad77e9404633aee0e0c802b3b81841a9ab29b44b587044457ccc8e4d1c1786"
  theoremElaboratorHash := "4f26fb4ce497c2f0deb5b42955a7b58f203751201de85671ec99560a50572074"
  packageLeanSha256 := "a6edd501d38cf21bd7dbbe89c51257f1845b4aed7269c28ed57ddf257fbbc7c1"
}

def bridge_clifford_metadata : BridgeMetadata := {
  benchmarkId := "clifford_simplification_preserves_unitary"
  claimedLink := "kernel_checked_artifact_semantics"
  artifactSha256 := "929766d92f5a9bb80e986776e5a74023f01deae1d78d0be0bbd78bc40cea7876"
  astSha256 := "8d877bec8367c1b09dc280937365b1e3eeb8d957246b8a6806098dd3a0232123"
  generatedLeanSha256 := "81c2803db29a8f1311ab6eebdc4d1514775016161e9d1874be8cfddb3d2a5c5c"
  theoremIdentifierSha256 := "331a27fda0a9837a254c1976074984112760d45de25c773bc8f9280894ea5c4e"
  theoremSourceStatementHash := "7e6ed8251e88cab400c15402e839b0db03aa1cc4097d81cf56586982a9275812"
  theoremElaboratorHash := "aeabd1fbd8ee6dce934467594e8d3d5385e59eec4f0ceb85d06b8c54b6fec6e5"
  packageLeanSha256 := "1248e66bba70d4634d4713613c3fa1095d6158e4c59ace8b8d45bc663eb29a30"
}

def allKernelBridgeMetadata : List BridgeMetadata := [
  bridge_cnot_metadata,
  bridge_hadamard_metadata,
  bridge_hadamard_cancel_metadata,
  bridge_bell_metadata,
  bridge_swap_metadata,
  bridge_toffoli_metadata,
  bridge_toffoli_pair_metadata,
  bridge_teleport_metadata,
  bridge_clifford_metadata,
]

/-! ## Dynamic (measure+if CanonicalAst) bridge metadata — not matrix `KERNEL_BRIDGE`.

These pin the declared on-disk dynamic-fragment artifact + fail-closed CanonicalAst mirror
hash, and the Lean theorem that anchors the claimed link. `DynamicAstBridgeMetadata` pins
`kernel_checked_dynamic_ast_semantics` (structural AST binding only). -/
structure DynamicAstBridgeMetadata where
  benchmarkId : String
  claimedLink : String
  propositionId : String
  dynamicArtifactSha256 : String
  dynamicAstSha256 : String
  leanTheorem : String
  deriving Repr

/-- `DynamicDenotationBridgeMetadata` pins the strictly stronger `kernel_checked_dynamic_denotation`
link: the pinned theorem's on-disk statement must invoke `Measurement.writeZOutcome` /
`ClassicalReg` denotation functions (checked separately by
`qspecbench.bridge_metadata.verify_dynamic_denotation_bridge_metadata`), not just a bare
CanonicalAst-hash equality. -/
structure DynamicDenotationBridgeMetadata where
  benchmarkId : String
  claimedLink : String
  propositionId : String
  dynamicArtifactSha256 : String
  dynamicAstSha256 : String
  leanTheorem : String
  deriving Repr

/-- Parent-benchmark infrastructure anchor: `teleportation_preserves_state_up_to_pauli_correction`'s
`dynamic_ast_bridge_metadata` proof obligation cites this pin (proposition v3 of the sibling
dynamic-protocol ABRC), distinct from the sibling's own retained anchor below. -/
def bridge_teleport_dynamic_ast_metadata : DynamicAstBridgeMetadata := {
  benchmarkId := "teleportation_preserves_state_up_to_pauli_correction"
  claimedLink := "kernel_checked_dynamic_ast_semantics"
  propositionId := "teleportation_dynamic_feedforward_protocol_v3"
  dynamicArtifactSha256 := "250860b2db62ab8a992f79a761f49c627087272b90265aad3c926b8ecf383024"
  dynamicAstSha256 := "5bf411e14ed8898bf1af2367911f75ebd46fa659b3dd156500744f7ec2f18654"
  leanTheorem := "QSpecBench.teleport_dynamic_feedforward_artifact_protocol_linked"
}

/-- `teleportation_dynamic_feedforward_protocol` sibling ABRC: retained AST-semantics anchor
(supersedes into `bridge_teleport_dynamic_denotation_metadata` below as the benchmark's
headline pin; kept as supporting evidence, not a fake/duplicate promotion). -/
def bridge_teleport_dynamic_feedforward_abrc_metadata : DynamicAstBridgeMetadata := {
  benchmarkId := "teleportation_dynamic_feedforward_protocol"
  claimedLink := "kernel_checked_dynamic_ast_semantics"
  propositionId := "teleportation_dynamic_feedforward_protocol_v3"
  dynamicArtifactSha256 := "250860b2db62ab8a992f79a761f49c627087272b90265aad3c926b8ecf383024"
  dynamicAstSha256 := "5bf411e14ed8898bf1af2367911f75ebd46fa659b3dd156500744f7ec2f18654"
  leanTheorem := "QSpecBench.teleport_dynamic_feedforward_artifact_protocol_linked"
}

/-- `teleportation_dynamic_feedforward_protocol` sibling ABRC headline pin (2026-07-25
promotion): the same theorem additionally composes `denoteCanonicalMeasures` /
`canonicalControlsToStmts` (Measurement/ClassicalReg denotation), not a bare AST-hash pin. -/
def bridge_teleport_dynamic_denotation_metadata : DynamicDenotationBridgeMetadata := {
  benchmarkId := "teleportation_dynamic_feedforward_protocol"
  claimedLink := "kernel_checked_dynamic_denotation"
  propositionId := "teleportation_dynamic_feedforward_protocol_v3"
  dynamicArtifactSha256 := "250860b2db62ab8a992f79a761f49c627087272b90265aad3c926b8ecf383024"
  dynamicAstSha256 := "5bf411e14ed8898bf1af2367911f75ebd46fa659b3dd156500744f7ec2f18654"
  leanTheorem := "QSpecBench.teleport_dynamic_feedforward_artifact_protocol_linked"
}

def bridgeMetadataHonestyNote : String :=
  "theoremElaboratorHash is Lean #check export (v1 primary); theorem_source_statement_hash is syntactic secondary. \
teleportation_dynamic_feedforward_protocol claims kernel_checked_dynamic_denotation via \
bridge_teleport_dynamic_denotation_metadata (2026-07-25); the AST-semantics anchor is retained \
as supporting evidence only, not the benchmark's headline."

#check bridge_cnot_metadata
#check bridgeMetadataHonestyNote
#check bridge_teleport_dynamic_ast_metadata
#check bridge_teleport_dynamic_feedforward_abrc_metadata
#check bridge_teleport_dynamic_denotation_metadata

end QSpecBench.Quantum.BridgeMetadata
