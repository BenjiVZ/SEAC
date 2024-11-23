from flask import session, render_template, send_file
import pandas as pd
import tempfile
import os
import pythoncom
import win32com.client
from datetime import datetime
import io
import logging

# Importar desde config.py en lugar de app.py
from config import VBA_CODE, insert_vba_code

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def procesar_archivo_vba(file, sheet_name):
    """Procesa el archivo con VBA y retorna la ruta del archivo temporal y mensajes"""
    messages = []
    temp_dir = tempfile.mkdtemp()
    temp_path = os.path.join(temp_dir, 'temp_vba.xlsx')
    file.save(temp_path)
    
    pythoncom.CoInitialize()
    excel = None
    try:
        excel = win32com.client.Dispatch("Excel.Application")
        excel.Visible = False
        excel.DisplayAlerts = False
        
        workbook = excel.Workbooks.Open(temp_path)
        insert_vba_code(workbook)
        
        # Ejecutar macros y capturar mensajes
        excel.Application.Run("DesvincularCeldas", sheet_name)
        messages.append("Todas las celdas vinculadas han sido desvinculadas y sus valores copiados.")
        
        excel.Application.Run("TabularInformacionCorregido", sheet_name)
        messages.append("Información tabulada correctamente en 'Tabla Tabulada'.")
        
        workbook.Save()
        workbook.Close()
        return True, messages, temp_path
    except Exception as e:
        return False, [str(e)], None
    finally:
        if excel:
            excel.Quit()
        pythoncom.CoUninitialize()

def procesar_pandas_automatico(file_path):
    """Procesa el archivo Excel con pandas"""
    df = pd.read_excel(file_path, sheet_name='Tabla Tabulada')
    df = df.dropna(subset=['N° de Local', 'Nombre', 'Apertura', 'Cierre'])
    df = df.drop_duplicates(subset=['N° de Local', 'Nombre', 'Apertura', 'Cierre', 'Día Semana 1', 'Fecha 1'])
    df['Fecha 1'] = pd.to_datetime(df['Fecha 1'], errors='coerce')
    df = df.dropna(subset=['Fecha 1'])
    df['Fecha 1'] = df['Fecha 1'].dt.strftime('%d-%m-%Y')
    return df

def guardar_df_temporal(df, suffix=''):
    """Guarda un DataFrame en un archivo temporal y retorna la ruta"""
    temp_dir = tempfile.mkdtemp()
    temp_path = os.path.join(temp_dir, f'temp_{suffix}.csv')
    df.to_csv(temp_path, index=False, encoding='cp1252')
    return temp_path

def limpiar_datos_adicionales_automatico(file_path):
    """Limpia datos adicionales del DataFrame"""
    df = pd.read_csv(file_path, encoding='cp1252')
    columnas_a_eliminar = ['Fecha 2', 'Día Semana 2']
    df = df.drop(columns=[col for col in columnas_a_eliminar if col in df])
    
    for columna in ['Fecha 1']:
        df[columna] = pd.to_datetime(df[columna], format='%d-%m-%Y', errors='coerce').dt.strftime('%Y-%m-%d')
    
    def convertir_a_hora(valor):
        try:
            valor_str = f"{int(valor):04d}"
            return f"{valor_str[:2]}:{valor_str[2:]}"
        except (ValueError, TypeError):
            return valor
    
    for columna in ['Apertura', 'Cierre']:
        df[columna] = df[columna].apply(convertir_a_hora)
    
    return df

def convertir_a_csv_automatico(file_path):
    """Convierte el archivo a CSV"""
    df = pd.read_csv(file_path, encoding='cp1252')
    temp_dir = tempfile.mkdtemp()
    temp_path = os.path.join(temp_dir, 'temp_converted.csv')
    df.to_csv(temp_path, index=False, encoding='cp1252')
    return temp_path

def tabular_por_dias_automatico(file_path, month, feriados):
    """Tabula los datos por días"""
    df = pd.read_csv(file_path, encoding='cp1252')
    selected_month = datetime.strptime(month, '%Y-%m')
    df['Fecha 1'] = pd.to_datetime(df['Fecha 1'])
    df = df[(df['Fecha 1'].dt.year == selected_month.year) & 
            (df['Fecha 1'].dt.month == selected_month.month)]
    
    dias_semana = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
    feriados = [datetime.strptime(f, '%Y-%m-%d').date() if f else None for f in feriados if f]
    
    result_dfs = []
    for _, row in df.iterrows():
        fecha = row['Fecha 1']
        if fecha.date() in feriados:
            row = row.copy()
            row['Día'] = 'Feriado'
        else:
            row = row.copy()
            row['Día'] = dias_semana[fecha.weekday()]
        result_dfs.append(row)
    
    return pd.DataFrame(result_dfs)

def configurar_gourmet_automatico(file_path, tiendas_gourmet):
    """Configura las tiendas gourmet y retorna el DataFrame final"""
    logger.debug(f"Iniciando configuración gourmet con archivo: {file_path}")
    logger.debug(f"Tiendas gourmet seleccionadas: {tiendas_gourmet}")

    try:
        # Debug: ver los primeros bytes del archivo
        with open(file_path, 'rb') as f:
            print("Primeros bytes del archivo:", f.read(100))

        # Leer el archivo con encoding específico
        df = pd.read_csv(file_path, encoding='cp1252')
        
        # Si llegamos aquí, la lectura fue exitosa
        logger.debug("Archivo leído exitosamente")
        
        # Verificar que tenemos las columnas necesarias
        if 'Nombre' not in df.columns or 'Día' not in df.columns:
            raise ValueError("El archivo no contiene las columnas requeridas (Nombre y Día)")
            
        # Imprimir información de debug
        logger.debug(f"Columnas en el DataFrame: {df.columns.tolist()}")
        logger.debug(f"Primeras filas del DataFrame:\n{df.head()}")
        
        # Separar registros de feriados
        df_feriados = df[df['Día'] == 'Feriado'].copy()
        df_no_feriados = df[df['Día'] != 'Feriado'].copy()
        
        # Para los no feriados, marcar las tiendas gourmet
        df_normal = df_no_feriados[~df_no_feriados['Nombre'].isin(tiendas_gourmet)].copy()
        df_gourmet = df_no_feriados[df_no_feriados['Nombre'].isin(tiendas_gourmet)].copy()
        df_gourmet['Día'] = 'Especial'
        
        # Concatenar todos los DataFrames
        df_final = pd.concat([df_normal, df_feriados, df_gourmet], ignore_index=True)
        
        # Asegurarse de que todas las columnas estén presentes
        logger.debug(f"Columnas en el DataFrame final: {df_final.columns.tolist()}")
        logger.debug(f"Número total de filas: {len(df_final)}")
        
        return df_final
        
    except Exception as e:
        logger.error(f"Error en configurar_gourmet_automatico: {str(e)}")
        logger.error(f"Archivo: {file_path}")
        logger.error(f"Tiendas gourmet: {tiendas_gourmet}")
        raise

def limpiar_archivos_temporales(session):
    """Limpia todos los archivos temporales almacenados en la sesión"""
    for key in ['temp_file', 'temp_file_pandas', 'temp_file_limpio', 
                'temp_file_csv', 'temp_file_tabulado']:
        if key in session:
            try:
                os.remove(session[key])
                os.rmdir(os.path.dirname(session[key]))
                del session[key]
            except (OSError, KeyError):
                pass