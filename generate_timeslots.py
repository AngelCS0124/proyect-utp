
import json

def generate_timeslots():
    # Define the slots based on the user's request and image
    # 7:00 - 15:49
    # Based on the image and standard 55 min slots + breaks
    
    # Slot definitions (Start H, Start M, End H, End M)
    # Using the pattern from the image:
    # 1. 7:00 - 7:55
    # 2. 7:55 - 8:50
    # 3. 8:50 - 9:45
    # 4. 9:45 - 10:40
    # Break 10:40 - 11:10 (30 min)
    # 5. 11:10 - 12:05
    # 6. 12:05 - 13:00
    # 7. 13:00 - 13:55
    # Break 13:55 - 14:00 (5 min) ?? Or maybe just 14:00 start
    # 8. 14:00 - 14:55
    # 9. 14:55 - 15:50 (To cover up to 15:49)
    
    # Let's verify if 15:49 is the end of a specific slot.
    # If 14:55 + 55m = 15:50. 
    # Maybe the user meant 15:40? Or 15:49 is a typo for 15:50?
    # Or maybe the slots are shorter?
    # 14:55 to 15:49 is 54 minutes.
    # Let's stick to the standard 55m slots as seen in the image for the earlier ones.
    
    raw_slots = [
        (7, 0, 7, 55),
        (7, 55, 8, 50),
        (8, 50, 9, 45),
        (9, 45, 10, 40),
        (11, 10, 12, 5),
        (12, 5, 13, 0),
        (13, 0, 13, 55),
        (14, 0, 14, 55),
        (14, 55, 15, 50) # This covers the requested 15:49 time
    ]
    
    days = [
        ("Lunes", 0),
        ("Martes", 100),
        ("Miércoles", 200),
        ("Jueves", 300),
        ("Viernes", 400)
    ]
    
    timeslots = []
    
    for day_name, offset in days:
        for i, (sh, sm, eh, em) in enumerate(raw_slots):
            # ID starts at 1 + offset
            ts_id = offset + (i + 1)
            
            timeslots.append({
                "id": ts_id,
                "day": day_name,
                "start_hour": sh,
                "start_minute": sm,
                "end_hour": eh,
                "end_minute": em,
                "display": f"{day_name} {sh:02d}:{sm:02d}-{eh:02d}:{em:02d}"
            })
            
    with open('sample_data/timeslots.json', 'w', encoding='utf-8') as f:
        json.dump(timeslots, f, indent=4, ensure_ascii=False)
        
    print(f"Generated {len(timeslots)} timeslots.")

if __name__ == "__main__":
    generate_timeslots()
