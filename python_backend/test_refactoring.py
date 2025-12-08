
import unittest
import os
import sys
import time
from data_loader import DataLoader
from scheduler_wrapper import PyScheduler
from config.periods import PERIODOS

class TestRefactoring(unittest.TestCase):
    def setUp(self):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.courses_path = os.path.join(self.base_dir, 'courses_full.csv')
        self.professors_path = os.path.join(os.path.dirname(self.base_dir), 'sample_data', 'professors.json')
        self.timeslots_path = os.path.join(os.path.dirname(self.base_dir), 'sample_data', 'timeslots.json')
        
        # Load data
        self.courses = DataLoader.load_courses_from_csv(self.courses_path)
        
        prof_data = DataLoader.load_professors_from_json(self.professors_path)
        if isinstance(prof_data, dict):
            self.professors = prof_data['professors']
            self.timeslots = prof_data.get('timeslots', [])
        else:
            self.professors = prof_data
            self.timeslots = []
            
        if not self.timeslots:
            self.timeslots = DataLoader.load_timeslots_from_json(self.timeslots_path)

        self.scheduler = PyScheduler()
        
        # Load timeslots first
        for ts in self.timeslots:
            self.scheduler.load_timeslot(ts.id, ts.dia, ts.hora_inicio, ts.minuto_inicio, ts.hora_fin, ts.minuto_fin)
            
        # Load professors
        for p in self.professors:
            self.scheduler.load_professor(p.id, p.nombre, p.bloques_disponibles)

    def test_1_no_cuatrimestre_0(self):
        """Test 1: Nunca genera cuatrimestre 0"""
        print("\nRunning Test 1: No Cuatrimestre 0")
        # Check loaded courses
        for c in self.courses:
            self.assertIsNotNone(c.cuatrimestre, f"Course {c.id} has None semester")
            self.assertGreater(c.cuatrimestre, 0, f"Course {c.id} has semester 0")
            
    def test_constraints_and_generation(self):
        """Run generation and check constraints"""
        print("\nRunning Generation Tests...")
        
        # Filter for one period to make it faster/feasible (e.g. sept-dec)
        period_courses = [c for c in self.courses if c.cuatrimestre in [1, 4, 7, 10]]
        
        for c in period_courses:
            duration = int(c.creditos / 15.0) if c.creditos else 4
            if duration < 1: duration = 1
            self.scheduler.load_course(c.id, c.nombre, c.matricula, c.prerequisitos, getattr(c, 'id_grupo', 0), duration)
            
        # Generate
        start_time = time.time()
        result = self.scheduler.generate_schedule_with_config(30, "time_limit") # 30 seconds limit
        duration = time.time() - start_time
        
        print(f"Generation took {duration:.2f}s. Success: {result['success']}")
        print(f"Assignments: {len(result['assignments'])}")
        if not result['success']:
            print(f"Error Message:\n{result['error_message']}")
        
        if not result['assignments']:
            self.fail("No assignments generated")
            
        assignments = result['assignments']
        
        # Test 2: Completeness (Best Effort check)
        # We expect at least some assignments.
        self.assertGreater(len(assignments), 0)
        
        # Test 3: Max 3 hours consecutive
        # We need to reconstruct the schedule to check this
        course_schedule = {} # course_id -> {day -> [slots]}
        
        # Helper to get slot details
        slot_map = {t.id: t for t in self.timeslots}
        
        for a in assignments:
            cid = a['course_id']
            tid = a['timeslot_id']
            ts = slot_map.get(tid)
            if not ts: continue
            
            if cid not in course_schedule: course_schedule[cid] = {}
            if ts.dia not in course_schedule[cid]: course_schedule[cid][ts.dia] = []
            
            course_schedule[cid][ts.dia].append(ts)
            
        for cid, days in course_schedule.items():
            for day, slots in days.items():
                # Sort by time
                slots.sort(key=lambda x: x.hora_inicio * 60 + x.minuto_inicio)
                
                consecutive = 0
                last_end = -1
                current_run = 0
                
                for s in slots:
                    start = s.hora_inicio * 60 + s.minuto_inicio
                    end = s.hora_fin * 60 + s.minuto_fin
                    
                    if last_end == -1 or start == last_end:
                        current_run += 1
                    else:
                        current_run = 1
                    
                    if current_run > 3:
                        self.fail(f"Course {cid} has > 3 consecutive hours on {day}")
                    
                    last_end = end

        print("Test 3 Passed: Max 3 consecutive hours respected")

        # Test 5: Priority 7:00 AM
        starts_at_7 = 0
        total_slots = 0
        for a in assignments:
            ts = slot_map.get(a['timeslot_id'])
            if ts:
                total_slots += 1
                if ts.hora_inicio == 7:
                    starts_at_7 += 1
        
        print(f"7:00 AM starts: {starts_at_7}/{total_slots} ({starts_at_7/total_slots*100:.1f}%)")
        # We can't assert 100% but it should be high if possible.
        
        # Test 6: Time limit respected
        # We ran with 30s. It should be around 30s if it hit the limit, or less if finished.
        # But we can't easily test "exactness" here without a long running case.
        # The C++ code checks every 1000 backtracks.
        
if __name__ == '__main__':
    unittest.main()
