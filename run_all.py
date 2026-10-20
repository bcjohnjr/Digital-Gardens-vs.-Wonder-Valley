"""Reproduce the updated 2026-10-20 agricultural/community-screening outputs.

Also runs all available test modules in `model/`. Earlier training and seasonal
source models remain available in their respective archived folders; this command
is not a claim to regenerate every historical figure or third-party dataset.
"""
from pathlib import Path
import subprocess,sys
ROOT=Path(__file__).resolve().parent
commands=[
 [sys.executable,str(ROOT/'model/agriculture_diesel.py')],
 [sys.executable,str(ROOT/'model/community_benefits.py')],
 [sys.executable,str(ROOT/'model/build_workbook.py')],
 [sys.executable,'-m','unittest','discover','-s',str(ROOT/'model'),'-p','test_*.py'],
]
for command in commands:
 print('RUN',' '.join(command),flush=True)
 subprocess.run(command,cwd=ROOT,check=True)
print('All current agricultural and community model steps complete.')
