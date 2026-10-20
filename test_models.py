"""Source-level consistency tests; no empirical hardware validation implied."""
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'software'))
from bc_datacentre_screening import calculate,NODES
from proximity_aware_training import evaluate

class TestScreeningAlgebra(unittest.TestCase):
    def test_17_nodes(self): self.assertEqual(len(NODES),17)
    def test_capacity(self): self.assertAlmostEqual(calculate()['it_capacity_mw'],3624.51,places=5)
    def test_energy(self): self.assertAlmostEqual(calculate()['facility_gwh_y'],32861.98,delta=.1)
    def test_heat(self): self.assertAlmostEqual(calculate()['useful_heat_gwh_y'],14573.57,delta=.1)
    def test_peak(self): self.assertAlmostEqual(calculate()['facility_peak_mw'],4168.1865,delta=.1)
    def test_usable_heat_monotonic(self):
        self.assertGreater(calculate(heat_use=.8)['useful_heat_gwh_y'],calculate(heat_use=.2)['useful_heat_gwh_y'])
    def test_zero_payload(self): self.assertEqual(evaluate(0,400,.5,2,1)['slowdown_pct'],0)
    def test_10GB_slowdown(self): self.assertAlmostEqual(evaluate(10,400,.5,2,.2)['slowdown_pct'],.402,places=5)
    def test_slowdown_grows_with_payload(self):
        self.assertGreater(evaluate(100,400,.5,2,.2)['slowdown_pct'],evaluate(1,400,.5,2,.2)['slowdown_pct'])
    def test_bandwidth_reduces_slowdown(self):
        self.assertLess(evaluate(10,800,.5,2,.2)['slowdown_pct'],evaluate(10,100,.5,2,.2)['slowdown_pct'])

if __name__=='__main__':unittest.main()
