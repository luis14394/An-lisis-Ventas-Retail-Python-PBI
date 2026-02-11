import pandas as pd
import numpy as np

#carga de datos
df = pd.read_csv(r'C:\One_Proyect\retail_data.csv')
#copia del dataset original
df_raw = df.copy()
#Pasamos los nombres de las columnas a minusculas
df.columns = df.columns.str.lower()

# Eliminamos espacios en blanco al inicio o final de los nombres
df.columns = df.columns.str.strip()

# Reemplazamos espacios internos por guiones bajos para facilitar el acceso
df.columns = df.columns.str.replace(' ', '_')

# Identificamos columnas de texto para limpieza 
text_columns = df.select_dtypes(include=['object']).columns

# Eliminamos espacios en blaco al inicio y al final 
df[text_columns] = df[text_columns].apply(lambda x: x.str.strip())

# Reemplazamos valores vacios 
df = df.replace(r'^\s*$', np.nan, regex=True)

# Llenamos valores nulos en columnas no especificadas
df['gender'] = df['gender'].fillna('Not Specified')
df['customer_segment'] = df['customer_segment'].fillna('Regular')
df['product_category'] = df['product_category'].fillna('General')

# Llenamos valores nulos con 0
df['ratings'] = df['ratings'].replace(np.nan, 0)

# Convertimos la columna de fecha a formato datetime
df['date'] = pd.to_datetime(df['date'], errors='coerce')

# Extraemos componentes temporales 
df['order_year'] = df['date'].dt.year
df['order_month'] = df['date'].dt.month
df['order_day_name'] = df['date'].dt.day_name()

# Aseguramos que los IDs sean tratados como str
df['transaction_id'] = df['transaction_id'].astype(str)
df['customer_id'] = df['customer_id'].astype(str)

# Usamos np.where para corregir montos negativos que podrían ser errores
df['amount'] = np.where(df['amount'] < 0, np.abs(df['amount']), df['amount'])

# Redondeamos las columnas monetarias a 2 decimales 
df['amount'] = np.round(df['amount'], 2)
df['total_amount'] = np.round(df['total_amount'], 2)

# Tratamiento de valores atipicos 
upper_limit = np.percentile(df['total_amount'].dropna(), 99)
df['total_amount_clean'] = np.clip(df['total_amount'], a_min=None, a_max=upper_limit)


# Clasificamos clientes por edad 
age_conditions = [
    (df['age'] < 20),
    (df['age'] >= 20) & (df['age'] < 40),
    (df['age'] >= 40) & (df['age'] < 60),
    (df['age'] >= 60)
]
age_labels = ['Gen Z', 'Millennial', 'Gen X', 'Senior']
df['age_group'] = np.select(age_conditions, age_labels, default='Other')

# Creamos una métrica de rentabilidad simple
df['high_ticket_order'] = np.where(df['total_amount'] > 500, 'Yes', 'No')

# Verificamos que Total_Amount sea coherente (Quantity * Amount)
# Si hay discrepancia, lo recalculamos 
df['total_amount_verified'] = df['total_purchases'] * df['amount']
df['data_alert'] = np.where(df['total_amount'] != df['total_amount_verified'], 1, 0)

# Ordenamos el dataset por fecha para una línea de tiempo coherente
df = df.sort_values(by='date')

# Eliminamos duplicados
df = df.drop_duplicates(subset=['transaction_id'])

# Seleccionamos solo las columnas necesarias para el reporte final
columns_to_keep = [
    'transaction_id', 'customer_id', 'city', 'state', 'country', 
    'age', 'gender', 'income', 'customer_segment', 'date', 
    'order_year', 'order_month', 'order_day_name', 'total_purchases', 
    'amount', 'total_amount', 'product_category', 'product_brand', 
    'product_type', 'feedback', 'shipping_method', 'payment_method', 
    'order_status', 'ratings', 'age_group', 'high_ticket_order'
]

df_final = df[columns_to_keep]

# Exportamos el archivo limpio listo para importar en Power BI
df_final.to_csv('retail_data_for_powerbi.csv', index=False)

# Mensaje de confirmacion 
print("Limpieza completada exitosamente. Archivo generado: retail_data_for_powerbi.csv")
