"""Regenerate the complete ten-sheet community/agriculture workbook.

The version-controlled workbook template is a formula-linked artifact_tool model,
not a stale five-sheet recreation. This script refreshes key inputs from the
source-of-record model and verifies the agricultural link before export.

Usage: python model/build_workbook.py
Requires: artifact_tool (see requirements.txt)
"""
from pathlib import Path
from artifact_tool import Blob,SpreadsheetFile
from agriculture_diesel import calculate
from community_benefits import CONFIG,estimate

ROOT=Path(__file__).resolve().parent.parent
TEMPLATE=Path(__file__).resolve().parent/'Community_Charging_Fuel_Parity_Template.xlsx'
OUTPUT=ROOT/'Community_Charging_Fuel_Parity_Model.xlsx'
assert TEMPLATE.is_file(), f'Missing version-controlled ten-sheet template: {TEMPLATE}'
wb=SpreadsheetFile.import_xlsx(Blob.load(str(TEMPLATE)))
expected={'Editable Inputs','Two-phase Benefits','PUE Utilisation',
 'Food Entitlement Summary','Sources and limits','Farm Coefficients',
 'RD Agriculture','17 Community Allocation','Fuel Sensitivity','Agricultural Summary'}
actual={wb.worksheets.get_item_at(i).name for i in range(10)}
if actual != expected:
 raise ValueError(f'Template sheet mismatch: missing {expected-actual}, unexpected {actual-expected}')
# Ensure formula uses the eight-region machinery fuel estimate, never the discarded 100M L scenario.
inputs=wb.worksheets.get_item('Editable Inputs')
assert inputs.get_range('A25').values[0][0].startswith('Eligible agricultural fuel')
inputs.get_range('B25').formulas=[["='RD Agriculture'!L10"]]
inputs.get_range('D25').values=[['Eight complete census districts; modeled machinery fuel only; NOT observed litres or municipal purchases']]
inputs.get_range('B2').values=[[CONFIG['population_both_phases']]]
inputs.get_range('B19').values=[[CONFIG['fresh_produce_entitlement_kg_per_resident']]]
inputs.get_range('B22').values=[[CONFIG['seafood_entitlement_kg_per_resident']]]
inputs.get_range('B26').values=[[CONFIG['other_commercial_fuel_eligible_litres']]]
inputs.get_range('B27').values=[[CONFIG['ag_fossil_parity_gap_cad_per_litre']]]
inputs.get_range('B28').values=[[CONFIG['other_fossil_parity_gap_cad_per_litre']]]
# Inputs in both document and workbook should be current, but source-of-record CSV is authoritative.
regional_fuel=calculate()[2]['diesel_l']
full=estimate(CONFIG,2)
assert abs(regional_fuel-CONFIG['agriculture_fuel_eligible_litres'])<0.01
assert abs(full['agricultural_fuel_price_parity_subsidy_mcad']-regional_fuel*CONFIG['ag_fossil_parity_gap_cad_per_litre']/1e6)<1e-9
assert abs(full['total_annual_community_value_mcad']-1876.6514349305558)<0.001
assert abs(full['annual_programme_funding_mcad']-1864.9557659450554)<0.001
SpreadsheetFile.export_xlsx(wb).save(str(OUTPUT))
print('Saved full 10-sheet workbook:', OUTPUT)
print(f'8-district ag diesel: {regional_fuel/1e6:.6f} million L/y')
print(f'Full community value: CAD {full["total_annual_community_value_mcad"]:.6f} million/y')
print(f'Illustrative funding: CAD {full["annual_programme_funding_mcad"]:.6f} million/y')
