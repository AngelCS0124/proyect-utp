import pandas as pd

try:
    df = pd.read_excel('/home/gina/Documentos/EstDatos/proyect-utp/Horarios EneAbr18.xlsx')
    print("Columns:", df.columns.tolist())
    print("First 5 rows:")
    print(df.head())
except Exception as e:
    print(f"Error reading excel: {e}")
