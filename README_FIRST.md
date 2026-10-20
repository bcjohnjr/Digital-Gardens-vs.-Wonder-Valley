# Digital Gardens versus Wonder Valley — food-entitlement and community mobility revision (20 October 2026)

**The proposed programme does NOT provide free electricity to residences.** Its free-electricity benefit is restricted to qualified EV charging. Renewable agriculture and transport fuel beneficiaries pay the fossil-fuel benchmark price; the programme subsidises only verified positive renewable-fuel price differentials. An optional vehicle-provision scenario is isolated and must be removed if not confirmed by the proponent.

**Food delivery commitment modeled:** 146 kg of fresh produce and 46 kg of marketable seafood per resident annually; full cumulative Phase 2 covers 787,934 residents. This is not an allocation based on fixed shares of total food output. The new food-benefit line is CAD 656.349 million/year.

## Documents
- `CPP_Blinded_Manuscript.docx` and `PDF/CPP_Blinded_Manuscript.pdf`: 15 embedded figures, 17 numbered tables plus assumptions register; updated Tables 14–17.
- `CPP_Supplementary_Methods.docx`: S16–S17 economic and utilisation/PUE methods.
- `CPP_Cover_Letter.docx`, `CPP_Separate_Title_Page.docx` (editor-only), `AUTHOR_REFEREE_RESPONSE.docx` (editorial working material).
- `Community_Charging_Fuel_Parity_Model.xlsx`: formula-driven editable two-phase programme and nine-case PUE sheet.
- `model/community_benefits.py`, `model/test_community_benefits.py`: rerunnable Python standard-library scenario and 13 community-model checks.
- `results/community_two_phase_baseline.csv`, `results/community_two_phase_sensitivity.csv`, `results/electricity_heat_pue_utilization.csv`, `results/community_assumptions.json`.
- Prior software, results, figures and tests are retained in the supplementary folders.

## Source and rights status
The public GitHub source repository exists and was previously verified: https://github.com/bcjohnjr/Digital-Gardens-vs.-Wonder-Valley , baseline commit `04bb59ed071c98c283e2eb21120b2d7b934d2f70`. The complete version-specific model for this submission is supplied in the archive; a publication-specific archival DOI requires a deposited tagged record. Any redistribution licence remains subject to author approval; reproducibility access is provided through this archived submission copy.

## Essential finance cautions
- The 787,934 residents are cumulative after Phase 2. The 50/50 phase distribution is an assumption.
- Market-equivalent value is NOT cash, budgeted profits or net income; asset replacement is annual-equivalent value.
- The CAD 4.6-billion annual aspiration is NOT supported by audited distributable cash flow.
- Renewable fuel parity support is not a free fuel giveaway; it pays only the marginal premium.
- Charging adds roughly 0.707 TWh/year to energy needs in the mature programme screen, on top of computing and food operations; firm supply and hourly grid capacity are not verified.
- EV fleet provision and fuel subsidy volumes are scenario choices, not signed contracts. The 146/46-kg food entitlements are explicit programme targets, not delivered quantities or binding commitments. Saleable yield assumptions are 90% for produce and 65% for aquaculture live weight, awaiting species-specific validation.

## Revised per-resident food accounting — definitive current model
Phase 1: 393,967 residents; 57,519.182 t/year fresh produce; 18,122.482 t/year marketable seafood; annual food market-equivalent value CAD 328.174511 million. Cumulative Phase 2: 787,934 residents; 115,038.364 t/year produce; 36,244.964 t/year marketable seafood; food value CAD 656.349022 million. The CURRENT agriculture screen covers 18.6904995 million litres/year and CAD 4.672624875 million/year at the assumed CAD 0.25/L premium. Full mature programme annual market-equivalent value **CAD 1,876.651435 million** and annual financing requirement **CAD 1,864.955766 million**. Annual gap to CAD 4.6-billion aspiration **CAD 2,723.348565 million**. Optional annualized vehicle value CAD 935.671625 million is included and is not a confirmed commitment. No free household electricity.

## Reproducing this package
`python model/community_benefits.py` regenerates the phase, food-entitlement and PUE sensitivity CSV/JSON files. `python model/build_workbook.py` regenerates the existing ten-sheet, formula-linked Excel workbook from its versioned template (requires `artifact_tool`); this action retains all agricultural worksheets and uses the regional-district calculation, not a 100-million-litre constant. `python model/test_community_benefits.py` executes 13 community checks. Older manuscript-assembly scripts, which would overwrite food entitlements with prior assumptions, have been excluded intentionally. The Word manuscript remains the editorial source of record, while the Excel model and CSVs are the calculation source of record. Earlier AI/network and circular-food scripts have been retained unchanged for reproducibility.

## Current agriculture-fuel extension (20 October 2026)
The prior 100-million-litre agricultural-fuel assumption is replaced in all current recalculations with a modeled 18.6905-million-litre full-eight-regional-district SCREEN. Official 2021 B.C. district farm/crop/pasture counts are paired with unverified machinery litres-per-hectare and service assumptions. These entire districts contain agriculture outside municipal boundaries. Allocation among 17 hosts does not constitute a municipal inventory. At CAD 0.25/L the modeled annual parity payment is CAD 4.6726m. Full programme value is CAD 1,876.651m annually including optional annualized vehicle provision; programme funding is CAD 1,864.956m. No free home electricity; food entitlements remain 146/46 kg/resident. Tables 16 and 17 and Figure 15 are inline.

Run: `python model/agriculture_diesel.py`, `python model/community_benefits.py`, `python -m unittest discover -s model -p "test_*.py"`. A publication-specific DOI and any redistribution licence are author-controlled decisions; this submission includes a complete reviewable archive.

## Submission audit (referee reconciliation)
This version supersedes older, inconsistent community-benefit narrative amounts. The two-phase CSV is the numerical source of record; programme value CAD 1,876.651435m, funding CAD 1,864.955766m, agricultural fuel 18.6904995m L, parity CAD 4.672624875m. Figure 7 was verified present in the rendered pages. Historical rejected fuel allocations, if mentioned, are clearly named rejected comparators only. `run_all.py` and `requirements.txt` are included and checksummed. The Github repository is not asserted to be empty or incomplete.


## Final production corrections (20 October 2026)
The 43-page manuscript is image and text checked on every page. Figure 8/caption are together on page 27; Table 1 starts and finishes on page 7. Prior reported numeral blocks are extraction artifacts, not visible PDF content. `render_log.txt` is excluded; there is one canonical `RENDER_LOG.txt`. The new author response and `PRODUCTION_QA_RECORD.json` provide explicit QA outcomes. All 68 tests passed again. See `PRODUCTION_AND_RECONCILIATION_AUDIT.md`. GitHub file-upload status is not inferred.
