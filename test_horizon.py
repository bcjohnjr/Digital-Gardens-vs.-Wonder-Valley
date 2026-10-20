"""Deterministic unit tests for the prospective multi-site sensitivity model."""
import unittest,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'software'))
from horizon_parallelism import rtt_ms,ring_collective_gb,training_overhead,SITE_COUNT
class HorizonTests(unittest.TestCase):
 def test_physics(self): self.assertAlmostEqual(rtt_ms(800)[0],8)
 def test_route_longer_than_light_floor(self): self.assertGreater(rtt_ms(800)[1],rtt_ms(800)[0])
 def test_local_inference(self): self.assertEqual(training_overhead(0,400,20,0)['network_overhead_pct'],0)
 def test_more_bandwidth(self):self.assertLess(training_overhead(50,1600,4)['network_overhead_pct'],training_overhead(50,400,4)['network_overhead_pct'])
 def test_collective_payload(self):self.assertAlmostEqual(ring_collective_gb(70),2*70*2*(SITE_COUNT-1)/SITE_COUNT)
 def test_2026_sync_dp(self):self.assertGreater(training_overhead(ring_collective_gb(70),400,20,2)['network_overhead_pct'],50)
 def test_no_faster_light(self):self.assertGreaterEqual(rtt_ms(50)[0],.5)
if __name__=='__main__':unittest.main()
