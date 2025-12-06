import pandas as pd

try:
    df = pd.read_excel('/home/gina/Documentos/EstDatos/proyect-utp/sample_data/Disponibilidad.xlsx', header=None)
    print("Shape:", df.shape)
    print("First 20 rows, first 20 columns:")
    print(df.iloc[:20, :20].to_string())
except Exception as e:
    print(f"Error reading Excel: {e}")
