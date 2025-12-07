import pandas as pd

def inspect_csv():
    df = pd.read_csv('../sample_data/Disponibilidad - Disponibilidad(1).csv', header=None)
    
    # Find column for Adriana
    name_row = 0
    target_name = "Adriana L. Trujillo"
    
    found_col = -1
    for col in range(df.shape[1]):
        val = str(df.iloc[name_row, col]).strip()
        if val == target_name:
            found_col = col
            break
            
    if found_col == -1:
        print(f"Could not find {target_name}")
        return

    print(f"Found {target_name} at column {found_col}")
    
    # Print data for this professor
    print("Data rows:")
    for row in range(2, 20):
        time_val = df.iloc[row, 0]
        # Get 5 columns for this prof
        vals = df.iloc[row, found_col:found_col+5].values
        print(f"Row {row} ({time_val}): {vals}")

if __name__ == "__main__":
    inspect_csv()
