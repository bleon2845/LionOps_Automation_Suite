"""
Created on Thu Apr 10 13:38:38 2025

@author: bleonpar
"""

# %% Celda 1
import pandas as pd
import numpy as np
import calendar
from datetime import datetime
import sys
import tkinter as tk
from tkinter import filedialog, messagebox


# ---------------------- CARGAR ARCHIVOS CON VENTANA  ----------------------
#def cargar_excel_con_error(ruta, archivo_nombre, hoja=None):
#    try:
#        if hoja:
#            df = pd.read_excel(ruta, sheet_name=hoja)
#        else:
#            df = pd.read_excel(ruta)
#        return df
#    except Exception as e:
#        root = tk.Tk()
#        root.withdraw()
#        hoja_msg = f", hoja "{hoja}"" if hoja else ""
#        messagebox.showerror(
#            "Error al cargar archivo",
#            f"Error cargando "{archivo_nombre}"{hoja_msg}:\n{e}"
#        )
#        root.destroy()
#        return None

#def solicitar_archivos():
#    archivos_requeridos = [
#        ("Base Activos - Retirados Meli.xlsx", ["Activo", "Retirado"]),
#        ("Conso_Nomina.xlsx", None),
#        ("Conso_PreNomina.xlsx", None),
#        ("Acumulado_Mes.xlsx", None),
#        ("Agrupaciones.xlsx", ["Agrupaciones"]),
#        ("Base Personal Nacional.xlsx", ["BD Personal DHL"])
#    ]

#    archivos_seleccionados = {}

#    root = tk.Tk()
#    root.withdraw()

#    for archivo_nombre, hojas in archivos_requeridos:
#        messagebox.showinfo("Seleccionar archivo", f"Por favor selecciona el archivo:\n{archivo_nombre}")
#        ruta = filedialog.askopenfilename(title=f"Selecciona {archivo_nombre}",
#                                          filetypes=[("Archivos Excel", "*.xlsx *.xls")])
#        if not ruta:
#            messagebox.showerror("Error", f"No seleccionaste el archivo: {archivo_nombre}")
#            root.destroy()
#            return None
#        archivos_seleccionados[archivo_nombre] = ruta

#    root.destroy()
#    return archivos_seleccionados


 #Solicitar archivos
#rutas = solicitar_archivos()

#if rutas:
    # Cargar dataframes individualmente con manejo de error
#    df_activos = cargar_excel_con_error(rutas["Base Activos - Retirados Meli.xlsx"], "Base Activos - Retirados Meli.xlsx", "Activo")
#    df_retirados = cargar_excel_con_error(rutas["Base Activos - Retirados Meli.xlsx"], "Base Activos - Retirados Meli.xlsx", "Retirado")
#    df_consoNomina = cargar_excel_con_error(rutas["Conso_Nomina.xlsx"], "Conso_Nomina.xlsx")
#    df_preNomina = cargar_excel_con_error(rutas["Conso_PreNomina.xlsx"], "Conso_PreNomina.xlsx")
#    df_acumulado = cargar_excel_con_error(rutas["Acumulado_Mes.xlsx"], "Acumulado_Mes.xlsx")
#    df_agrp = cargar_excel_con_error(rutas["Agrupaciones.xlsx"], "Agrupaciones.xlsx", "Agrupaciones")
#    df_personalNacional = cargar_excel_con_error(rutas["Base Personal Nacional.xlsx"], "Base Personal Nacional.xlsx", "BD Personal DHL")

    
#    dfs = [df_activos, df_retirados, df_consoNomina, df_preNomina, df_acumulado, df_agrp, df_personalNacional]
#    if any(df is None for df in dfs):
 #       print("Hubo errores cargando uno o más archivos.")
  #  else:
   #     print("Todos los archivos cargados correctamente.")
#else:
    #print("No se seleccionaron todos los archivos necesarios.")


#--------------- FUNCION PARA LEER ARCHIVOS --------------- 
def cargar_excel(path, sheet=None):
    try:
        if sheet:
            return pd.read_excel(path, sheet_name=sheet)
        else:
            return pd.read_excel(path)
    except Exception as e:
        # Crear ventana de Tkinter para mostrar error
        root = tk.Tk()
        root.withdraw()  # Oculta la ventana principal
        mensaje = f"❌ Error al cargar '{path}'" + (f", hoja '{sheet}'" if sheet else "") + f":\n{e}"
        messagebox.showerror("Error al cargar archivo Excel", mensaje)
        root.destroy()
        sys.exit(1)  # Detener el script con código de error 1

df_activos = cargar_excel("Base Activos - Retirados Meli.xlsx", sheet="Activo")
df_retirados = cargar_excel("Base Activos - Retirados Meli.xlsx", sheet="Retirado")
df_consoNomina = cargar_excel("Conso_Nomina.xlsx")
df_preNomina = cargar_excel("Conso_PreNomina.xlsx")
df_acumulado = cargar_excel("Acumulado_Mes.xlsx")
df_agrp = cargar_excel("Agrupaciones.xlsx", sheet="Agrupaciones")
df_personalNacional = cargar_excel("Base Personal Nacional.xlsx", sheet="BD Personal DHL")

#--------------- FUNCION PARA VALIDAR COLUMNAS Y MAYUS -------------
def validar_columnas(df, columnas_requeridas, nombre_df):
    # Convert both lists to uppercase for validation only
    columnas_actuales_upper = [col.upper() for col in df.columns]
    columnas_requeridas_upper = [col.upper() for col in columnas_requeridas]

    # Find missing ones
    faltantes = [col for col in columnas_requeridas_upper if col not in columnas_actuales_upper]

    if faltantes:
        mensaje = f"❌ Faltan columnas en \"{nombre_df}\": {', '.join(faltantes)}"
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Error de Columnas", mensaje)
        root.destroy()
        sys.exit(1)

# Validar columnas en cada DataFrame
validar_columnas(df_activos, ["CEDULA", "NOMBRE DEL PUESTO", "FECHA DE INGRESO", "SALARIO MENSUAL"], "Base Activos - Retirados Meli")
validar_columnas(df_retirados, ["CEDULA", "NOMBRE DEL PUESTO", "FECHA DE INGRESO", "FECHA DE BAJA"], "Base Activos - Retirados Meli")
validar_columnas(df_consoNomina, ["CEDULA", "CARGO NOMINA", "SALARIO BASICO"], "Conso_Nomina")
validar_columnas(df_preNomina, ["Cedula", "Basico"], "Conso_PreNomina")
validar_columnas(df_personalNacional, ["OPERACION","ID", "CARGO NÓMINA", "FECHA DE INGRESO", "FECHA DE RETIRO"], "Base Personal Nacional")
validar_columnas(df_agrp, ["CONCEPTO", "DESCRIPCION", "AGRUPACION"], "Agrupaciones")
validar_columnas(df_acumulado, ["NÓMINA", "PROCESO", "AÑO PROCESO", "PERIODO PROCESO", "MES PROCESO",
                                "NUMERO DOCUMENTO", "PRIMER APELLIDO", "SEGUNDO APELLIDO", "NOMBRES",
                                "CONCEPTO", "DESCRIPCIÓN", "CANTIDAD", "MONTO","NETO", "SMRU"], "Acumulado_Mes")

#--------------- FUNCION PARA CONFIRMAR SMLV -------------
def solicitar_salario():
    salario_valor = None  # Por defecto None

    def validar_entrada(texto):
        return texto.isdigit() or texto == ""

    def confirmar():
        nonlocal salario_valor
        salario = entry.get()
        if not salario.isdigit() or salario == "":
            messagebox.showerror("Error", "Debe ingresar solo números.")
            return
        
        salario_valor = int(salario)
        respuesta = messagebox.askyesnocancel(
            "Confirmar",
            f"¿Desea confirmar que el SMLV es de: {salario_valor}?"
        )
        
        if respuesta is True:
            messagebox.showinfo("Confirmado", f"El SMLV ha sido confirmado en {salario_valor}.")
            root.destroy()
        elif respuesta is False:
            salario_valor = None
            root.destroy()
        else:
            pass

    root = tk.Tk()
    root.title("Ingreso SMLV")

    tk.Label(root, text="Ingrese el salario mínimo:").pack(pady=5)

    vcmd = (root.register(validar_entrada), "%P")
    entry = tk.Entry(root, validate="key", validatecommand=vcmd)
    entry.pack(pady=5)

    tk.Button(root, text="Aceptar", command=confirmar).pack(pady=10)

    root.mainloop()
    return salario_valor


salario = solicitar_salario()



#--------------- FUNCION PARA MERGE ENTRE DF"s ---------------
def fusionar_dataframes(df_izquierdo, df_derecho, col_izq, col_der, como, nombre_union):
    df_resultado = pd.merge(
        left=df_izquierdo,
        right=df_derecho,
        how=como,
        left_on=col_izq,
        right_on=col_der
    )
    return df_resultado

#--------------- FUNCION PARA ELIMINAR OBJETOS Y VARIBALES ---------------
def eliminar(objetivo, *nombres):
    if isinstance(objetivo, dict):
        for nombre in nombres:
            if nombre in objetivo:
                del objetivo[nombre]
    elif hasattr(objetivo, "drop") and hasattr(objetivo, "columns"):
        for nombre in nombres:
            if nombre in objetivo.columns:
                objetivo.drop(columns=nombre, inplace=True)
        return objetivo

#--------------- CREAR VARIABLES DE NOMBRE MES ACTUAL Y ANTERIOR ---------------
""" Lista de meses en texto """
meses = [
    "ENERO", "FEBRERO", "MARZO", "ABRIL",
    "MAYO", "JUNIO", "JULIO", "AGOSTO",
    "SEPTIEMBRE", "OCTUBRE", "NOVIEMBRE", "DICIEMBRE"
]

# Obtener número de mes actual desde la primera fila
nMesActual = int(df_acumulado["Mes proceso"].iloc[0])

# Calcular mes anterior
nMesAnterior = nMesActual - 1 if nMesActual > 1 else 12

# Obtener nombres de mes usando la lista
nombreMesActual = meses[nMesActual - 1]
nomMesAnterior = meses[nMesAnterior - 1]
nomMesIBC = meses[nMesAnterior - 2]

# Crear variables de corte de nómina
corteNomina1 = "1Q " + nomMesAnterior
corteNomina2 = "2Q " + nomMesAnterior

#--------------- FILTRAR DATAFRAMES Y DEJAR COLUMNAS NECESARIAS ---------------
""" Filtrar ConsoNomina y PreNomina con Mes Anterior """
df_consoNomina = df_consoNomina[df_consoNomina["MES"] == nomMesAnterior]
df_preNomina = df_preNomina[df_preNomina["Periodo"].isin([corteNomina1, corteNomina2])]


""" Dejar columnas necesarias """
df_activos = df_activos[["CEDULA", "NOMBRE DEL PUESTO", "FECHA DE INGRESO", "SALARIO MENSUAL"]]
df_retirados = df_retirados[["CEDULA", "NOMBRE DEL PUESTO", "FECHA DE INGRESO", "FECHA DE BAJA", ]]
df_consoNomina = df_consoNomina[["CEDULA", "CARGO NOMINA", "SALARIO BASICO"]]
df_preNomina = df_preNomina[["Cedula", "Basico"]]
df_personalNacional = df_personalNacional[["OPERACION","ID", "CARGO NÓMINA", "FECHA DE INGRESO", "FECHA DE RETIRO"]]

""" Crear columna """
df_activos["FECHA DE BAJA"] = "1990-01-01 00:00:00"

#--------------- CONSOLIDAR DATA DE EMPLEADOS ACTIVOS RETIRADOS ---------------
""" Cruzar con archivos consolidados para traer Salario """
df_retirados = fusionar_dataframes(
    df_izquierdo=df_retirados,
    df_derecho=df_consoNomina,
    col_izq="CEDULA",
    col_der="CEDULA",
    como="left",
    nombre_union="Retirados vs ConsoNomina"
)

df_retirados = fusionar_dataframes(
    df_izquierdo=df_retirados,
    df_derecho=df_preNomina,
    col_izq="CEDULA",
    col_der="Cedula",
    como="left",
    nombre_union="Retirados vs PreNomina"
)


""" Eliminar columna no necesaria """
df_retirados = eliminar(df_retirados, "CARGO NOMINA")

""" Eliminar duplicados dejando el primer registro """
df_retirados = df_retirados.drop_duplicates(subset="CEDULA", keep="first")

""" Crear columna salario """
df_retirados["SALARIO MENSUAL"] = df_retirados["SALARIO BASICO"].where(df_retirados["SALARIO BASICO"] != "", df_retirados["Basico"])

""" Actualizar columna Salario Mensual si es nan """
df_retirados.loc[
    df_retirados["SALARIO BASICO"].isna(), "SALARIO MENSUAL"
] = df_retirados["Basico"]


""" Eliminar Columnas """
df_retirados = eliminar(df_retirados, "SALARIO BASICO", "Basico","Cedula")

""" Eliminar Variable """
eliminar(globals(), "df_preNomina")

""" Ordenar archivo de activos """
df_activos = df_activos[["CEDULA", "NOMBRE DEL PUESTO", "FECHA DE INGRESO", "FECHA DE BAJA", "SALARIO MENSUAL"]]

""" Concatenar dataframes """
df_activos = pd.concat([df_activos, df_retirados], axis=0)

"""Eliminar variable """
eliminar(globals(), "df_retirados")


# -------------- UNIR BASES NACIONAL AMERICAS Y FUNZA  ---------------
""" Cargar excel de Funza """
df_personalNacionalFunza = cargar_excel("Planta de personal DHL.xlsx", sheet="RETIRADOS")

""" Crear columnas con 0 """
df_personalNacionalFunza["OPERACION"] = "Funza"

""" Dejar columnas necesarias """
df_personalNacionalFunza = df_personalNacionalFunza[["OPERACION", "CEDULA", "CARGO DHL", "FECHA INGRESO", "FECHA RETIRO"]]

""" Cambiar nombre de columnas"""
df_personalNacionalFunza = df_personalNacionalFunza.rename(columns={
    "CEDULA": "ID",
    "CARGO DHL": "CARGO NÓMINA",
    "FECHA INGRESO": "FECHA DE INGRESO",
    "FECHA RETIRO": "FECHA DE RETIRO"
})

""" eliminar duplicados de base nacional """
df_personalNacional = df_personalNacional.drop_duplicates(subset=["ID"], keep="last")
df_personalNacionalFunza = df_personalNacionalFunza.drop_duplicates(subset=["ID"], keep="last")

""" Consolidar archivos de perosnal nacional americas y funza """
df_personalNacional = pd.concat([df_personalNacional, df_personalNacionalFunza], axis=0)

# --------------- ELIMINAR DUPLICADOS DE BASE NACIONAL Y RETIRADOS -----------
""" Eiliminar filas sin fechas validas """
df_personalNacionalRetirados = df_personalNacional[df_personalNacional["FECHA DE RETIRO"] != "1990-01-01 00:00:00"]

""" Ordenar el df de manera ascendente """
df_personalNacionalRetirados = df_personalNacionalRetirados.sort_values(by="FECHA DE RETIRO", ascending=True)
df_personalNacional = df_personalNacional.sort_values(by="FECHA DE RETIRO", ascending=True)

""" Eliminar duplicado y dejar último registro """
df_personalNacionalRetirados = df_personalNacionalRetirados.drop_duplicates(subset=["ID"], keep="last")
df_personalNacional = df_personalNacional.drop_duplicates(subset=["ID"], keep="last")

#--------------- VERIFICAR CARGO FECHAS DE INGRESO Y RETIRO DE EMPLEADOS ---------------

""" Merge Activos vs Personal Nacional """
df_activos = fusionar_dataframes(
    df_izquierdo=df_activos,
    df_derecho=df_personalNacionalRetirados,
    col_izq="CEDULA",
    col_der="ID",
    como="left",
    nombre_union="Activos vs Base Personal Nacional"
)


""" Eliminar Columnas """
df_activos = eliminar(df_activos, "CARGO NÓMINA", "OPERACION", "CARGO MELI")

""" Conservar datos de cargo hasta el . """
df_activos["NOMBRE DEL PUESTO"] = df_activos["NOMBRE DEL PUESTO"].str.split(".").str[1]

""" Actualizar fecha de ingreso y feha de baja """
df_activos["FECHA DE INGRESO_x"] = pd.to_datetime(df_activos["FECHA DE INGRESO_x"], errors="coerce")
df_activos["FECHA DE INGRESO_y"] = pd.to_datetime(df_activos["FECHA DE INGRESO_y"], errors="coerce")

fecha_vacia = "1990-01-01 00:00:00"

""" Actualizar la columna fecha de baja """
condicion = (
    (df_activos["FECHA DE BAJA"].isna()) |
    (df_activos["FECHA DE BAJA"] == fecha_vacia)
)

df_activos.loc[condicion, "FECHA DE BAJA"] = df_activos.loc[condicion, "FECHA DE RETIRO"]

""" Actualizar la columna fecha de ingreso """
condicion = (
    (df_activos["FECHA DE INGRESO_x"].isna()) |
    (df_activos["FECHA DE INGRESO_x"] == fecha_vacia)
)

df_activos.loc[condicion, "FECHA DE INGRESO_x"] = df_activos.loc[condicion, "FECHA DE INGRESO_y"]

""" Eliminar Columnas """
df_activos = eliminar(df_activos, "FECHA DE INGRESO_y", "ID", "FECHA DE RETIRO")

""" Cambiar nombre de columnas """
df_activos = df_activos.rename(columns={
    "FECHA DE INGRESO_x": "FECHA DE INGRESO",
})

#-------------------- VERIFICAR ARCHIVO DE ACUMULADO MES --------------------
""" Merge para traer columna de salario"""
df_acumulado = fusionar_dataframes(
    df_izquierdo=df_acumulado,
    df_derecho=df_activos,
    col_izq="Numero Documento",
    col_der="CEDULA",
    como="left",
    nombre_union="Acumulado vs Base Activos"
)

""" Eliminar columnas """
df_acumulado = eliminar(df_acumulado, "CEDULA", "NOMBRE DEL PUESTO","FECHA DE BAJA", "FECHA DE INGRESO")

""" Crear columnas para verificar salario por dias """ 
df_acumulado["Salario Dia"] = df_acumulado["SALARIO MENSUAL"]/30
df_acumulado["Verificacion Dias Salario"] = df_acumulado["Neto"]/df_acumulado["Salario Dia"]

""" Lista de códigos permitidos """
lista_codigos_validos = [
    "D144", "D169", "D196",
    "P003", "P129", "P140", "P153",
    "P211", "P216", "P243", "P275", "P331", "P115", "P210",
    "D232", "P176"
]

""" filtrar donde se tengan los codigos indicados """
mascara_codigos = df_acumulado["Concepto"].isin(lista_codigos_validos)

""" Eliminar Variable"""
eliminar(globals(), "lista_codigos_validos")

""" Comparar las columnas como enteros """
cantidad = df_acumulado.loc[mascara_codigos, "Cantidad"].astype(float)
verificacion = df_acumulado.loc[mascara_codigos, "Verificacion Dias Salario"].astype(float)

""" Crear condición donde los valores sean diferentes """
mascara_actualizar = (
    mascara_codigos &
    (df_acumulado["Verificacion Dias Salario"] > 0) &
    (df_acumulado["SALARIO MENSUAL"] > 0) &
    (df_acumulado["Cantidad"] != df_acumulado["Verificacion Dias Salario"])
)

df_acumulado.loc[mascara_actualizar, "Cantidad"] = df_acumulado.loc[mascara_actualizar, "Verificacion Dias Salario"]

""" Crear lista de codigo para personal FT"""
lista_codigos_validos = [
    "P138", "P142", "P144", "P358"
]

"""" Crear masacara con codigod de perosnal FT"""
mascara_codigos_ft = df_acumulado["Concepto"].isin(lista_codigos_validos)

""" Eliminar Variable"""
eliminar(globals(), "lista_codigos_validos")

""" Actualizar columna con valores para personal FT """
mascara_actualizar = (
    mascara_codigos_ft &
    (df_acumulado["Verificacion Dias Salario"] > 0) &
    (df_acumulado["SALARIO MENSUAL"] > salario) &
    (df_acumulado["Cantidad"] != df_acumulado["Verificacion Dias Salario"])
)

df_acumulado.loc[mascara_actualizar, "Cantidad"] = df_acumulado.loc[mascara_actualizar, "Verificacion Dias Salario"]


""" Eliminar Columnas y variables"""
eliminar(globals(), "cantidad")
df_acumulado = eliminar(df_acumulado, "SALARIO MENSUAL", "Salario Dia","Verificacion Dias Salario")

""" Descargar reporte de acumulado verificados los días """
df_acumulado.to_excel("Acumulado_Mes_Verificado.xlsx")

#---------------- ARCHIVO CIFRAS DE CIERRE MELI O INTERFAZ --------------
""" Cambiar a Negativo Inasistencia o Suspension"""
conditionlist = [
    df_acumulado["Concepto"].str.contains("D196", na=False),
    df_acumulado["Concepto"].str.contains("D144", na=False)
]

choicelist = [
    df_acumulado["Cantidad"] * -1,
    df_acumulado["Cantidad"] * -1
]

df_acumulado["Total Dias"] = np.select(conditionlist, choicelist, default=df_acumulado["Cantidad"])

""" Pasar a mayusculas columnas del dataframe """
df_acumulado.columns = df_acumulado.columns.str.upper()

""" Concatenar nombres y apellidos """
df_acumulado["NOMBRE COMPLETO"] = df_acumulado["NOMBRES"]+" "+df_acumulado["PRIMER APELLIDO"]+" "+df_acumulado["SEGUNDO APELLIDO"]

""" Eliminar Columnas """
df_acumulado = eliminar(df_acumulado, "PRIMER APELLIDO", "SEGUNDO APELLIDO","NOMBRES",
                        "NÓMINA", "PROCESO", "PERIODO PROCESO", "NÚMERO EMPLEADO", "AÑO PROCESO", "CANTIDAD")

""" Leer archivo de cifras de cierre meli (Interfaz) """
df_cifrasMes = pd.read_excel("Cifras de cierre Meli.xlsx", sheet_name="Base")

""" Eliminar las fila diferente a NSELECT """
df_cifrasMes = df_cifrasMes[df_cifrasMes["COMPROBANTE"] != "NELECT  "]

""" Cambiar nombre de columnas """
df_cifrasMes = df_cifrasMes.rename(columns={
    "CEDULA": "NUMERO DOCUMENTO",
    "NOMBRE": "NOMBRE COMPLETO",
    "NOMBRE_CONCEPTO": "DESCRIPCIÓN",
    "NETO": "MONTO",
    "MES": "MES PROCESO"
})

""" Crear Columna que no se tienen en el dataframe """
df_cifrasMes["CANTIDAD"] = 0
df_cifrasMes["NETO"] = df_cifrasMes["MONTO"]
df_cifrasMes["TOTAL DIAS"] = 0

""" Eliminar cuentas que empiezan con 4 """
df_cifrasMes = df_cifrasMes[df_cifrasMes["CUENTA"].astype(str).str.startswith("4")]

""" Ordenar archivo de cifras mes igual a acumulado """
orden_columnas = ["MES PROCESO","NUMERO DOCUMENTO", "CONCEPTO", "DESCRIPCIÓN", "CANTIDAD", "MONTO", "NETO", "SMRU","TOTAL DIAS", "NOMBRE COMPLETO"]
df_cifrasMes = df_cifrasMes[orden_columnas]

""" Eliminar variable """
eliminar(globals(), "orden_columnas")

""" Consolidar archivos de acumulado y cifras """
df_acumulado = pd.concat([df_acumulado, df_cifrasMes], axis=0)

""" Eliminar repetidos de columna Cedula """
df_activos = df_activos.drop_duplicates(subset=["CEDULA"])

#----------- CRUZAR NOMINA MES CON DATOS DE EMPLEADOS ACTIVOS -----------
""" Merge Traer Columna de ingreso, retiro, salario y cargo """
df_acumulado = fusionar_dataframes(
    df_izquierdo=df_acumulado,
    df_derecho=df_activos,
    col_izq="NUMERO DOCUMENTO",
    col_der="CEDULA",
    como="left",
    nombre_union="Acumulado vs Base Activos"
)

""" Eliminar Columna y Variable """
df_acumulado = eliminar(df_acumulado, "CEDULA")
eliminar(globals(), "df_activos")

#--------------- CRUZAR NOMINA CON BASE NACIONAL DE PERSONAL --------------
""" Merge Acumulado vs Base Nacional de Personal para traer cargo faltante """
df_acumulado = fusionar_dataframes(
    df_izquierdo=df_acumulado,
    df_derecho=df_personalNacional,
    col_izq="NUMERO DOCUMENTO",
    col_der="ID",
    como="left",
    nombre_union="Acumulado vs Base Personal Nacional"
)

""" Modificar a datetime las columnas """
df_acumulado["FECHA DE BAJA"] = pd.to_datetime(df_acumulado["FECHA DE BAJA"], errors="coerce")
df_acumulado["FECHA DE RETIRO"] = pd.to_datetime(df_acumulado["FECHA DE RETIRO"], errors="coerce")

""" Actualizar los datos de nombre de puesto """
df_acumulado["NOMBRE DEL PUESTO"] = df_acumulado["NOMBRE DEL PUESTO"].fillna(df_acumulado["CARGO NÓMINA"])
df_acumulado["FECHA DE INGRESO_x"] = df_acumulado["FECHA DE INGRESO_x"].fillna(df_acumulado["FECHA DE INGRESO_y"])
df_acumulado["FECHA DE BAJA"] = df_acumulado["FECHA DE BAJA"].fillna(df_acumulado["FECHA DE RETIRO"])

""" Eliminar Columnas """
df_acumulado = eliminar(df_acumulado, "CARGO NÓMINA", "ID", "FECHA DE INGRESO_y", "FECHA DE RETIRO", "OPERACION")

""" Cambiar el nombre de la columna Fecha de ingreso """
df_acumulado = df_acumulado.rename(columns={
    "FECHA DE INGRESO_x": "FECHA DE INGRESO",
})

#------------------------- CREAR COLUMNAS EN NOMINA ----------------------
""" Actualizar columna de Centro de Costos """
conditionlist = [
    (df_acumulado["SMRU"] == "COL - MERCADO LIBRE - Funza Zol - WHS."),
    (df_acumulado["SMRU"] == "COL - MERCADO LIBRE - Btá Americas - WHS"),
    (df_acumulado["SMRU"] == "COL - MERCADO LIBRE - Cortijo 9 - WHS."),
    (df_acumulado["SMRU"] == "COL - MERCADO LIBRE - Medellin Olaya - WHS."),
    (df_acumulado["SMRU"] == "COL - MERCADO LIBRE - Giron In House - WHS."),
    (df_acumulado["SMRU"] == "COL - MERCADO LIBRE - Pereira In House - WHS."),
    (df_acumulado["SMRU"] == "COL - MERCADO LIBRE - Tunja In House - WHS."),
    (df_acumulado["SMRU"] == "COL - MERCADO LIBRE - Ibague In House - WHS."),
    (df_acumulado["SMRU"] == "COL - MERCADO LIBRE - Estrella  In House - WHS"),
    (df_acumulado["SMRU"] == "COL - MERCADO LIBRE -Funza Zol -WHS"),
    ]
choicelist = ["6563","6571", "1980", "6567", "5641", "5358", "5359", "5840", "5421", "1111"]
df_acumulado["CENTRO DE COSTOS"] = np.select(conditionlist, choicelist, default="N/A")

""" Actualizar columna de Nombre Centro de Costos """
conditionlist = [
    (df_acumulado["SMRU"] == "COL - MERCADO LIBRE - Funza Zol - WHS."),
    (df_acumulado["SMRU"] == "COL - MERCADO LIBRE - Btá Americas - WHS"),
    (df_acumulado["SMRU"] == "COL - MERCADO LIBRE - Cortijo 9 - WHS."),
    (df_acumulado["SMRU"] == "COL - MERCADO LIBRE - Medellin Olaya - WHS."),
    (df_acumulado["SMRU"] == "COL - MERCADO LIBRE - Giron In House - WHS."),
    (df_acumulado["SMRU"] == "COL - MERCADO LIBRE - Pereira In House - WHS."),
    (df_acumulado["SMRU"] == "COL - MERCADO LIBRE - Tunja In House - WHS."),
    (df_acumulado["SMRU"] == "COL - MERCADO LIBRE - Ibague In House - WHS."),
    (df_acumulado["SMRU"] == "COL - MERCADO LIBRE - Estrella  In House - WHS"),
    (df_acumulado["SMRU"] == "COL - MERCADO LIBRE -Funza Zol -WHS"),
    ]
choicelist = ["FUNZA ZOL","BTA AMERICAS", "CORTIJO 9", "MEDELLIN OLAYA", "GIRON IN HOUSE",
              "PEREIRA IN HOUSE", "TUNJA IN HOUSE", "IBAGUE IN HOUSE",
              "Estrella  In House", "SVC FUNZA"]
df_acumulado["NOMBRE CENTRO DE COSTOS"] = np.select(conditionlist, choicelist, default="N/A")

""" Actualizar columna de Poblacion """
conditionlist = [
    (df_acumulado["SMRU"] == "COL - MERCADO LIBRE - Funza Zol - WHS."),
    (df_acumulado["SMRU"] == "COL - MERCADO LIBRE - Btá Americas - WHS"),
    (df_acumulado["SMRU"] == "COL - MERCADO LIBRE - Cortijo 9 - WHS."),
    (df_acumulado["SMRU"] == "COL - MERCADO LIBRE - Medellin Olaya - WHS."),
    (df_acumulado["SMRU"] == "COL - MERCADO LIBRE - Giron In House - WHS."),
    (df_acumulado["SMRU"] == "COL - MERCADO LIBRE - Pereira In House - WHS."),
    (df_acumulado["SMRU"] == "COL - MERCADO LIBRE - Tunja In House - WHS."),
    (df_acumulado["SMRU"] == "COL - MERCADO LIBRE - Ibague In House - WHS."),
    (df_acumulado["SMRU"] == "COL - MERCADO LIBRE - Estrella  In House - WHS"),
    (df_acumulado["SMRU"] == "COL - MERCADO LIBRE -Funza Zol -WHS"),
    ]
choicelist = ["FUNZA","BOGOTA", "YUMBO", "MEDELLIN", "GIRON",
              "PEREIRA", "TUNJA", "IBAGUE", "MEDELLIN", "SVC FUNZA"]
df_acumulado["POBLACIÓN"] = np.select(conditionlist, choicelist, default="N/A")

""" Eliminar Variables """
eliminar(globals(), "choicelist", "conditionlist")

""" Crear columna con nombre correcto """
df_acumulado["CARGO NOMINA"] = df_acumulado["NOMBRE DEL PUESTO"]

""" Eliminar Columna """
df_acumulado = eliminar(df_acumulado, "NOMBRE DEL PUESTO")

#----------- CRUZAR NOMINA CON AGRUPACIONES DE CUENTAS CONTABLES ---------
""" Merge Acumulado vs Agrupaciones """
df_acumulado = fusionar_dataframes(
    df_izquierdo=df_acumulado,
    df_derecho=df_agrp,
    col_izq="CONCEPTO",
    col_der="CONCEPTO",
    como="left",
    nombre_union="Acumulado vs Base Agrupaciones"
)

""" Eliminar agrupaciones diferentes a NO APLICA """
df_acumulado = df_acumulado[df_acumulado["AGRUPACION"] != "NO APLICA"]

""" Eliminar Variable """
eliminar(globals(), "df_agrp")

""" Actuaizar a negativo los valores para cuentas que empizan con D """
df_acumulado["TOTAL"] = df_acumulado.apply(
    lambda fila: fila["MONTO"] * -1 
    if str(fila["CONCEPTO"]).startswith("D")
    else fila["MONTO"],
    axis=1
)


# --------------- FUNCION PARA CREAR COLUMNAS CON SUMA DE DESCRIPCIONES ---------------
""" Actualizar el concepto P333 con AJUS SALARIO """
df_acumulado.loc[df_acumulado["CONCEPTO"] == "P333", "DESCRIPCION"] = "AJUS SALARIO"

diccionario = {
    "SUELDO BASICO": "DIAS_SUELDO_BASICO",
    "DÍA FAMILIAR": "DIAS_FAMILIAR",
    "SANCION / SUSPENSION": "DIAS_SANCION_/_SUSPENSION",
    "LICENCIA NO REMUN": "DIAS_LICENCIA_NO_REMUN",
    "INASISTENCIA INJUST": "DIAS_INASISTENCIA_INJUST",
    "VACACIONES": "DIAS_VACACIONES",
    "VACACIONES FESTIVAS": "DIAS_VACACIONES_FESTIVAS",
    "VACACIONES EN DINERO": "DIAS_VACACIONES_DINERO",
    "GASTO INCAPACIDAD": "DIAS_GASTO_INCAPACIDAD",
    "LIC LEY MARIA 8 DIAS": "DIAS_LIC_LEY_MARIA_8_DIAS",
    "INCAPACIDAD ACC TRAB": "DIAS_INCAPACIDAD_ACC_TRAB",
    "INCAP ENFERMEDAD GEN": "DIAS_INCAP_ENFERMEDAD_GEN",
    "LICENCIA MATERNIDAD": "DIAS_LICENCIA_MATERNIDAD",
    "VAC HABILES SAL INT": "DIAS_VAC_HABILES_SAL_INT",
    "INCAPACIDAD AL 50%": "DIAS_INCAPACIDAD_AL_50%",
    "DÍA NO LAB DER A PAG": "DIAS_DÍA_NO_LAB_DER_A_PAG",
    "RTEGRO DTO INASISTEN": "DIAS_RTEGRO_DTO_INASISTEN",
    "AJS  LICENCIA MATERN": "DIAS_AJS_LICENCIA_MATERN",
    "INCAP ENF GEN PRORR": "DIAS_INCAP_ENF_GEN_PRORR",
    "DTO SALARIO": "DIAS_DTO_SALARIO",
    "INASIS X INC > 180 D": "DIAS_INASIS_X_INC_>_180_D",
    "DTO INC ENF GRAL AL": "DIAS_DTO_INC_ENF_GRAL_AL",
    "PERMISO JUSTIFICADO": "DIAS_PERMISO_JUSTIFICADO",
    "RETROACTIV SALARIO": "DIAS_RETROACTIV_SALARIO",
    "PERMISO PERSONAL": "DIAS_PERMISO_PERSONAL",
    "AJUS SALARIO": "DIAS_AJUS_SALARIO"
}

""" Funcion para crear columnas con suma de descripciones """
def calcular_sumas(df, diccionario, columna_filtro, columna_valor, asignar_primera_fila=False):
    resultados = []
    for num_doc, grupo in df.groupby("NUMERO DOCUMENTO"):
        fila = {"NUMERO DOCUMENTO": num_doc}
        for descripcion, columna in diccionario.items():
            suma = grupo.loc[grupo[columna_filtro] == descripcion, columna_valor].sum()
            fila[columna] = int(round(suma))
        resultados.append(fila)
    df_sumas = pd.DataFrame(resultados)

    for col in diccionario.values():
        if col not in df.columns:
            df[col] = None if asignar_primera_fila else 0

    if asignar_primera_fila:
        df["es_primera_fila"] = df.groupby("NUMERO DOCUMENTO").cumcount() == 0
        df = df.merge(df_sumas, on="NUMERO DOCUMENTO", how="left", suffixes=("", "_suma"))

        for col in diccionario.values():
            df[col] = df.apply(lambda row: int(row[f"{col}_suma"]) if row["es_primera_fila"] else None, axis=1)

        df.drop(columns=[f"{col}_suma" for col in diccionario.values()] + ["es_primera_fila"], inplace=True)

    else:
        df = df.merge(df_sumas, on="NUMERO DOCUMENTO", how="left", suffixes=("", "_suma"))

        for col in diccionario.values():
            df[col] = df[f"{col}_suma"].fillna(0).astype(int)
        df.drop(columns=[f"{col}_suma" for col in diccionario.values()], inplace=True)

    return df

""" Ejecutar funcion """
df_acumulado = calcular_sumas(df_acumulado, diccionario, "DESCRIPCION", "TOTAL DIAS", asignar_primera_fila=False)

# --------------- FUNCION PARA CREAR COLUMNAS CON SUMA DE AGRUPACIONES ---------------
""" Eliminar espacios en los textos de las agrupaciones """
df_acumulado["AGRUPACION"] = df_acumulado["AGRUPACION"].astype(str).str.strip()

""" Crear diccionario """
diccionario = {
    "SALARIO A PAGAR": "SALARIO_A_PAGAR",
    "SUBSIDIO DE TRANSPORTE": "SUBSIDIO_TRANSPORTE",
    "HE DIURNA - 1.25": "VR._HORA_EXTRA_DIURNA - 1,25",
    "HE NOCTURNA - 1.75": "VR._HORA_EXTRA_NOCTURNA - 1,75",
    "HRS. EXTRA HORA DOM/FEST. NOCTURNA 2.50%": "VR._EXTRA_HORA_DOM/FEST._NOCTURNA_2.50%",
    "HRS. HORA EXTRA DOMINICAL Y FESTIVA DIURNA 2.00%": "VR._HORA_EXTRA_DOMINICAL_Y_FESTIVA_DIURNA_2.00%",
    "HRS. DOMINICAL DIURNO - 1,75": "VR._DOMINICAL_DIURNO - 1,75",
    "FESTIVO DIURNO  1.75": "VR._FESTIVO_DIURNO - 1,75",
    "RECAR DOM NOCT - 2.1": "VR._RECARGO_DOMINICAL_NOCTURNO - 2,1",
    "RECARGO FESTIVO NOCTURNO - 2,1": "VR._RECARGO_FESTIVO_NOCTURNO - 2,1",
    "RECARGO NOCT - 0.35": "VR._RECARGO_NOCTURNO - 0,35",
    "REAJUSTE RECARGOS": "REAJUSTE_RECARGOS",
    "REAJUSTE H.E": "REAJUSTE_H.E",
    "REAJUSTE SALARIAL": "REAJUSTE_SALARIAL",
    "REAJUSTE AUSENCIAS JUSTIFICADAS": "REAJUSTE_AUSENCIAS_JUSTIFICADAS",
    "REAJUSTE VACACIONES": "REAJUSTE_VACACIONES",
    "DIAS AUSENCIAS JUSTIFICADAS SIN COBRO (Vac. Habiles, inc 66,67%)": "VALOR_AUSENCIAS_JUSTIFICADAS_SIN_COBRO_(Vac. Habiles, inc 66,67%)",
    "BONIFICACION NO CONSTITUTIVA DE SALARIO": "BONIFICACION_NO_CONSTITUTIVA_DE_SALARIO",
    "BONIFICACION SALARIAL": "BONIFICACION_SALARIAL",
    "TRANSPORTE EXTRALEGAL AUT. POR CL": "TRANSPORTE_EXTRALEGAL_AUT._POR_CL",
    "AUXILIO DE RODAMIENTO": "AUXILIO_DE_RODAMIENTO",
    "MAY. VALOR PAGADO EN SALARIO": "MAY._VALOR_PAGADO_EN_SALARIO",
    "MAY. VALOR PAGADO EN AUX. TRANS": "MAY._VALOR_PAGADO_EN_AUX._TRANS",
    "BENEFICIOS": "BENEFICIOS",
    "VACACIONES": "VACACIONES",
    "OTROS CONCEPTOS FACTURABLES PRESTACIONALES": "OTROS_CONCEPTOS_FACTURABLES_PRESTACIONALES",
    "SALUD": "SALUD_PATRONO",
    "PENSION": "PENSION_12%",
    "ARL": "ARP",
    "CAJA": "CAJA_DE_COMP_4%",
    "SENA": "SENA",
    "ICBF": "ICBF",
    "PROV. CESANTIAS": "CESANTIAS_8.33%",
    "PROV. INT CESANT": "INT._CESANTIAS_1%",
    "PRO_PRIMA": "PRIMA_8.33%",
    "PROV. VACACIONES": "VACACIONES_4.34%",
    "PROV. BONO ANUAL": "BONIFICACION_DIRECTIVO",
    "PROV. PRIMA EXTRALEGAL": "CONCEPTOS_NO_CONTEMPLADOS_SUPPLA_NO_PRESTACIONALES_CON_SERVICIOS",
}

""" Ejecutar funcion """
df_acumulado = calcular_sumas(df_acumulado, diccionario, "AGRUPACION", "TOTAL", asignar_primera_fila=False)

# --------------- CREAR COLUMNAS DE DIAS PAGO NOMINA  ---------------
""" Modificar diccionario """
diccionario = {"SALARIO A PAGAR": "DIAS_PAGO_NOMINA"}

""" Ejecutar funcion """
df_acumulado = calcular_sumas(df_acumulado, diccionario, "AGRUPACION", "TOTAL DIAS", asignar_primera_fila=True)

# --------------- CREAR COLUMNAS DE CUENTAS DE NOMINA CON SUMA DE DIAS ---------------
diccionario = {
    "HE DIURNA - 1.25    ": "HRS_HORA_EXTRA_DIURNA - 1,25",
    "HE NOCTURNA - 1.75  ": "HRS._HORA_EXTRA_NOCTURNA - 1,75",
    "HRS. EXTRA HORA DOM/FEST. NOCTURNA 2.50%": "HRS._EXTRA_HORA_DOM/FEST._NOCTURNA_2.50%",
    "HRS. HORA EXTRA DOMINICAL Y FESTIVA DIURNA 2.00%": "HRS._HORA_EXTRA_DOMINICAL_Y_FESTIVA_DIURNA_2.00%",
    "HRS. DOMINICAL DIURNO - 1,75": "HRS._DOMINICAL_DIURNO - 1,75",
    "FESTIVO DIURNO  1.75": "HRS._FESTIVO_DIURNO - 1,75",
    "RECAR DOM NOCT - 2.1": "HRS. RECARGO DOMINICAL NOCTURNO - 2,1",
    "RECARGO FESTIVO NOCTURNO - 2,1": "HRS._RECARGO_FESTIVO_NOCTURNO - 2,1",
    "RECARGO NOCT - 0.35 ": "HRS_RECARGO_NOCTURNO - 0,35",
    "DIAS AUSENCIAS JUSTIFICADAS SIN COBRO (Vac. Habiles, inc 66,67%)": "DIAS_AUSENCIAS_JUSTIFICADAS_SIN_COBRO (Vac. Habiles, inc 66,67%)",
}

""" Ejecutar funcion """
df_acumulado = calcular_sumas(df_acumulado, diccionario, "AGRUPACION", "CANTIDAD", asignar_primera_fila=True)

#---------------- CREAR COLUMNAS CON SUMA ENTRE COLUMNAS -----------------
""" Funcion para suma de columnas """
def crear_totales_desde_dict(df, dict_totales):
    for nombre_columna, columnas_a_sumar in dict_totales.items(): # Valida columnas existen
        columnas_existentes = [col for col in columnas_a_sumar if col in df.columns]
        if not columnas_existentes:
            print(f'Advertencia: Ninguna de las columnas para "{nombre_columna}" existe en el DataFrame.')
            df[nombre_columna] = 0
            continue
        
        df[nombre_columna] = df[columnas_existentes].sum(axis=1)
    return df

""" Diccionario con las columnas de suma """
totales_columnas = {
    "TOTAL # H.E.": [
        "HRS_HORA_EXTRA_DIURNA - 1,25",
        "HRS._HORA_EXTRA_NOCTURNA - 1,75",
        "HRS._EXTRA_HORA_DOM/FEST._NOCTURNA_2.50%",
        "HRS._HORA_EXTRA_DOMINICAL_Y_FESTIVA_DIURNA_2.00%"
    ],
    "TOTAL_HORAS_EXTRAS_SIN_R.N.": [
        "VR._HORA_EXTRA_DIURNA - 1,25",
        "VR._HORA_EXTRA_NOCTURNA - 1,75",
        "VR._EXTRA_HORA_DOM/FEST._NOCTURNA_2.50%",
        "VR._HORA_EXTRA_DOMINICAL_Y_FESTIVA_DIURNA_2.00%"
    ],
    "TOTAL NO. RECARGOS": [
        "HRS._DOMINICAL_DIURNO - 1,75",
        "HRS._FESTIVO_DIURNO - 1,75",
        "HRS. RECARGO DOMINICAL NOCTURNO - 2,1",
        "HRS._RECARGO_FESTIVO_NOCTURNO - 2,1",
        "HRS_RECARGO_NOCTURNO - 0,35"
    ],
    "TOTAL_$_RECARGOS": [
        "VR._DOMINICAL_DIURNO - 1,75",
        "VR._FESTIVO_DIURNO - 1,75",
        "VR._RECARGO_DOMINICAL_NOCTURNO - 2,1",
        "VR._RECARGO_FESTIVO_NOCTURNO - 2,1",
        "VR._RECARGO_NOCTURNO - 0,35"
    ],
    "TOTAL_S.S.": [
        "SALUD_PATRONO",
        "PENSION_12%",
        "ARP"
    ],
    "VALOR_PARAFISCALES": [
        "CAJA_DE_COMP_4%",
        "SENA",
        "ICBF"
    ],
    "VALOR_PRESTACIONES": [
        "CESANTIAS_8.33%",
        "INT._CESANTIAS_1%",
        "PRIMA_8.33%",
        "VACACIONES_4.34%"
    ],
    "TOTAL_NOMINA_S.S.PARAFI_PRESTA": [
        "SALARIO_A_PAGAR",
        "SUBSIDIO_TRANSPORTE",
        "TOTAL_HORAS_EXTRAS_SIN_R.N.",
        "TOTAL_$_RECARGOS",
        "REAJUSTE_RECARGOS",
        "REAJUSTE_H.E",
        "REAJUSTE_SALARIAL",
        "REAJUSTE_AUSENCIAS_JUSTIFICADAS",
        "REAJUSTE_VACACIONES",
        "BONIFICACION_NO_CONSTITUTIVA_DE_SALARIO",
        "BONIFICACION_SALARIAL",
        "TRANSPORTE_EXTRALEGAL_AUT._POR_CL",
        "AUXILIO_DE_RODAMIENTO",
        "MAY._VALOR_PAGADO_EN_SALARIO",
        "BENEFICIOS",
        "EXAMENES_MEDICOS_SERVICIOS",
        "VACACIONES",
        "OTROS_CONCEPTOS_FACTURABLES_PRESTACIONALES",
        "CONCEPTOS_NO_CONTEMPLADOS_SUPPLA_NO_PRESTACIONALES_CON_SERVICIOS",
        "TOTAL_S.S.",
        "VALOR_PARAFISCALES",
        "VALOR_PRESTACIONES"
    ],
    "SUBTOTAL FACTURA": [
        "SALARIO_A_PAGAR",
        "SUBSIDIO_TRANSPORTE",
        "TOTAL_HORAS_EXTRAS_SIN_R.N.",
        "TOTAL_$_RECARGOS",
        "REAJUSTE_RECARGOS",
        "REAJUSTE_H.E",
        "REAJUSTE_SALARIAL",
        "REAJUSTE_AUSENCIAS_JUSTIFICADAS",
        "REAJUSTE_VACACIONES",
        "BONIFICACION_NO_CONSTITUTIVA_DE_SALARIO",
        "BONIFICACION_SALARIAL",
        "TRANSPORTE_EXTRALEGAL_AUT._POR_CL",
        "AUXILIO_DE_RODAMIENTO",
        "MAY._VALOR_PAGADO_EN_SALARIO",
        "BENEFICIOS",
        "EXAMENES_MEDICOS_SERVICIOS",
        "VACACIONES",
        "OTROS_CONCEPTOS_FACTURABLES_PRESTACIONALES",
        "CONCEPTOS_NO_CONTEMPLADOS_SUPPLA_NO_PRESTACIONALES_CON_SERVICIOS",
        "TOTAL_S.S.",
        "VALOR_PARAFISCALES",
        "VALOR_PRESTACIONES",
        "MAY._VALOR_PAGADO_EN_AUX._TRANS",
        "IMPREVISTOS",
        "ADMINISTRACION",
        "BONIFICACION_DIRECTIVO"
    ]
}

""" Ejecutar funcion """
df_acumulado = crear_totales_desde_dict(df_acumulado, totales_columnas)

# --------------- CREAR COLUMNAS CON INICIALIZACIÓN EN 0 O STRING ---------------
""" Columnas con inicialización en 0 """
lista = [
    "IMPREVISTOS",
    "EXAMENES_MEDICOS_SERVICIOS",
    "MAYOR_VALOR_PAGADO_AUX._DE_RODAMIENTO",
    "ADMINISTRACION",
    "CARGO_MELI",
    "TIPO_DE_DOTACION",
    "TIPO_DE_CARGO",
    "NO.HORA_ORD_DOMINICAL_175",
    "VR.HORA_ORD_DOMINICAL_175",
    "HRS._HORA_DOMINICAL_Y_FESTIVO_CON_COMPENSATORIO_DIUR_1.00%",
    "VR._HORA_DOMINICAL_Y_FESTIVO_CON_COMPENSATORIO_DIUR_1.00%",
    "HRS_HORA_DOMINICAL_Y_FESTIVO_CON_COMPENSATORIO_NOC_1.35%",
    "VR._HORA_DOMINICAL_Y_FESTIVO_CON_COMPENSATORIO_NOC_1.35%"
]

""" Asignación a las columnas """
df_acumulado[lista] = 0

""" Columnas con string especifico """
df_acumulado["EMPRESA"] = "SUPPLA S.A"
df_acumulado["TIPO_DE_VINCULACIÓN"] = "DIRECTO"

""" Cambiar nombre de columna Mes """
df_acumulado = df_acumulado.rename(columns={
    "MES PROCESO":"MES"})


# --------------- COMPARATIVO DE NOMINA Y INTERFAZ ---------------
""" Crear copia de dataframe """
df_summ_cifrasMes = df_cifrasMes.copy()

""" Garantizar la columna como numero """
df_summ_cifrasMes["NETO"] = pd.to_numeric(df_summ_cifrasMes["NETO"], errors="coerce")

""" Crear tabla resumen de nomina """
df_summ_cifrasMes = df_summ_cifrasMes.pivot_table(index=["NUMERO DOCUMENTO", "NOMBRE COMPLETO", "CONCEPTO"],
                                            aggfunc={"NETO": "sum"}).reset_index()

""" Crear tabla resumen de nomina """
df_summ_acumulado = df_acumulado.pivot_table(index=["NUMERO DOCUMENTO", "NOMBRE COMPLETO", "CONCEPTO"],
                                            aggfunc={"NETO": "sum"}).reset_index()

""" Convertir a string columna """
df_summ_cifrasMes["NUMERO DOCUMENTO"] = df_summ_cifrasMes["NUMERO DOCUMENTO"].astype(str)
df_summ_acumulado["NUMERO DOCUMENTO"] = df_summ_acumulado["NUMERO DOCUMENTO"].astype(str)

""" Crear llaves de cada dataframe """
df_summ_cifrasMes["LLAVE"] = df_summ_cifrasMes["NUMERO DOCUMENTO"]+df_summ_cifrasMes["CONCEPTO"]
df_summ_acumulado["LLAVE"] = df_summ_acumulado["NUMERO DOCUMENTO"]+df_summ_acumulado["CONCEPTO"]

""" Merge Acumulado vs cifrasMes """
df_summ_acumulado = fusionar_dataframes(
    df_izquierdo=df_summ_acumulado,
    df_derecho=df_summ_cifrasMes,
    col_izq="LLAVE",
    col_der="LLAVE",
    como="left",
    nombre_union="Summ Acumulado vs Summ Cifras Mes"
)

""" Merge Acumulado vs cifrasMes """
df_summ_cifrasMes = fusionar_dataframes(
    df_izquierdo=df_summ_cifrasMes,
    df_derecho=df_summ_acumulado,
    col_izq="LLAVE",
    col_der="LLAVE",
    como="left",
    nombre_union="Summ Cifras Mes vs Summ Acumulado"
)

""" Eliminar Columnas y Variable """
eliminar(globals(), "df_summ_cifrasMes")
df_summ_acumulado = eliminar(df_summ_acumulado, "NUMERO DOCUMENTO_y", "NOMBRE COMPLETO_y","CONCEPTO_y", "LLAVE")

""" Cambiar nombre de columnas """
df_summ_acumulado = df_summ_acumulado.rename(columns={
    "NUMERO DOCUMENTO_x":"NUMERO DOCUMENTO",
    "NOMBRE COMPLETO_x": "NOMBRE COMPLETO",
    "CONCEPTO_x": "CONCEPTO",
    "NETO_x": "VALOR NOMINA",
    "NETO_y": "VALOR INTERFAZ",
    })

""" Modiifcar nan por 0 """
df_summ_acumulado["VALOR INTERFAZ"] = df_summ_acumulado["VALOR INTERFAZ"].fillna(0)

""" Crear columna de diferencia """
df_summ_acumulado["DIFERENCIA CONCEPTO"] = df_summ_acumulado["VALOR NOMINA"]-df_summ_acumulado["VALOR INTERFAZ"] 

""" Crear columna de total de valor nomina """
df_summ_acumulado.sort_values(by=["NUMERO DOCUMENTO"], inplace=True)
suma_por_documento = df_summ_acumulado.groupby("NUMERO DOCUMENTO")["VALOR NOMINA"].transform("sum")
es_primer_registro = ~df_summ_acumulado.duplicated(subset="NUMERO DOCUMENTO")
df_summ_acumulado["TOTAL NOMINA"] = suma_por_documento.where(es_primer_registro, 0)

""" Crear columna de total de valor interfaz """
suma_por_documento = df_summ_acumulado.groupby("NUMERO DOCUMENTO")["VALOR INTERFAZ"].transform("sum")
es_primer_registro = ~df_summ_acumulado.duplicated(subset="NUMERO DOCUMENTO")
df_summ_acumulado["TOTAL INTERFAZ"] = suma_por_documento.where(es_primer_registro, 0)

""" Eliminar Variable """
eliminar(globals(), "suma_por_documento", "es_primer_registro")

""" diferencia de columnas Total Nomina y Total Interfaz """
df_summ_acumulado["DIFERENCIA TOTAL"] = df_summ_acumulado["TOTAL NOMINA"]-df_summ_acumulado["TOTAL INTERFAZ"] 

# --------------- ORDENAR COLUMNAS DE NOMINA ---------------
""" Ordenar columnas de informe """
df_acumulado = df_acumulado[["EMPRESA", "TIPO_DE_VINCULACIÓN", "MES",
                             "CENTRO DE COSTOS", "NOMBRE CENTRO DE COSTOS",
                             "POBLACIÓN", "NUMERO DOCUMENTO","NOMBRE COMPLETO",
                             "CARGO NOMINA","TIPO_DE_DOTACION","TIPO_DE_CARGO",
                             "FECHA DE INGRESO","FECHA DE BAJA",
                             "SALARIO MENSUAL","DIAS_PAGO_NOMINA",
                             "SALARIO_A_PAGAR","SUBSIDIO_TRANSPORTE",
                             "HRS_HORA_EXTRA_DIURNA - 1,25",
                             "VR._HORA_EXTRA_DIURNA - 1,25",
                             "HRS._HORA_EXTRA_NOCTURNA - 1,75",
                             "VR._HORA_EXTRA_NOCTURNA - 1,75",
                             "NO.HORA_ORD_DOMINICAL_175",
                             "VR.HORA_ORD_DOMINICAL_175",
                             "HRS._EXTRA_HORA_DOM/FEST._NOCTURNA_2.50%",
                             "VR._EXTRA_HORA_DOM/FEST._NOCTURNA_2.50%",
                             "HRS._HORA_EXTRA_DOMINICAL_Y_FESTIVA_DIURNA_2.00%",
                             "VR._HORA_EXTRA_DOMINICAL_Y_FESTIVA_DIURNA_2.00%",
                             "TOTAL # H.E.",
                             "TOTAL_HORAS_EXTRAS_SIN_R.N.",
                             "HRS._DOMINICAL_DIURNO - 1,75",
                             "VR._DOMINICAL_DIURNO - 1,75",
                             "HRS._FESTIVO_DIURNO - 1,75",
                             "VR._FESTIVO_DIURNO - 1,75",
                             "HRS. RECARGO DOMINICAL NOCTURNO - 2,1",
                             "VR._RECARGO_DOMINICAL_NOCTURNO - 2,1",
                             "HRS._RECARGO_FESTIVO_NOCTURNO - 2,1",
                             "VR._RECARGO_FESTIVO_NOCTURNO - 2,1",
                             "HRS._HORA_DOMINICAL_Y_FESTIVO_CON_COMPENSATORIO_DIUR_1.00%",
                             "VR._HORA_DOMINICAL_Y_FESTIVO_CON_COMPENSATORIO_DIUR_1.00%",
                             "HRS_HORA_DOMINICAL_Y_FESTIVO_CON_COMPENSATORIO_NOC_1.35%",
                             "VR._HORA_DOMINICAL_Y_FESTIVO_CON_COMPENSATORIO_NOC_1.35%",
                             "HRS_RECARGO_NOCTURNO - 0,35",
                             "VR._RECARGO_NOCTURNO - 0,35",
                             "TOTAL NO. RECARGOS",
                             "TOTAL_$_RECARGOS","REAJUSTE_RECARGOS",
                             "REAJUSTE_H.E","REAJUSTE_SALARIAL",
                             "REAJUSTE_AUSENCIAS_JUSTIFICADAS",
                             "REAJUSTE_VACACIONES",
                             "DIAS_AUSENCIAS_JUSTIFICADAS_SIN_COBRO (Vac. Habiles, inc 66,67%)",
                             "VALOR_AUSENCIAS_JUSTIFICADAS_SIN_COBRO_(Vac. Habiles, inc 66,67%)",
                             "BONIFICACION_NO_CONSTITUTIVA_DE_SALARIO",
                             "BONIFICACION_SALARIAL",
                             "TRANSPORTE_EXTRALEGAL_AUT._POR_CL",
                             "AUXILIO_DE_RODAMIENTO",
                             "MAYOR_VALOR_PAGADO_AUX._DE_RODAMIENTO",
                             "MAY._VALOR_PAGADO_EN_SALARIO",
                             "MAY._VALOR_PAGADO_EN_AUX._TRANS","BENEFICIOS",
                             "EXAMENES_MEDICOS_SERVICIOS",
                             "VACACIONES","OTROS_CONCEPTOS_FACTURABLES_PRESTACIONALES",
                             "CONCEPTOS_NO_CONTEMPLADOS_SUPPLA_NO_PRESTACIONALES_CON_SERVICIOS",
                             "SALUD_PATRONO","PENSION_12%","ARP","TOTAL_S.S.",
                             "CAJA_DE_COMP_4%","SENA","ICBF",
                             "VALOR_PARAFISCALES","CESANTIAS_8.33%",
                             "INT._CESANTIAS_1%","PRIMA_8.33%",
                             "VACACIONES_4.34%","IMPREVISTOS",
                             "VALOR_PRESTACIONES","TOTAL_NOMINA_S.S.PARAFI_PRESTA",
                             "ADMINISTRACION","BONIFICACION_DIRECTIVO",
                             "SUBTOTAL FACTURA",
                             "DIAS_SUELDO_BASICO",
                             "DIAS_FAMILIAR",
                             "DIAS_PERMISO_JUSTIFICADO",
                             "DIAS_SANCION_/_SUSPENSION",
                             "DIAS_LICENCIA_NO_REMUN",
                             "DIAS_LICENCIA_MATERNIDAD",
                             "DIAS_AJS_LICENCIA_MATERN",
                             "DIAS_INASISTENCIA_INJUST",
                             "DIAS_VACACIONES",
                             "DIAS_VACACIONES_FESTIVAS",
                             "DIAS_VACACIONES_DINERO",
                             "DIAS_GASTO_INCAPACIDAD",
                             "DIAS_LIC_LEY_MARIA_8_DIAS",
                             "DIAS_INCAPACIDAD_ACC_TRAB",
                             "DIAS_INCAP_ENFERMEDAD_GEN",
                             "DIAS_VAC_HABILES_SAL_INT",
                             "DIAS_INCAPACIDAD_AL_50%",
                             "DIAS_DÍA_NO_LAB_DER_A_PAG",
                             "DIAS_RTEGRO_DTO_INASISTEN",
                             "DIAS_DTO_SALARIO",
                             "DIAS_INASIS_X_INC_>_180_D",
                             "DIAS_INCAP_ENF_GEN_PRORR",
                             "DIAS_DTO_INC_ENF_GRAL_AL",
                             "DIAS_RETROACTIV_SALARIO",
                             "DIAS_PERMISO_PERSONAL",
                             "DIAS_AJUS_SALARIO"                             
                             ]]

# --------------- UNIR ARCHIVOS DE TEMPORALES Y NOMINA ---------------
""" Leer archivo de temporales """
df_temp = pd.read_excel("Plantillas Facturacion y Nómina 2025 - Mercado libre.xlsx")

""" Cambiar nombre de columnas """
df_temp = df_temp.rename(columns={
    "TIPO DE VINCULACIÓN":"TIPO_DE_VINCULACIÓN",
    "COST CENTER":"CENTRO DE COSTOS", 
    "COST CENTER NAME":"NOMBRE CENTRO DE COSTOS",
    "CEDULA":"NUMERO DOCUMENTO",
    "NOMBRE DEL EMPLEADO":"NOMBRE COMPLETO",
    "FECHA INGRESO (D/M/A)":"FECHA DE INGRESO",
    "FECHA DE RETIRO (D/M/A)":"FECHA DE BAJA",
    "SALARIO BASICO":"SALARIO MENSUAL",
    "DIAS PAGO NOMINA":"DIAS_PAGO_NOMINA",
    "SALARIO A PAGAR":"SALARIO_A_PAGAR",
    "SUBSIDIO DE TRANSPORTE":"SUBSIDIO_TRANSPORTE",
    "HRS. HORA EXTRA DIURNA - 1,25":"HRS_HORA_EXTRA_DIURNA - 1,25",
    "VR. HORA EXTRA DIURNA - 1,25":"VR._HORA_EXTRA_DIURNA - 1,25",
    "HRS. HORA EXTRA NOCTURNA - 1,75":"HRS._HORA_EXTRA_NOCTURNA - 1,75",
    "VR. HORA EXTRA NOCTURNA - 1,75":"VR._HORA_EXTRA_NOCTURNA - 1,75",
    "NO.HORA ORD DOMINICAL 175":"NO.HORA_ORD_DOMINICAL_175",
    "VA.HORA ORD DOMINICAL 175":"VR.HORA_ORD_DOMINICAL_175",
    "HRS. EXTRA HORA DOM/FEST. NOCTURNA 2.50%":"HRS._EXTRA_HORA_DOM/FEST._NOCTURNA_2.50%",
    "VR. EXTRA HORA DOM/FEST. NOCTURNA 2.50%":"VR._EXTRA_HORA_DOM/FEST._NOCTURNA_2.50%",
    "HRS. HORA EXTRA DOMINICAL Y FESTIVA DIURNA 2.00%":"HRS._HORA_EXTRA_DOMINICAL_Y_FESTIVA_DIURNA_2.00%",
    "VR. HORA EXTRA DOMINICAL Y FESTIVA DIURNA 2.00%":"VR._HORA_EXTRA_DOMINICAL_Y_FESTIVA_DIURNA_2.00%",
    "TOTAL # H.E.":"TOTAL # H.E.",
    "TOTAL HORAS EXTRAS SIN R.N.":"TOTAL_HORAS_EXTRAS_SIN_R.N.",
    "HRS. DOMINICAL DIURNO - 1,75":"HRS._DOMINICAL_DIURNO - 1,75",
    "VR. DOMINICAL DIURNO - 1,75":"VR._DOMINICAL_DIURNO - 1,75",
    "HRS. FESTIVO DIURNO - 1,75":"HRS._FESTIVO_DIURNO - 1,75",
    "VR. FESTIVO DIURNO - 1,75":"VR._FESTIVO_DIURNO - 1,75",
    "HRS. RECARGO DOMINICAL NOCTURNO - 2,10":"HRS. RECARGO DOMINICAL NOCTURNO - 2,1",
    "VR. RECARGO DOMINICAL NOCTURNO - 2,10":"VR._RECARGO_DOMINICAL_NOCTURNO - 2,1",
    "HRS. RECARGO FESTIVO NOCTURNO - 2,1":"HRS._RECARGO_FESTIVO_NOCTURNO - 2,1",
    "VR. RECARGO FESTIVO NOCTURNO - 2,1":"VR._RECARGO_FESTIVO_NOCTURNO - 2,1",
    "HRS. HORA DOMINICAL Y FESTIVO CON COMPENSATORIO DIUR 1.00%":"HRS._HORA_DOMINICAL_Y_FESTIVO_CON_COMPENSATORIO_DIUR_1.00%",
    "VR. HORA DOMINICAL Y FESTIVO CON COMPENSATORIO DIUR 1.00%":"VR._HORA_DOMINICAL_Y_FESTIVO_CON_COMPENSATORIO_DIUR_1.00%",
    "HRS HORA DOMINICAL Y FESTIVO CON COMPENSATORIO NOC 1.35%":"HRS_HORA_DOMINICAL_Y_FESTIVO_CON_COMPENSATORIO_NOC_1.35%",
    "VR. HORA DOMINICAL Y FESTIVO CON COMPENSATORIO NOC 1.35%":"VR._HORA_DOMINICAL_Y_FESTIVO_CON_COMPENSATORIO_NOC_1.35%",
    "HRS RECARGO NOCTURNO - 0,35":"HRS_RECARGO_NOCTURNO - 0,35",
    "VR. RECARGO NOCTURNO - 0,35":"VR._RECARGO_NOCTURNO - 0,35",
    "TOTAL NO. RECARGO NOCTURNO":"TOTAL NO. RECARGOS",
    "TOTAL $ RECARGO NOCTURNO":"TOTAL_$_RECARGOS",
    "REAJUSTE RECARGOS":"REAJUSTE_RECARGOS",
    "REAJUSTE H.E":"REAJUSTE_H.E",
    "REAJUSTE SALARIAL":"REAJUSTE_SALARIAL",  
    "REAJUSTE AUSENCIAS JUSTIFICADAS":"REAJUSTE_AUSENCIAS_JUSTIFICADAS",
    "REAJUSTE VACACIONES":"REAJUSTE_VACACIONES",
    "DIAS AUSENCIAS JUSTIFICADAS SIN COBRO (Vac. Habiles, inc 66,67%)":"DIAS_AUSENCIAS_JUSTIFICADAS_SIN_COBRO (Vac. Habiles, inc 66,67%)",
    "VALOR AUSENCIAS JUSTIFICADAS SIN COBRO (Vac. Habiles, inc 66,67%)": "VALOR_AUSENCIAS_JUSTIFICADAS_SIN_COBRO_(Vac. Habiles, inc 66,67%)",
    "BONIFICACION NO CONSTITUTIVA DE SALARIO":"BONIFICACION_NO_CONSTITUTIVA_DE_SALARIO",
    "BONIFICACION SALARIAL":"BONIFICACION_SALARIAL",
    "TRANSPORTE EXTRALEGAL AUT. POR CL":"TRANSPORTE_EXTRALEGAL_AUT._POR_CL",
    "AUXILIO DE RODAMIENTO":"AUXILIO_DE_RODAMIENTO",
    "MAYOR VALOR PAGADO AUX. DE RODAMIENTO":"MAYOR_VALOR_PAGADO_AUX._DE_RODAMIENTO",
    "MAY. VALOR PAGADO EN SALARIO":"MAY._VALOR_PAGADO_EN_SALARIO",
    "MAY. VALOR PAGADO EN AUX. TRANS":"MAY._VALOR_PAGADO_EN_AUX._TRANS",
    "EXAMENES MEDICOS SERVICIOS":"EXAMENES_MEDICOS_SERVICIOS",
    "OTROS CONCEPTOS FACTURABLES PRESTACIONALES ":"OTROS_CONCEPTOS_FACTURABLES_PRESTACIONALES",
    "CONCEPTOS NO CONTEMPLADOS SUPPLA- NO PRESTACIONALES CON SERVICIOS":"CONCEPTOS_NO_CONTEMPLADOS_SUPPLA_NO_PRESTACIONALES_CON_SERVICIOS",
    "SALUD PATRONO":"SALUD_PATRONO",
    "PENSION 12%":"PENSION_12%",
    "TOTAL S.S.":"TOTAL_S.S.",
    "CAJA DE COMP 4%":"CAJA_DE_COMP_4%",
    "VALOR PARAFISCALES":"VALOR_PARAFISCALES",
    "CESANTIAS 8.33%":"CESANTIAS_8.33%",
    "INT. CESANTIAS 1%":"INT._CESANTIAS_1%",
    "PRIMA 8.33%":"PRIMA_8.33%",
    "VACACIONES 4.34%":"VACACIONES_4.34%",
    "VALOR PRESTACIONES":"VALOR_PRESTACIONES",
    "TOTAL NOMINA S.S.PARAFI PRESTA":"TOTAL_NOMINA_S.S.PARAFI_PRESTA",
    "BONIFICACION DIRECTIVO":"BONIFICACION_DIRECTIVO",
})

""" Eliminar duplicados del acumulado"""
df_acumulado = df_acumulado.drop_duplicates(subset="NUMERO DOCUMENTO", keep="first")

""" Actualizar acumulado con nombre de mes """
df_acumulado["MES"] = nombreMesActual

""" Unir archivos de acumulado y temporales """
df_acumulado = pd.concat([df_acumulado, df_temp], axis=0)

""" Eliminar Columnas y Variable """
df_acumulado = eliminar(df_acumulado, "a")
eliminar(globals(), "conceptos_lista", "df_temp")

# --------------- CREAR VARIABLES PARA ANALISIS DE DIAS ---------------
""" Crear variable con año actual """
añoActual = datetime.now().year

""" Funcion para obtener dias de mes """
def obtener_dias_mes(nombre_mes, año):
    meses_nombres_a_num = {
        "ENERO": 1, "FEBRERO": 2, "MARZO": 3, "ABRIL": 4, "MAYO": 5, "JUNIO": 6,
        "JULIO": 7, "AGOSTO": 8, "SEPTIEMBRE": 9, "OCTUBRE": 10, "NOVIEMBRE": 11, "DICIEMBRE": 12
    }
    num_mes = meses_nombres_a_num.get(nombre_mes.upper())
    if not num_mes:
        raise ValueError("Nombre de mes no válido")
    return calendar.monthrange(año, num_mes)[1]

""" Obetener dias de mes Actual y Anterior """
cDiasMesActual = obtener_dias_mes(nombreMesActual, añoActual)
cDiasMesAnterior = obtener_dias_mes(nomMesAnterior, añoActual)

""" Validar dias de cada mes """
cDiasMesAnterior = 30 if cDiasMesAnterior < 30 else cDiasMesAnterior #Se modifica para febrero <30
cDiasMesActual = 30 if cDiasMesActual == 31 else cDiasMesActual #Se modifica variable de dias del mes

# --------------- ANALISIS DE DIAS EN NOMINA ---------------
""" Actualizar dias a pagar si salario es igual a salario a pagar """
df_acumulado.loc[df_acumulado["SALARIO MENSUAL"] == df_acumulado["SALARIO_A_PAGAR"], "DIAS_PAGO_NOMINA"] = cDiasMesActual

""" Actualizar campos de fecha de ingreso y baja con fechas """
df_acumulado["FECHA DE INGRESO"] = df_acumulado["FECHA DE INGRESO"].fillna(pd.Timestamp("1900-01-01 00:00:00"))
df_acumulado["FECHA DE BAJA"] = df_acumulado["FECHA DE BAJA"].fillna(pd.Timestamp("1900-01-01 00:00:00"))
df_acumulado.loc[df_acumulado["FECHA DE BAJA"] == 1, "FECHA DE BAJA"] = "1900-01-01 00:00:00"

""" Convertir en datetima las columnas """
df_acumulado["FECHA DE INGRESO"] = pd.to_datetime(df_acumulado["FECHA DE INGRESO"])
df_acumulado["FECHA DE BAJA"] = pd.to_datetime(df_acumulado["FECHA DE BAJA"])

""" Crear columna de cantidad de dias según fechas de ingreso y baja """
df_acumulado["DIAS_TRABAJADOS"] = (df_acumulado["FECHA DE BAJA"] - df_acumulado["FECHA DE INGRESO"]).dt.days

""" Crear columna con validación de días a pagar """
df_acumulado["ESTATUS_DIAS"] = "VALIDAR"

""" Validar diferencia de 1 Peso en Salarios """
condicion = (
    (df_acumulado["ESTATUS_DIAS"] == "VALIDAR") &
    ((df_acumulado["SALARIO MENSUAL"] - df_acumulado["SALARIO_A_PAGAR"]).abs() == 1)
    )

df_acumulado.loc[condicion, "ESTATUS_DIAS"] = "OK"
df_acumulado.loc[condicion, "OBSERVACION"] = "Dias Laborados = Dias a Pagar (con diferencia de $1)"

""" Actualizar columna de estatus días """
condicion = df_acumulado["DIAS_TRABAJADOS"] == df_acumulado["DIAS_PAGO_NOMINA"]
df_acumulado.loc[condicion, "ESTATUS_DIAS"] = "OK"
df_acumulado.loc[condicion, "OBSERVACION"] = "Dias Laborados = Dias a Pagar"

condicion = df_acumulado["SALARIO MENSUAL"] == df_acumulado["SALARIO_A_PAGAR"]
df_acumulado.loc[condicion, "ESTATUS_DIAS"] = "OK"
df_acumulado.loc[condicion, "OBSERVACION"] = "Salario Mensual = Salario a Pagar"

condicion = df_acumulado["DIAS_PAGO_NOMINA"] == cDiasMesActual
df_acumulado.loc[condicion, "ESTATUS_DIAS"] = "OK"
df_acumulado.loc[condicion, "OBSERVACION"] = "30 Dias Trabajados"

""" Se verifica redondeando dias pago nomina y solo para empleados full time """
df_acumulado["DIAS_PAGO_NOMINA"] = df_acumulado["DIAS_PAGO_NOMINA"].astype(float)
df_acumulado["SALARIO MENSUAL"] = df_acumulado["SALARIO MENSUAL"].astype(float)

mask_salario = df_acumulado["SALARIO MENSUAL"] > 1000000
df_acumulado.loc[mask_salario, "DIAS_PAGO_NOMINA"] = df_acumulado.loc[mask_salario, "DIAS_PAGO_NOMINA"].round()

condicion = df_acumulado["DIAS_PAGO_NOMINA"] == cDiasMesActual
df_acumulado.loc[condicion, "ESTATUS_DIAS"] = "OK"
df_acumulado.loc[condicion, "OBSERVACION"] = "30 Dias Trabajados"

# --------------- ANALISIS DIAS SEGUN FECHA DE INGRESO Y RETIRO ---------------
""" Diccionario para convertir nombre del mes a número y crear funciones """
mes_nombre_a_num = {
    "ENERO": 1, "FEBRERO": 2, "MARZO": 3, "ABRIL": 4, "MAYO": 5, "JUNIO": 6,
    "JULIO": 7, "AGOSTO": 8, "SEPTIEMBRE": 9, "OCTUBRE": 10, "NOVIEMBRE": 11, "DICIEMBRE": 12
}

mes_num_a_nombre = {v: k for k, v in mes_nombre_a_num.items()}

""" Validar que columna esta en datetime """
df_acumulado["FECHA DE BAJA"] = pd.to_datetime(df_acumulado["FECHA DE BAJA"], errors="coerce")

""" Funcion para validar retiros en el mismo mes """
# Crear columna con el primer día del mes
def calcular_fecha_inicio_mes(mes_nombre):
    if isinstance(mes_nombre, str):
        mes_nombre = mes_nombre.strip().upper()
        mes = mes_nombre_a_num.get(mes_nombre, None)
        if mes:
            return pd.Timestamp(year=2025, month=mes, day=1)
    return pd.NaT

""" Ejecución de función """
df_acumulado["FECHA_INICIO_MES"] = df_acumulado["MES"].apply(calcular_fecha_inicio_mes)

""" Crear columna con diferencia de dias """
df_acumulado["DIFERENCIA_DIAS"] = (df_acumulado["FECHA DE BAJA"] - df_acumulado["FECHA_INICIO_MES"]).dt.days+1

""" Actualizar Observacion y Estatus dias """
condicion = (
    (df_acumulado["ESTATUS_DIAS"] == "VALIDAR") &
    (df_acumulado["DIFERENCIA_DIAS"] == df_acumulado["DIAS_PAGO_NOMINA"])
)

df_acumulado.loc[condicion, "ESTATUS_DIAS"] = "OK"
df_acumulado.loc[condicion, "OBSERVACION"] = "Empleado con Retiro en Mismo Mes"

""" Funcion para obtener fecha final del mes """
def obtener_fecha_fin_mes(fila):
    anio = fila["FECHA_INICIO_MES"].year
    mes_texto = str(fila["MES"]).upper()
    mes = mes_nombre_a_num.get(mes_texto)
    if pd.notna(anio) and mes:
        ultimo_dia = calendar.monthrange(anio, mes)[1]
        return datetime(anio, mes, ultimo_dia)
    return pd.NaT

""" Crear columna con fecha final del mes """
df_acumulado["FECHA_FIN_MES"] = df_acumulado.apply(
    lambda fila: obtener_fecha_fin_mes(fila) if fila["FECHA_INICIO_MES"] < fila["FECHA DE INGRESO"] else pd.NaT,
    axis=1
)

""" Actualizar la columna de diferencia días """
condicion = df_acumulado["FECHA_INICIO_MES"] < df_acumulado["FECHA DE INGRESO"]

df_acumulado.loc[condicion, "DIFERENCIA_DIAS"] = (
    (df_acumulado.loc[condicion, "FECHA_FIN_MES"] - df_acumulado.loc[condicion, "FECHA DE INGRESO"]).dt.days
)

""" Actualizar Observacion y Estatus dias """
condicion = (
    (df_acumulado["ESTATUS_DIAS"] == "VALIDAR") &
    (df_acumulado["DIFERENCIA_DIAS"] == df_acumulado["DIAS_PAGO_NOMINA"])
)

df_acumulado.loc[condicion, "ESTATUS_DIAS"] = "OK"
df_acumulado.loc[condicion, "OBSERVACION"] = "Empleado con Ingreso en Mismo Mes"

""" Actualizar diferencia dias si mas 1 dan los días """
condicion = df_acumulado["FECHA_INICIO_MES"] < df_acumulado["FECHA DE INGRESO"]

df_acumulado.loc[condicion, "DIFERENCIA_DIAS"] = (
    (df_acumulado.loc[condicion, "FECHA_FIN_MES"] - df_acumulado.loc[condicion, "FECHA DE INGRESO"]).dt.days + 1
)

""" Actualizar columnas diferencia dias es igual a dias pagos """
condicion = (
    (df_acumulado["ESTATUS_DIAS"] == "VALIDAR") &
    (df_acumulado["DIFERENCIA_DIAS"] == df_acumulado["DIAS_PAGO_NOMINA"])
)

df_acumulado.loc[condicion, "ESTATUS_DIAS"] = "OK"
df_acumulado.loc[condicion, "OBSERVACION"] = "Empleado con Ingreso en Mismo Mes"

""" Validar dias de colaboradores con ingreso y salida en mismo mes """
condicion = (
    (df_acumulado["FECHA_INICIO_MES"] < df_acumulado["FECHA DE INGRESO"]) &
    (df_acumulado["FECHA_FIN_MES"] > df_acumulado["FECHA DE BAJA"])
)

df_acumulado.loc[condicion, "DIFERENCIA_DIAS"] = (
    (df_acumulado.loc[condicion, "FECHA DE BAJA"] - df_acumulado.loc[condicion, "FECHA DE INGRESO"]).dt.days + 1
)

""" Actualizar Observacion y Estatus dias """
condicion = (
    (df_acumulado["ESTATUS_DIAS"] == "VALIDAR") &
    (df_acumulado["DIFERENCIA_DIAS"] == df_acumulado["DIAS_PAGO_NOMINA"])
)

df_acumulado.loc[condicion, "ESTATUS_DIAS"] = "OK"
df_acumulado.loc[condicion, "OBSERVACION"] = "Empleado con Ingreso y Retiro en Mismo Mes"

""" Modificar datos de columna """
df_acumulado.loc[df_acumulado["FECHA DE BAJA"] == pd.Timestamp("1900-01-01"), "FECHA DE BAJA"] = pd.Timestamp("1990-01-01")

""" Actualizar columna fecha fin mes """
primer_valor = df_acumulado["FECHA_FIN_MES"].dropna().iloc[0]
df_acumulado["FECHA_FIN_MES"] = df_acumulado["FECHA_FIN_MES"].fillna(primer_valor)

""" Crear observacion de validar retiro cuando las fechas no concuerdan """
condicion = (
    (df_acumulado["ESTATUS_DIAS"] == "VALIDAR") &    
    (df_acumulado["DIFERENCIA_DIAS"] != df_acumulado["DIAS_PAGO_NOMINA"]) &
    (df_acumulado["FECHA DE BAJA"] != "1990-01-01 00:00:00") &
    (df_acumulado["FECHA_FIN_MES"] > df_acumulado["FECHA DE BAJA"])
)

df_acumulado.loc[condicion, "ESTATUS_DIAS"] = "VALIDAR"
df_acumulado.loc[condicion, "OBSERVACION"] = "Validar Retiro"


# ---------------- VALIDAR RETIROS DIAS VIERNES ----------------
""" Verificar tipo datetime """
df_acumulado["FECHA DE BAJA"] = pd.to_datetime(df_acumulado["FECHA DE BAJA"], errors="coerce")

""" Crear la nueva columna con el nombre del día de la semana (Ej: "Lunes", "Martes", etc.) """
df_acumulado["DIA SEMANA RETIRO"] = df_acumulado["FECHA DE BAJA"].dt.day_name(locale="es_ES")

""" Actualizar diferencia de dias con dias no laborales """
condicion = (
    (df_acumulado["ESTATUS_DIAS"] == "VALIDAR") &    
    (df_acumulado["OBSERVACION"] == "Validar Retiro") &
    (df_acumulado["EMPRESA"] == "SUPPLA S.A") &
    (df_acumulado["DIA SEMANA RETIRO"] == "Viernes")
)

df_acumulado.loc[condicion, "ESTATUS_DIAS"] = "VALIDAR"
df_acumulado.loc[condicion, "DIFERENCIA_DIAS"] = df_acumulado.loc[condicion, "DIFERENCIA_DIAS"] + 2

""" Actualizar si el retiro es un viernes """
condicion = (
    (df_acumulado["ESTATUS_DIAS"] == "VALIDAR") &    
    (df_acumulado["OBSERVACION"] == "Validar Retiro") &
    (df_acumulado["EMPRESA"] == "SUPPLA S.A") &
    (df_acumulado["DIA SEMANA RETIRO"] == "Viernes") &
    (df_acumulado["DIFERENCIA_DIAS"] == df_acumulado["DIAS_PAGO_NOMINA"])
)

df_acumulado.loc[condicion, "ESTATUS_DIAS"] = "OK"
df_acumulado.loc[condicion, "OBSERVACION"] = "Empleado con Retiro en Mismo Mes"

""" Actualizar si el retiro es un viernes """
condicion = (
    (df_acumulado["ESTATUS_DIAS"] == "VALIDAR") &    
    (df_acumulado["OBSERVACION"] == "Validar Retiro") &
    (df_acumulado["EMPRESA"] == "SUPPLA S.A") &
    (df_acumulado["DIAS_DÍA_NO_LAB_DER_A_PAG"] >0) &
    ((df_acumulado["DIAS_PAGO_NOMINA"] - df_acumulado["DIAS_DTO_SALARIO"]) == df_acumulado["DIFERENCIA_DIAS"])
)

df_acumulado.loc[condicion, "ESTATUS_DIAS"] = "OK"
df_acumulado.loc[condicion, "OBSERVACION"] = (
    df_acumulado.loc[condicion, "DIAS_DÍA_NO_LAB_DER_A_PAG"].astype(int).astype(str) + 
    " Dias No Laborales " + 
    df_acumulado.loc[condicion, "DIAS_DTO_SALARIO"].astype(int).astype(str) + 
    " Dias Dcto"
)

""" Actualizar si el retiro es un viernes """
condicion = (
    (df_acumulado["ESTATUS_DIAS"] == "VALIDAR") &    
    (df_acumulado["OBSERVACION"] == "Validar Retiro") &
    (df_acumulado["EMPRESA"] == "SUPPLA S.A") &
    ((df_acumulado["DIAS_PAGO_NOMINA"] - df_acumulado["DIAS_DTO_SALARIO"]) == df_acumulado["DIFERENCIA_DIAS"])
)

df_acumulado.loc[condicion, "ESTATUS_DIAS"] = "OK"
df_acumulado.loc[condicion, "OBSERVACION"] = (
    df_acumulado.loc[condicion, "DIAS_PAGO_NOMINA"].astype(int).astype(str) + 
    " Dias Trabajados " + 
    df_acumulado.loc[condicion, "DIAS_DTO_SALARIO"].astype(int).astype(str) + 
    " Dias Dcto"
)

# ---------------- VALIDAR RETIROS DIAS SABADO ----------------
""" Actualizar diferencia de dias con dias no laborales """
condicion = (
    (df_acumulado["ESTATUS_DIAS"] == "VALIDAR") &    
    (df_acumulado["OBSERVACION"] == "Validar Retiro") &
    (df_acumulado["EMPRESA"] == "SUPPLA S.A") &
    (df_acumulado["DIA SEMANA RETIRO"] == "Sábado")
)

df_acumulado.loc[condicion, "ESTATUS_DIAS"] = "VALIDAR"
df_acumulado.loc[condicion, "DIFERENCIA_DIAS"] = df_acumulado.loc[condicion, "DIFERENCIA_DIAS"] + 1

""" Condiciones para actualizar si es sabadao"""
condicion = (
    (df_acumulado["ESTATUS_DIAS"] == "VALIDAR") &    
    (df_acumulado["OBSERVACION"] == "Validar Retiro") &
    (df_acumulado["EMPRESA"] == "SUPPLA S.A") &
    (df_acumulado["DIA SEMANA RETIRO"] == "Sábado") &
    (df_acumulado["DIFERENCIA_DIAS"] == df_acumulado["DIAS_PAGO_NOMINA"])
)

df_acumulado.loc[condicion, "ESTATUS_DIAS"] = "OK"
df_acumulado.loc[condicion, "OBSERVACION"] = "Empleado con Retiro en Mismo Mes"

# ---------------- VERIFICAR LOS EMPLEADOS CON CAMBIO DE VINCULACION ----------------
""" Funcion para validar empleados con cambio de vinculacion """
def validar_cambio_vinculacion(grupo, cDiasMesActual):
    if len(grupo) != 2:

        return grupo  # Solo duplicados exactos de 2
        
    tipos = set(grupo["TIPO_DE_VINCULACIÓN"])

    # Verificar si hay directo y temporal
    if tipos == {"DIRECTO", "TEMPORAL"}:
        suma_dias = grupo["DIAS_PAGO_NOMINA"].sum()
        
        if suma_dias == cDiasMesActual:
            # Ordenamos por TIPO_DE_VINCULACIÓN para control
            grupo_ordenado = grupo.sort_values("TIPO_DE_VINCULACIÓN")

            fila1 = grupo_ordenado.iloc[0]
            fila2 = grupo_ordenado.iloc[1]

            observacion = (
                f'{fila1["DIAS_PAGO_NOMINA"]} Dias Trabajados en {fila1["TIPO_DE_VINCULACIÓN"]} '
                f'{fila2["DIAS_PAGO_NOMINA"]} Dias Trabajados en {fila2["TIPO_DE_VINCULACIÓN"]}'
            )

            grupo.loc[:, "ESTATUS_DIAS"] = "OK"
            grupo.loc[:, "OBSERVACION"] = observacion

    return grupo

""" Crear copia del df_acumulado """
df_acumulado["NUMERO_DOCUMENTO_copy"] = df_acumulado["NUMERO DOCUMENTO"]    

""" Ejecutar funcion """
df_acumulado = (
    df_acumulado
    .groupby("NUMERO DOCUMENTO", group_keys=False)
    .apply(lambda grupo: validar_cambio_vinculacion(grupo, cDiasMesActual), include_groups=False)
).reset_index(drop=True)

""" Recuperar la columna de la copia """
df_acumulado["NUMERO DOCUMENTO"] = df_acumulado["NUMERO_DOCUMENTO_copy"]

""" Eliminar la columna temporal """
df_acumulado.drop(columns=["NUMERO_DOCUMENTO_copy"], inplace=True)

# ---------------- VALIDAR SALARIO Y CARGO DEL MES ANTERIOR ----------------
""" Eliminar duplicados """
df_consoNomina = df_consoNomina.drop_duplicates(subset=["CEDULA"])

""" Validar si la columna existe """
if "NUMERO DOCUMENTO" not in df_acumulado.columns and "NUMERO DOCUMENTO" in df_acumulado.index.names:
    df_acumulado = df_acumulado.reset_index()

""" Merge Acumulado vs Nomina Mes Anterior """
df_acumulado = fusionar_dataframes(
    df_izquierdo=df_acumulado,
    df_derecho=df_consoNomina,
    col_izq="NUMERO DOCUMENTO",
    col_der="CEDULA",
    como="left",
    nombre_union="Acumulado vs Nomina Mes Anterior"
)

""" Validar si cargo y salario son del mes actual y anterior son iguales """
df_acumulado["VALIDACION SALARIO Y CARGO"] = df_acumulado.apply(
    lambda fila: "Salario y Cargo del Mes Anterior es Igual"
    if fila["CARGO NOMINA_x"] == fila["CARGO NOMINA_y"] and fila["SALARIO MENSUAL"] == fila["SALARIO BASICO"]
    else "Salario o Cargo del Mes Anterior Diferentes",
    axis=1
)

""" Eliminar Columnas """
df_acumulado = eliminar(df_acumulado, "CARGO NOMINA_y", "CEDULA", "SALARIO BASICO")

# ---------------- FUNCION PARA VALIDAR DIAS SEGÚN NOVEDADES ----------------
""" Cambiar tipo de columnas a int """
df_acumulado["DIAS_SANCION_/_SUSPENSION"] = df_acumulado["DIAS_SANCION_/_SUSPENSION"].fillna(0).astype(int)
df_acumulado["DIAS_PAGO_NOMINA"] = df_acumulado["DIAS_PAGO_NOMINA"].fillna(0).astype(int)
df_acumulado["DIAS_VACACIONES"] = df_acumulado["DIAS_VACACIONES"].fillna(0).astype(int)
df_acumulado["DIAS_INCAP_ENFERMEDAD_GEN"] = df_acumulado["DIAS_INCAP_ENFERMEDAD_GEN"].fillna(0).astype(int)
df_acumulado["DIAS_GASTO_INCAPACIDAD"] = df_acumulado["DIAS_GASTO_INCAPACIDAD"].fillna(0).astype(int)

""" Crear columna de total dias  """
lista = [
    "DIAS_SUELDO_BASICO",
    "DIAS_FAMILIAR",
    "DIAS_PERMISO_JUSTIFICADO",
    "DIAS_SANCION_/_SUSPENSION",
    "DIAS_LICENCIA_NO_REMUN",
    "DIAS_INASISTENCIA_INJUST",
    "DIAS_VACACIONES",
    "DIAS_GASTO_INCAPACIDAD",
    "DIAS_LIC_LEY_MARIA_8_DIAS",
    "DIAS_INCAPACIDAD_ACC_TRAB",
    "DIAS_INCAP_ENFERMEDAD_GEN",
    "DIAS_LICENCIA_MATERNIDAD",
    "DIAS_VAC_HABILES_SAL_INT",
    "DIAS_INCAPACIDAD_AL_50%",
    "DIAS_DÍA_NO_LAB_DER_A_PAG",
    "DIAS_RTEGRO_DTO_INASISTEN",
    "DIAS_AJS_LICENCIA_MATERN",
    "DIAS_INCAP_ENF_GEN_PRORR",
    "DIAS_VACACIONES_FESTIVAS",
    "DIAS_DTO_SALARIO",
    "DIAS_INASIS_X_INC_>_180_D",
    "DIAS_DTO_INC_ENF_GRAL_AL",
    "DIAS_RETROACTIV_SALARIO",
    "DIAS_PERMISO_PERSONAL",
    "DIAS_AJUS_SALARIO"
    
    
]# Se elimina la columna de Dias Vacaciones en Dinero

df_acumulado[lista] = df_acumulado[lista].abs()
df_acumulado[lista] = df_acumulado[lista].fillna(0).astype(int)
df_acumulado["TOTAL_SUMA_DIAS"] = df_acumulado[lista].sum(axis=1)

# ---------------- VERIFICACION DE DÍAS SI CUMPLE LA SUMA CON 30 DIAS ----------------
""" Diccionario de columnas y texto asociado """
diccionario = {
    "DIAS_SANCION_/_SUSPENSION": "Dias Sancion",
    "DIAS_PERMISO_PERSONAL": "Dias Permiso Personal",
    "DIAS_PERMISO_JUSTIFICADO": "Dias Permiso Justificado",
    "DIAS_FAMILIAR" : "Dia Familiar",
    "DIAS_LICENCIA_NO_REMUN": "Dias Licencia No Remunerada",
    "DIAS_INASISTENCIA_INJUST": "Dias Inasistencia",
    "DIAS_VACACIONES": "Dias Vacaciones",
    "DIAS_VACACIONES_DINERO": "Dias Vacaciones en Dinero",
    "DIAS_GASTO_INCAPACIDAD": "Dias Gasto Incapacidad",
    "DIAS_LIC_LEY_MARIA_8_DIAS": "Dias Lic Ley Maria Dias Diaserada",
    "DIAS_INCAPACIDAD_ACC_TRAB": "Dias Incapacidad Acc Trab",
    "DIAS_INCAP_ENFERMEDAD_GEN": "Dias Incap Enfermedad General",
    "DIAS_LICENCIA_MATERNIDAD": "Dias Licencia Maternidad",
    "DIAS_VAC_HABILES_SAL_INT": "Dias Vac Habiles Sal Int",
    "DIAS_INCAPACIDAD_AL_50%": "Dias Incapacidad",
    "DIAS_DÍA_NO_LAB_DER_A_PAG": "Dias Día No Lab Der A Pag",
    "DIAS_RTEGRO_DTO_INASISTEN": "Dias Rtegro Dto Inasistencia",
    "DIAS_AJS_LICENCIA_MATERN": "Dias Ajs Licencia Maternerada",
    "DIAS_INCAP_ENF_GEN_PRORR": "Dias Incap Enf Gen Prorr",
    "DIAS_VACACIONES_FESTIVAS": "Dias Vacaciones Festivas",
    "DIAS_DTO_SALARIO": "Dias Dto Salario",
    "DIAS_INASIS_X_INC_>_180_D": "Dias Inasis X Inc >180 D",
    "DIAS_DTO_INC_ENF_GRAL_AL": "Dias Dto Inc Enf Gral",
    "DIAS_RETROACTIV_SALARIO": "Dias Retroactivo Salario",
    "DIAS_AJUS_SALARIO": "Dias Ajuste Salario"
}

""" Funcion para construir observacion """
def construir_observacion(df_filas, diccionario):
    observaciones = []
    for idx in df_filas.index:
        partes = []

        # 1. Agregar siempre DIAS_PAGO_NOMINA
        if "DIAS_PAGO_NOMINA" in df_filas.columns and pd.notna(df_filas.at[idx, "DIAS_PAGO_NOMINA"]):
            partes.append(f"{int(df_filas.at[idx, 'DIAS_PAGO_NOMINA'])} Días trabajados")

        # 2. Agregar el resto según el diccionario
        for col, texto in diccionario.items():
            if col in df_filas.columns and pd.notna(df_filas.at[idx, col]) and df_filas.at[idx, col] > 0:
                partes.append(f"{int(df_filas.at[idx, col])} {texto}")

        # Unir todo
        observaciones.append("; ".join(partes))

    return observaciones

""" Funcion para validar reglas """
def aplicar_reglas(df, diccionario):
    reglas = [
        (# ACTUALIZAR SI SUMA DE DIAS ES IGUAL A 30
            (df["ESTATUS_DIAS"] == "VALIDAR") &
            (df["EMPRESA"] == "SUPPLA S.A") &
            (df["TOTAL_SUMA_DIAS"] == cDiasMesActual),
            True,
            True 
        ),
        (# ACTUALIZAR SI TIENE RETIRO DEL MES ANTERIOR
            (df_acumulado["ESTATUS_DIAS"] == "VALIDAR") &
            (df_acumulado["EMPRESA"] == "SUPPLA S.A") &
            (df_acumulado["OBSERVACION"] == "Validar Retiro") &
            (df_acumulado["FECHA_INICIO_MES"] > df_acumulado["FECHA DE BAJA"]),
            True,
            True 
        ),
        (# VERIFICACION DE DÍAS SI APLICA POR REINTEGRO
            (df_acumulado["ESTATUS_DIAS"] == "VALIDAR") &
            (df_acumulado["EMPRESA"] == "SUPPLA S.A") &
            ((df_acumulado["TOTAL_SUMA_DIAS"] - df_acumulado["DIAS_RTEGRO_DTO_INASISTEN"]) == cDiasMesActual),
            True,
            True 
        ),
        (# VERIFICACION DE DÍAS SI APLICA POR VACACIONES
            (df_acumulado["ESTATUS_DIAS"] == "VALIDAR") &
            (df_acumulado["TOTAL_SUMA_DIAS"] > 30) &
            (df_acumulado["DIAS_VACACIONES"] > 0) &
            (df_acumulado["EMPRESA"] == "SUPPLA S.A"),
            True,
            True
        ),
        (# VERIFICACION DE DÍAS SUELDO BASICO CON GASTO INCAPACIDAD
            (df_acumulado["ESTATUS_DIAS"] == "VALIDAR") &    
            (df_acumulado["EMPRESA"] == "SUPPLA S.A") &
            (df_acumulado["DIAS_GASTO_INCAPACIDAD"] > 0) &
            ((df_acumulado["DIAS_SUELDO_BASICO"] + df_acumulado["DIAS_GASTO_INCAPACIDAD"]) == df_acumulado["DIAS_PAGO_NOMINA"]),
            True,
            True
        ),
        (# VERIFICACION DE DÍAS DIAS PAGO + INASISTENCIA + INCAPACIDAD
            (df_acumulado["ESTATUS_DIAS"] == "VALIDAR") &
            (df_acumulado["EMPRESA"] == "SUPPLA S.A") &
            (
                (df_acumulado["DIAS_INASISTENCIA_INJUST"] > 0) |
                (df_acumulado["DIAS_INCAP_ENFERMEDAD_GEN"] > 0)
            ) &
            (
                df_acumulado["DIAS_PAGO_NOMINA"]
                + df_acumulado["DIAS_INASISTENCIA_INJUST"]
                + df_acumulado["DIAS_INCAP_ENFERMEDAD_GEN"]
                == cDiasMesActual
            ),
            True,
            True
        ),
        (# VERIFICACION DE DÍAS DIAS PAGO - DIAS SANCION
            (df_acumulado["ESTATUS_DIAS"] == "VALIDAR") &    
            (df_acumulado["EMPRESA"] == "SUPPLA S.A") &
            (df_acumulado["DIAS_SANCION_/_SUSPENSION"] > 0) &
            (
            ((df_acumulado["DIAS_PAGO_NOMINA"] - df_acumulado["DIAS_SANCION_/_SUSPENSION"]) == cDiasMesActual) |
            ((df_acumulado["DIAS_SUELDO_BASICO"] - df_acumulado["DIAS_SANCION_/_SUSPENSION"]) == df_acumulado["DIAS_PAGO_NOMINA"])
            ),
            True,
            True
        ),
        (# VERIFICACION DE DIAS CON INCAPACIDAD
            (df_acumulado["ESTATUS_DIAS"] == "VALIDAR") &    
            (df_acumulado["EMPRESA"] == "SUPPLA S.A") &
            (df_acumulado["DIAS_INCAP_ENFERMEDAD_GEN"] > 0) &
            ((df_acumulado["DIAS_PAGO_NOMINA"] - df_acumulado["DIAS_INCAP_ENFERMEDAD_GEN"]) == cDiasMesActual),
            True,
            True
        ),
        (# VERIFICACION DIAS INASISTENCIA Y SANCION
            (df_acumulado["ESTATUS_DIAS"] == "VALIDAR") &
            (df_acumulado["EMPRESA"] == "SUPPLA S.A") &
            (df_acumulado["DIAS_INASISTENCIA_INJUST"] > 0) &
            (df_acumulado["DIAS_SANCION_/_SUSPENSION"] > 0) &
            (
                round(
                    df_acumulado["DIAS_PAGO_NOMINA"]
                    + df_acumulado["DIAS_INASISTENCIA_INJUST"]
                    + df_acumulado["DIAS_SANCION_/_SUSPENSION"]
                ) == cDiasMesActual
            ),
            True,
            True
        ),
        (# VERIFICACION DIAS DCTO SALARIO O MAYOR VALOR PAGADO
            (df_acumulado["ESTATUS_DIAS"] == "VALIDAR") &
            (df_acumulado["EMPRESA"] == "SUPPLA S.A") &
            (df_acumulado["MAY._VALOR_PAGADO_EN_SALARIO"].abs() > 0) &
            (
                (
                    df_acumulado["DIAS_PAGO_NOMINA"]
                    - df_acumulado["DIAS_DTO_SALARIO"].round()
                ).astype(int) == df_acumulado["DIFERENCIA_DIAS"]
            ),
            True,
            True
        ),
        (# VERIFICACION DIAS DCTO SALARIO E INASITENCIAS CON RETIRO
            (df_acumulado["ESTATUS_DIAS"] == "VALIDAR") &
            (df_acumulado["EMPRESA"] == "SUPPLA S.A") &
            (df_acumulado["OBSERVACION"] == "Validar Retiro") &
            (df_acumulado["MAY._VALOR_PAGADO_EN_SALARIO"].abs() > 0) &
            (
                (
                    (
                        df_acumulado["DIAS_PAGO_NOMINA"] + df_acumulado["DIAS_DÍA_NO_LAB_DER_A_PAG"]
                    ) - (
                        df_acumulado["DIAS_DTO_SALARIO"] + df_acumulado["DIAS_INASISTENCIA_INJUST"]
                    )
                ).round().astype(int)
                == (df_acumulado["DIFERENCIA_DIAS"] -  df_acumulado["DIAS_INASISTENCIA_INJUST"]).astype(int)
            ),
            True,
            True
        ),
        (# VERIFICACION SALIDA ANTES DE INCIAR MES Y CON DCTO DE PAGO
            (df_acumulado["ESTATUS_DIAS"] == "VALIDAR") &
            (df_acumulado["OBSERVACION"] == "Validar Retiro") &
            ((df_acumulado["FECHA DE BAJA"] - df_acumulado["FECHA_INICIO_MES"]).dt.days < 0) &
            ((df_acumulado["SALARIO_A_PAGAR"] + df_acumulado["MAY._VALOR_PAGADO_EN_SALARIO"]).abs() == 0),
            True,
            True,
            "No se realiza pago por descuento mayor valor pagado"
        ),
    ]

    for regla in reglas:
        if len(regla) == 3:
            condicion, upd_observacion, upd_estatus = regla
            texto_personalizado = None
        else:
            condicion, upd_observacion, upd_estatus, texto_personalizado = regla

        sin_clasificar = (
            df["OBSERVACION"].isna() |
            (df["OBSERVACION"] == "") |
            (df["OBSERVACION"] == "Validar Retiro")
        )
        mask = sin_clasificar & condicion

        if upd_observacion:
            if texto_personalizado:
                df.loc[mask, "OBSERVACION"] = texto_personalizado
            else:
                df.loc[mask, "OBSERVACION"] = construir_observacion(df.loc[mask], diccionario)
        if upd_estatus:
            df.loc[mask, "ESTATUS_DIAS"] = "OK"

    return df

""" Ejecutar Funcion """
df_acumulado = aplicar_reglas(df_acumulado, diccionario)

# ---------------- OBTENER DIAS DEL MES ANTERIOR ----------------
""" Leer archivo de acumulado año """
df_acumuladoAño = pd.read_excel("Acumulado_Año.xlsx")

""" Actualizar acumulado año con nombre de mes """
df_acumuladoAño["MES PROCESO"] = df_acumuladoAño["MES PROCESO"].apply(
    lambda x: meses[int(x) - 1] if pd.notnull(x) else None
)

""" Asegurarse de que MES y MES PROCESO estén en formato numérico """
df_acumulado["MES"] = df_acumulado["MES"].map(mes_nombre_a_num)
df_acumuladoAño["MES PROCESO"] = df_acumuladoAño["MES PROCESO"].map(mes_nombre_a_num)

""" Funcion para obtener dias de sueldo basico del mes anterior """
def obtener_dias_conceptos_periodo_anterior(row, descripciones, df_acumuladoAño, nomMesAnterior):
    if row["ESTATUS_DIAS"] != "VALIDAR":
        return {desc: 0 for desc in descripciones}

    documento = row["NUMERO DOCUMENTO"]
    mes_actual = row["MES"]
    mes_anterior = mes_actual - 1 if mes_actual > 1 else 12

    resultados = {}

    for desc in descripciones:
        filtro = (
            (df_acumuladoAño["NUMERO DOCUMENTO"] == documento) &
            (df_acumuladoAño["MES PROCESO"] == mes_anterior) &
            (df_acumuladoAño["DESCRIPCIÓN"].str.strip().str.upper() == desc.strip().upper())
        )
        suma = df_acumuladoAño.loc[filtro, "CANTIDAD"].sum()
        resultados[f"{desc}_{nomMesAnterior}"] = suma if suma != 0 else 0

    return resultados

""" Limpiar registros de columna """
if "DESCRIPCIÓN" in df_acumuladoAño.columns:
    df_acumuladoAño["DESCRIPCIÓN"] = df_acumuladoAño["DESCRIPCIÓN"].astype(str).str.strip()

""" Actualizar el concepto P333 con AJUS SALARIO """
df_acumuladoAño.loc[df_acumuladoAño["CONCEPTO"] == "P333", "DESCRIPCIÓN"] = "AJUS SALARIO"

""" Lista de descripciones """
lista = [
    "SUELDO BASICO",
    "CALAMIDAD DOMESTICA",
    "DÍA FAMILIAR",
    "SANCION / SUSPENSION",
    "LICENCIA NO REMUN",
    "INASISTENCIA INJUST",
    "VACACIONES",
    "VACACIONES EN DINERO",
    "GASTO INCAPACIDAD",
    "LIC LEY MARIA 8 DIAS",
    "INCAPACIDAD ACC TRAB",
    "INCAP ENFERMEDAD GEN",
    "LICENCIA MATERNIDAD",
    "VAC HABILES SAL INT",
    "INCAPACIDAD AL 50%",
    "DÍA NO LAB DER A PAG",
    "RTEGRO DTO INASISTEN",
    "AJS  LICENCIA MATERN",
    "INCAP ENF GEN PRORR",    
    "VACACIONES FESTIVAS",
    "DTO SALARIO",
    "INASIS X INC > 180 D",
    "DTO INC ENF GRAL AL",
    "AJUS SALARIO"
]

""" Ejecutra funcion para crear columnas  """
resultados = df_acumulado.apply(
    lambda row: obtener_dias_conceptos_periodo_anterior(row, lista, df_acumuladoAño, nomMesAnterior),
    axis=1
)

df_resultados = pd.DataFrame(resultados.tolist(), index=df_acumulado.index)

""" Eliminar columnas cuyos nombres no están en la lista """
df_resultados = df_resultados.drop(columns=[col for col in lista if col in df_resultados.columns])

""" Añadir al DataFrame original """
df_acumulado = pd.concat([df_acumulado, df_resultados], axis=1)

""" Sumar las columnas de dias del mes anterior exluyendo vacaciones en dinero """
lista_suma = [desc for desc in lista if desc != "VACACIONES EN DINERO"]

""" Crear nombres de columnas del mes anterior """
columnas_mes_anterior = [desc + "_" + nomMesAnterior for desc in lista_suma]

""" Verificamos que columnas existan en el DataFrame """
columnas_existentes = [col for col in columnas_mes_anterior if col in df_acumulado.columns]

""" Crear columna con suma de dias de mes anterior """
df_acumulado["TOTAL_SUMA_DIAS_MESANTERIOR"] = df_acumulado[columnas_existentes].sum(axis=1)

"""  Asegurar que "VACACIONES EN DINERO_" exista (aunque no se sume)"""
col_vacaciones_dinero = "VACACIONES EN DINERO_" + nomMesAnterior
if col_vacaciones_dinero not in df_acumulado.columns:
    df_acumulado[col_vacaciones_dinero] = 0

# --------------- ACTUALIZAR VACACIONES MES ANTERIOR ---------------
""" Verificar vacaciones de mes anterior con días del mes anterior y actual """
if cDiasMesActual == 31:
    condicion = (
        (df_acumulado["ESTATUS_DIAS"] == "VALIDAR") &    
        (df_acumulado["EMPRESA"] == "SUPPLA S.A") &
        ((df_acumulado["TOTAL_SUMA_DIAS_MESANTERIOR"] + df_acumulado["DIAS_PAGO_NOMINA"]) == 60)
    )
elif cDiasMesActual == 30:
    condicion = (
        (df_acumulado["ESTATUS_DIAS"] == "VALIDAR") &    
        (df_acumulado["EMPRESA"] == "SUPPLA S.A") &
        ((df_acumulado["TOTAL_SUMA_DIAS_MESANTERIOR"] + df_acumulado["DIAS_PAGO_NOMINA"]) == (cDiasMesActual + cDiasMesAnterior))
    )
else:
    condicion = pd.Series([False] * len(df_acumulado))

""" Ejecutar actualizaciones """
dias_restantes = (
    cDiasMesActual - df_acumulado.loc[condicion, "DIAS_SUELDO_BASICO"].astype(int)
)

df_acumulado.loc[condicion, "ESTATUS_DIAS"] = "OK"
df_acumulado.loc[condicion, "OBSERVACION"] = (
    dias_restantes.astype(str) + " Dias Vacaciones Pagas Mes Anterior"
)

# --------------- VERIFICACION DIAS PAGOS MES ANTERIOR --------------- 
"""" Funcion para calcular dias no pagos del mes anterior """
def validar_nomina_mes_anterior(row, cDiasMesActual, nomMesAnterior):
    columna_sueldo_anterior = f"SUELDO BASICO_{nomMesAnterior.upper()}"
    
    if columna_sueldo_anterior not in row:
        return row
    
    sueldo_anterior = row.get(columna_sueldo_anterior, 0)

    if pd.notna(row["FECHA DE INGRESO"]) and sueldo_anterior == 0:
        dia_ingreso = row["FECHA DE INGRESO"].day
        dias_mes_anterior = (30 - dia_ingreso) + 1
        
        if (dias_mes_anterior + cDiasMesActual) == row.get("DIAS_PAGO_NOMINA", 0):
            row["ESTATUS_DIAS"] = "OK"
            row["OBSERVACION"] = f"30 Dias Trabajados {dias_mes_anterior} Dias Trabajados Mes Anterior"
    
    return row

""" Validar tipo de columna de fecha de ingreso """
df_acumulado["FECHA DE INGRESO"] = pd.to_datetime(df_acumulado["FECHA DE INGRESO"], errors="coerce")

""" Ejecutar funcion """
df_acumulado = df_acumulado.apply(
    lambda row: validar_nomina_mes_anterior(row, cDiasMesActual, nomMesAnterior),
    axis=1
)





















#Continue with change to Streamlit
# --------------- ANALISIS TEMPORALES MES ANTERIOR ---------------
""" cargar reporte de Horas para validar temporales """
df_infHe = pd.read_excel("Inf Ausentismo HE RN Consolidado 2025.xlsx", sheet_name="Ausentismo")

""" Filtrar data frame con mes actual """
df_temporales = df_infHe[df_infHe["Mes"] == nMesAnterior]
df_temporalesActual = df_infHe[df_infHe["Mes"] == nMesActual]


""" Crear columnas con descripciones de Novedad de mes anterior 
    y sumar 1 día si es de diferente semana """    

diccionario = {
    "Vacaciones": "DIAS_VACACIONES_TEMP",
    "Incapacidad E.G.": "DIAS_INCAPACIDAD_E.G_TEMP",
    "Licencia de paternidad": "DIAS_LIC_PATERNIDAD_TEMP",
    "Incapacidad A.T.": "DIAS_INCAPACIDAD_A.T_TEMP",
    "Asiste": "DIAS_LABORADOS_TEMP",
    "Permiso personal": "DIAS_PERMISO_PERSONAL_TEMP",
    "Dia Familiar Cumpleaños": "DIAS_FAMILIAR_TEMP",
    "Inasistencia injustificada": "DIAS_INASISTENCIA_INJUSTIFICADA_TEMP",
    "Suspensión de contrato": "DIAS_SUSPENSION_CONTRATO_TEMP",
    "Compensatorio": "DIAS_COMPENSATORIO_TEMP",
    "Cancelación turno cliente": "DIAS_CANCELACIÓN_TURNO_CLIENTE_TEMP",
    "Calamidad": "DIAS_CALAMIDAD_TEMP",
    "Licencia de luto": "DIAS_LICENCIA_LUTO_TEMP",
    "Capacitacion": "DIAS_CAPACITACIÓN_TEMP",
    "Día Familiar Fin de Año": "DIAS_FAMILIAR_FINAÑO_TEMP",
    "Urgencias, Triage o Citas Prioritarias EPS": "DIAS_CITA_PRIO_URG_TEMP",
    "Licencia no remunerada": "DIAS_LICENCIA_NOREMUN_TEMP"    
}

for columna in diccionario.values():
    if columna not in df_temporales.columns:
        df_temporales[columna] = None

def cuenta_dias(grupo):
    if "Identificacion" not in grupo.columns:
        grupo["Identificacion"] = None

    for descripcion, columna in diccionario.items():
        if descripcion == "Inasistencia injustificada":
            # Contar total de inasistencias injustificadas
            total_inasistencias = grupo.loc[grupo["Novedad"] == descripcion, "Identificacion"].count()
            # Contar semanas únicas en las que hubo inasistencias
            semanas_unicas = grupo.loc[grupo["Novedad"] == descripcion, "Sem"].nunique()
            # Sumamos los días + 1 adicional por cada semana distinta
            total_final = total_inasistencias + semanas_unicas
            
            if not grupo.empty:
                grupo.loc[grupo.index[0], columna] = total_final
                
                if columna not in grupo.columns:
                    grupo[columna] = None
        else:
            valor = grupo.loc[grupo["Novedad"] == descripcion, "Identificacion"].count()

            if not grupo.empty:
                grupo.loc[grupo.index[0], columna] = valor
    return grupo

def cuenta_dias_sin_grupo(grupo):
    grupo = grupo.copy()  # Para evitar SettingWithCopyWarning
    return cuenta_dias(grupo)

""" Ejecutar funcion para temporales """
df_temporales = df_temporales.groupby("Identificacion", group_keys=False).apply(cuenta_dias_sin_grupo)
df_temporales = df_temporales.reset_index(drop=True)

""" Ejecutar funcion para temporalesActual """
df_temporalesActual = df_temporalesActual.groupby("Identificacion", group_keys=False).apply(cuenta_dias_sin_grupo)
df_temporalesActual = df_temporalesActual.reset_index(drop=True)

""" eliminar repetidos en numero de identificación dejar el primero """
df_temporales = df_temporales.drop_duplicates(subset=["Identificacion"], keep="first")
df_temporalesActual = df_temporalesActual.drop_duplicates(subset=["Identificacion"], keep="first")

""" ELiminar columnas no necesarias """
diccionario = {
    "Mes",
    "Ciudad",
    "Operación",
    "Concatenado",
    "Sem",
    "Fecha",
    "Nombre",
    "Cargo",
    "Contrato",
    "Novedad",
    "Gestionable",
    "Gross?",    
}

df_temporales = df_temporales.drop(columns=[col for col in diccionario if col in df_temporales.columns])
df_temporalesActual = df_temporalesActual.drop(columns=[col for col in diccionario if col in df_temporalesActual.columns])

""" Merge Acumulados vs Temporales Mes Anterior"""
df_acumulado = fusionar_dataframes(
    df_izquierdo=df_acumulado,
    df_derecho=df_temporales,
    col_izq="NUMERO DOCUMENTO",
    col_der="Identificacion",
    como="left",
    nombre_union="Acumulado vs Temporales Mes Anterior"
)

# --------------- VALIDAR TEMPORALES CON INASISTENCIAS O INCAPACIDADES MES ANTERIOR ---------------
""" Funciona para validar inasistencias y actualizar Estatus Dias"""
def actualizar_estatus_temporales(df_acumulado, cDiasMesActual, columnas_suma, etiquetas_obs):
    # Asegurar columnas existen y sin NaN
    for col in columnas_suma:
        if col not in df_acumulado.columns:
            df_acumulado[col] = 0
        else:
            df_acumulado[col] = pd.to_numeric(df_acumulado[col], errors="coerce").fillna(0)

    if "ESTATUS_DIAS" not in df_acumulado.columns:
        df_acumulado["ESTATUS_DIAS"] = ""
    if "OBSERVACION" not in df_acumulado.columns:
        df_acumulado["OBSERVACION"] = ""
    if "EMPRESA" not in df_acumulado.columns:
        df_acumulado["EMPRESA"] = ""

    estatus_antes = df_acumulado["ESTATUS_DIAS"].copy()

    mask = (df_acumulado["ESTATUS_DIAS"] == "VALIDAR") & (df_acumulado["EMPRESA"] != "SUPPLA S.A")

    def evaluar_fila(row):
        suma = sum(row[col] for col in columnas_suma)
        if suma == cDiasMesActual:
            row["ESTATUS_DIAS"] = "OK"
            partes = []
            for col in columnas_suma:
                if row[col] > 0:
                    partes.append(f"{int(row[col])} {etiquetas_obs.get(col, col)}")
            row["OBSERVACION"] = " + ".join(partes)
        return row

    df_acumulado.loc[mask] = df_acumulado.loc[mask].apply(evaluar_fila, axis=1)

    nuevos_ok = (estatus_antes != "OK") & (df_acumulado["ESTATUS_DIAS"] == "OK")
    cantidad_nuevos = nuevos_ok.sum()


""" Actualizar estatus según suma de columnas de inasistencia """
columnas = [
    "DIAS_PAGO_NOMINA",
    "DIAS_INASISTENCIA_INJUSTIFICADA_TEMP",
    "DIAS_SUSPENSION_CONTRATO_TEMP",
    "DIAS_LICENCIA_NOREMUN_TEMP"
]

etiquetas = {
    "DIAS_PAGO_NOMINA": "Dias Trabajados",
    "DIAS_INASISTENCIA_INJUSTIFICADA_TEMP": "Dias Inasistencia Injust",
    "DIAS_SUSPENSION_CONTRATO_TEMP": "Dias Suspensión Contrato",
    "DIAS_LICENCIA_NOREMUN_TEMP": "Dias Licencia No Remun"
}

actualizar_estatus_temporales(df_acumulado, cDiasMesActual, columnas, etiquetas)

""" Actualizar estatus según suma de columnas de incapacidad """
columnas = [
    "DIAS_PAGO_NOMINA",
    "DIAS_INCAPACIDAD_E.G_TEMP",
    "DIAS_INCAPACIDAD_A.T_TEMP"
]

etiquetas = {
    "DIAS_PAGO_NOMINA": "Dias Trabajados",
    "DIAS_INCAPACIDAD_E.G_TEMP": "Dias Incapacidad E.G",
    "DIAS_INCAPACIDAD_A.T_TEMP": "Dias Incapacidad A.T"
}

actualizar_estatus_temporales(df_acumulado, cDiasMesActual, columnas, etiquetas)

#---------------- ACTUALIZAR ESTATUS SI CUMPLE CONDICIONES ---------------
""" Funcion para actualizar segun condiciones de columnas """
def actualizar_estatus_observacion(df, condicion, nuevo_estatus, nueva_observacion):    
    afectados = condicion.sum()
    df.loc[condicion, "ESTATUS_DIAS"] = nuevo_estatus
    df.loc[condicion, "OBSERVACION"] = nueva_observacion

""" Actualizar dias negativos de temporales y con retiro """
condicionales = (
    (df_acumulado["ESTATUS_DIAS"] == "VALIDAR") &    
    (df_acumulado["EMPRESA"] != "SUPPLA S.A") &
    (df_acumulado["OBSERVACION"] == "Validar Retiro") &
    (df_acumulado["DIAS_PAGO_NOMINA"] < 0)
)

actualizar_estatus_observacion(
    df=df_acumulado,
    condicion=condicionales,
    nuevo_estatus="OK",
    nueva_observacion="Nota Crédito del Mes de Retiro"
)

""" Actualizar dias 0 en temporales y con retiro """
condicionales = (
    (df_acumulado["ESTATUS_DIAS"] == "VALIDAR") &    
    (df_acumulado["EMPRESA"] != "SUPPLA S.A") &
    (df_acumulado["OBSERVACION"] == "Validar Retiro") &
    (df_acumulado["DIAS_PAGO_NOMINA"] == 0)
)

actualizar_estatus_observacion(
    df=df_acumulado,
    condicion=condicionales,
    nuevo_estatus="OK",
    nueva_observacion="Pagos Pendientes en Liquidación"
)

# --------------- VALIDAR TEMPORALES CON NOMINA ANTERIOR ---------------
""" Merge Acumulado vs ConsoNomina """
df_acumulado = fusionar_dataframes(
    df_izquierdo=df_acumulado,
    df_derecho=df_consoNomina,
    col_izq="NUMERO DOCUMENTO",
    col_der="CEDULA",
    como="left",
    nombre_union="Acumulado vs ConsoNomina"
)

""" Crear Columna de mes de Ingreso """
df_acumulado["FECHA DE INGRESO"] = pd.to_datetime(df_acumulado["FECHA DE INGRESO"], errors="coerce")

""" Obtener nombre de mes """
df_acumulado["MES_INGRESO"] = df_acumulado["FECHA DE INGRESO"].dt.month.map(lambda x: meses[x - 1] if pd.notna(x) else None)

""" Actualizar Temporales con Ingreso Mes Anterior y Sin Pago """
condicionales = (
    (df_acumulado["ESTATUS_DIAS"] == "VALIDAR") &    
    (df_acumulado["EMPRESA"] != "SUPPLA S.A") &
    (df_acumulado["MES_INGRESO"] == nomMesAnterior) &
    (df_acumulado["CEDULA"].isna() | (df_acumulado["CEDULA"] == ""))
)

actualizar_estatus_observacion(
    df=df_acumulado,
    condicion=condicionales,
    nuevo_estatus="OK",
    nueva_observacion="Se Facturan Dias Desde Su Fecha de Ingreso"
)

""" Actualizar Temporales PT con Incapacidades del mes Anterior """
condicionales = (
    (df_acumulado["ESTATUS_DIAS"] == "VALIDAR") &    
    (df_acumulado["EMPRESA"] != "SUPPLA S.A") &
    (df_acumulado["SALARIO MENSUAL"] < salario) &
    (
        (df_acumulado["DIAS_INCAPACIDAD_E.G_TEMP"] > 0) | 
        (df_acumulado["DIAS_INCAPACIDAD_A.T_TEMP"] > 0)
    )
)

suma_dias_incapacidad = (
    df_acumulado.loc[condicionales, "DIAS_INCAPACIDAD_E.G_TEMP"].fillna(0) + 
    df_acumulado.loc[condicionales, "DIAS_INCAPACIDAD_A.T_TEMP"].fillna(0)
).astype(int).astype(str) + " Días Incapacidad, Pagos al 100%"


df_acumulado.loc[condicionales, "ESTATUS_DIAS"] = "OK"
df_acumulado.loc[condicionales, "OBSERVACION"] = suma_dias_incapacidad
df_acumulado.loc[condicionales, "DIAS_PAGO_NOMINA"] = cDiasMesActual


# --------------- MERGE CON BASE NACIONAL DE PERSONAL ---------------
""" Eliminar Columnas """
df_personalNacionalCopy = eliminar(df_personalNacional, "CARGO NÓMINA", "FECHA DE INGRESO")

""" Merge Acumulado vs Base Personal Nacional """
df_acumulado = fusionar_dataframes(
    df_izquierdo=df_acumulado,
    df_derecho=df_personalNacionalCopy,
    col_izq="NUMERO DOCUMENTO",
    col_der="ID",
    como="left",
    nombre_union="Acumulado vs Copia Base Personal Nacional"
)

""" Actualizar Fecha de Retiro """
df_acumulado["FECHA DE BAJA"] = pd.to_datetime(df_acumulado["FECHA DE BAJA"], errors="coerce")
df_acumulado["FECHA DE RETIRO"] = pd.to_datetime(df_acumulado["FECHA DE RETIRO"], errors="coerce")


condicionales = (
    (df_acumulado["ESTATUS_DIAS"] == "VALIDAR") &
    (df_acumulado["EMPRESA"] != "SUPPLA S.A") &
    (df_acumulado["FECHA DE BAJA"].notna()) &
    (df_acumulado["FECHA DE RETIRO"].notna()) &
    (df_acumulado["FECHA DE BAJA"] < df_acumulado["FECHA DE RETIRO"])
)

df_acumulado.loc[condicionales, "FECHA DE BAJA"] = df_acumulado.loc[condicionales, "FECHA DE RETIRO"]

""" Actualizar la columna Estatus días para realizar cálculos """
condicion = df_acumulado["ESTATUS_DIAS"] == "VALIDAR"

df_acumulado.loc[condicion, "DIFERENCIA_DIAS"] = (
    (df_acumulado.loc[condicion, "FECHA DE BAJA"] - df_acumulado.loc[condicion, "FECHA_INICIO_MES"])
    .dt.days + 1
)

""" Actualizar Temporales con Retiro en Mismo Mes """
condicionales = (
    (df_acumulado["ESTATUS_DIAS"] == "VALIDAR") &    
    (df_acumulado["EMPRESA"] != "SUPPLA S.A") &
    ((df_acumulado["DIAS_PAGO_NOMINA"] + df_acumulado["DIAS_INASISTENCIA_INJUSTIFICADA_TEMP"])==(df_acumulado["FECHA DE BAJA"] - df_acumulado["FECHA_INICIO_MES"]).dt.days+1)
    
)


actualizar_estatus_observacion(
    df=df_acumulado,
    condicion=condicionales,
    nuevo_estatus="OK",
    nueva_observacion="Empleado con Retiro en Mismo Mes"
)

""" Actualizar temporales con retiros el mismo mes """
condicionales = (
    (df_acumulado["ESTATUS_DIAS"] == "VALIDAR") &
    (df_acumulado["EMPRESA"] != "SUPPLA S.A") &
    (df_acumulado["DIFERENCIA_DIAS"] == df_acumulado["DIAS_PAGO_NOMINA"])
)

actualizar_estatus_observacion(
    df=df_acumulado,
    condicion=condicionales,
    nuevo_estatus="OK",
    nueva_observacion="Empleado con Retiro en Mismo Mes"
)

""" Cambiar nombre de columna con días de inasitencias de temporales """
df_acumulado = df_acumulado.rename(
    columns={"DIAS_INASISTENCIA_INJUSTIFICADA_TEMP": "DIAS_INASISTENCIAS_TEMPORALES_MESANTERIOR"}
)

""" Eliminar Columnas """
df_acumulado = eliminar(df_acumulado, "FECHA DE RETIRO", "ID",
                        "SALARIO BASICO","CARGO NOMINA","CEDULA",
                        "DIAS_LICENCIA_NOREMUN_TEMP","DIAS_CITA_PRIO_URG_TEMP",
                        "DIAS_FAMILIAR_FINAÑO_TEMP","DIAS_CAPACITACIÓN_TEMP",
                        "DIAS_LICENCIA_LUTO_TEMP","DIAS_CALAMIDAD_TEMP",
                        "DIAS_CANCELACIÓN_TURNO_CLIENTE_TEMP","DIAS_COMPENSATORIO_TEMP",
                        "DIAS_SUSPENSION_CONTRATO_TEMP","DIAS_INCAPACIDAD_E.G_TEMP",
                        "DIAS_FAMILIAR_TEMP","DIAS_PERMISO_PERSONAL_TEMP","DIAS_LABORADOS_TEMP",
                        "DIAS_LIC_PATERNIDAD_TEMP","DIAS_INCAPACIDAD_A.T_TEMP",
                        "DIAS_VACACIONES_TEMP",
                        "TOTAL_SUMA_DIAS_MESANTERIOR","DTO INC ENF GRAL AL_MAYO",
                        "INASIS X INC > 180 D_MAYO","DTO SALARIO_MAYO",
                        "VACACIONES FESTIVAS_MAYO","INCAP ENF GEN PRORR_MAYO",
                        "AJS  LICENCIA MATERN_MAYO","RTEGRO DTO INASISTEN_MAYO",
                        "DÍA NO LAB DER A PAG_MAYO","INCAPACIDAD AL 50%_MAYO",
                        "VAC HABILES SAL INT_MAYO","LICENCIA MATERNIDAD_MAYO",
                        "INCAP ENFERMEDAD GEN_MAYO","INCAPACIDAD ACC TRAB_MAYO",
                        "LIC LEY MARIA 8 DIAS_MAYO","GASTO INCAPACIDAD_MAYO",
                        "VACACIONES EN DINERO_MAYO","VACACIONES_MAYO",
                        "INASISTENCIA INJUST_MAYO","LICENCIA NO REMUN_MAYO",
                        "SANCION / SUSPENSION_MAYO","DÍA FAMILIAR_MAYO",
                        "SUELDO BASICO_MAYO","Observacion", "Identificacion")

""" Eliminar identifiacación del index """
if "Identificacion" in df_temporalesActual.index.names:
    df_temporalesActual = df_temporalesActual.reset_index(drop=True)

if "Identificacion" in df_acumulado.index.names:
    df_acumulado = df_acumulado.reset_index(drop=True)

# --------------- VALIDAR TEMPORALES DEL MES ACTUAL ---------------
""" Merge Acumulados vs Temporales Mes Actual"""
df_acumulado = fusionar_dataframes(
    df_izquierdo=df_acumulado,
    df_derecho=df_temporalesActual,
    col_izq="NUMERO DOCUMENTO",
    col_der="Identificacion",
    como="left",
    nombre_union="Acumulado vs Temporales Mes Actual"
)

""" Actualizar Temporales PT con Incapacidades del mes Actual """
condicionales = (
    (df_acumulado["ESTATUS_DIAS"] == "VALIDAR") &    
    (df_acumulado["EMPRESA"] != "SUPPLA S.A") &
    (df_acumulado["SALARIO MENSUAL"] < salario) &
    (
        (df_acumulado["DIAS_INCAPACIDAD_E.G_TEMP"] > 0) | 
        (df_acumulado["DIAS_INCAPACIDAD_A.T_TEMP"] > 0)
    )
)

suma_dias_incapacidad = (
    df_acumulado.loc[condicionales, "DIAS_INCAPACIDAD_E.G_TEMP"].fillna(0) + 
    df_acumulado.loc[condicionales, "DIAS_INCAPACIDAD_A.T_TEMP"].fillna(0)
).astype(int).astype(str) + " Días Incapacidad, Pagos al 100%"

df_acumulado.loc[condicionales, "ESTATUS_DIAS"] = "OK"
df_acumulado.loc[condicionales, "OBSERVACION"] = suma_dias_incapacidad
df_acumulado.loc[condicionales, "DIAS_PAGO_NOMINA"] = cDiasMesActual


#%% Celda Oculta

""" Eliminar Variables y Columnas """
eliminar(globals(), "columna")
eliminar(globals(), "columnas")
eliminar(globals(), "columnas_existentes")
eliminar(globals(), "columnas_mes_anterior")
eliminar(globals(), "cond")
eliminar(globals(), "condicion")
eliminar(globals(), "condicionales")
eliminar(globals(), "df_acumuladoAño")
eliminar(globals(), "df_cifrasMes")
eliminar(globals(), "df_consoNomina")
eliminar(globals(), "df_infHe")
eliminar(globals(), "df_personalNacional")
eliminar(globals(), "df_personalNacionalCopy")
eliminar(globals(), "df_resultados")
eliminar(globals(), "df_summ_Acumulado")
eliminar(globals(), "df_temporales")
eliminar(globals(), "df_temporalesActual")
eliminar(globals(), "dias_restantes")
eliminar(globals(), "diccionario")
eliminar(globals(), "etiquetas")
eliminar(globals(), "fecha_vacia")
eliminar(globals(), "lista")
eliminar(globals(), "mascara_codigos")
eliminar(globals(), "primer_valor")
eliminar(globals(), "resultados")
eliminar(globals(), "suma_dias_incapacidad")
eliminar(globals(), "totales_columnas")
eliminar(globals(), "verificacion")
eliminar(globals(), "df_summ_acumulado")
eliminar(globals(), "mascara_actualizar")


""" Crear columna de Dias Vacaciones """
df_acumulado["DIAS VACACIONES"] = df_acumulado["DIAS_VACACIONES"]+df_acumulado["DIAS_VACACIONES_FESTIVAS"]

""" Eliminar Columnas """
df_acumulado = eliminar(df_acumulado, "DIAS_SUELDO_BASICO",
                        "DIAS_FAMILIAR","DIAS_SANCION_/_SUSPENSION",
                        "DIAS_LICENCIA_NO_REMUN","DIAS_LICENCIA_MATERNIDAD",
                        "DIAS_AJS_LICENCIA_MATERN","DIAS_INASISTENCIA_INJUST",
                        "DIAS_VACACIONES","DIAS_VACACIONES_FESTIVAS",
                        "DIAS_VACACIONES_DINERO","DIAS_GASTO_INCAPACIDAD",
                        "DIAS_LIC_LEY_MARIA_8_DIAS","DIAS_INCAPACIDAD_ACC_TRAB",
                        "DIAS_INCAP_ENFERMEDAD_GEN","DIAS_VAC_HABILES_SAL_INT",
                        "DIAS_INCAPACIDAD_AL_50%","DIAS_DÍA_NO_LAB_DER_A_PAG",
                        "DIAS_RTEGRO_DTO_INASISTEN","DIAS_DTO_SALARIO",
                        "DIAS_INASIS_X_INC_>_180_D","DIAS_INCAP_ENF_GEN_PRORR",
                        "DIAS_DTO_INC_ENF_GRAL_AL","Identificacion",
                        "DIAS_VACACIONES_TEMP","DIAS_INCAPACIDAD_E.G",
                        "DIAS_LIC_PATERNIDAD","DIAS_INCAPACIDAD_A.T",
                        "DIAS_LABORADOS","DIAS_PERMISO_PERSONAL",
                        "DIAS_FAMILIAR_TEMP","DIAS_INASISTENCIA_INJUSTIFICADA",
                        "DIAS_SUSPENSION_CONTRATO","DIAS_COMPENSATORIO",
                        "DIAS_CANCELACIÓN_TURNO_CLIENTE","DIAS_CALAMIDAD",
                        "DIAS_LICENCIA_LUTO","DIAS_CAPACITACIÓN",
                        "DIAS_FAMILIAR_FINAÑO","DIAS_CITA_PRIO_URG",
                        "DIAS_LICENCIA_NOREMUN"
)


#------------------------- VALIDACION PRORRATEOS --------------------------
""" Leer archivo de Novedades Nomina """
df_novedades_nom = cargar_excel("Cambios Nomina.xlsx", sheet="Data")
df_codProrrateo = cargar_excel("Agrupaciones.xlsx", sheet="Cod_Prorrateo")
df_codCCostos = cargar_excel("Agrupaciones.xlsx", sheet="Centros Costos")
df_codCargos = cargar_excel("Agrupaciones.xlsx", sheet="Cargos")

""" Eliminar duplicados """
df_novedades_nom = df_novedades_nom.drop_duplicates(subset="CEDULA", keep="first")

""" Filtrar Acumulado según registros de Novedades de Nomina """
df_acumuladoNov = df_acumulado[df_acumulado["NUMERO DOCUMENTO"].isin(df_novedades_nom["CEDULA"])].copy()

""" Eliminar Columnas """
df_novedades_nom = eliminar(df_novedades_nom, "MES")

""" Merge Acumulado Nov vs Novedades Nomina """
df_acumuladoNov = fusionar_dataframes(
    df_izquierdo=df_acumuladoNov,
    df_derecho=df_novedades_nom,
    col_izq="NUMERO DOCUMENTO",
    col_der="CEDULA",
    como="left",
    nombre_union="Acumulado Nov vs Novedades Nomina"
)


#-------------- CREAR DICCIONARIO PARA REALIZAR INSTRUCCIONES DE PRORRATEO --------
def crear_diccionario_por_fila(fila):
    if pd.isna(fila["TIPO DE CAMBIO"]) or str(fila["TIPO DE CAMBIO"]).strip() == "":
        return {}

    tipos = [x.strip() for x in str(fila["TIPO DE CAMBIO"]).split(";")]
    porcentaje = [x.strip() for x in str(fila.get("PORCENTAJE PR", "")).split(";")]
    cantidad = [x.strip() for x in str(fila.get("CANTIDAD PR", "")).split(";")]
    operacion = [x.strip() for x in str(fila.get("OPERACIÓN CAMBIO", "")).split(";")]
    cargo = [x.strip() for x in str(fila.get("CARGO CAMBIO", "")).split(";")]

    def es_valido(valor):
        return valor not in [None, "", "NA", "nan"] and not pd.isna(valor) and str(valor).lower() != "nan"

    resultado = {}

    for i, tipo in enumerate(tipos):
        subdict = {}

        if i < len(porcentaje) and es_valido(porcentaje[i]):
            subdict["PORCENTAJE PR"] = porcentaje[i]

        if i < len(cantidad) and es_valido(cantidad[i]):
            subdict["CANTIDAD PR"] = cantidad[i]

        if i < len(operacion) and es_valido(operacion[i]):
            subdict["OPERACIÓN CAMBIO"] = operacion[i]

        if i < len(cargo) and es_valido(cargo[i]):
            subdict["CARGO CAMBIO"] = cargo[i]

        if subdict:
            resultado[tipo] = subdict

    return resultado


#------------------------- FUNCION PARA REALIZAR PRORRATEOS -----------------------
def aplicar_cambios_final(fila, df_codProrrateo, df_codCargos, df_codCCostos):
    if fila is None:
        return None, []

    nuevas_filas = []
    cambios = fila.get("CAMBIOS_DETALLE", {}).copy()

    conceptos_prorrateo = df_codProrrateo["CONCEPTO"].tolist()
    columnas_sap_prst = df_codProrrateo[df_codProrrateo["CODIGO"].isin(["SAP", "PRST"])]["CONCEPTO"].tolist()
    columnas_no_sap_prst = df_codProrrateo[~df_codProrrateo["CODIGO"].isin(["SAP", "PRST"])]["CONCEPTO"].tolist()

    cod_centro_costos = fila.get("CENTRO DE COSTOS", None)
    if cod_centro_costos is not None:
        fila_costos_actual = df_codCCostos[df_codCCostos["CENTRO DE COSTOS"] == cod_centro_costos]
        if not fila_costos_actual.empty:
            for col in fila_costos_actual.columns:
                if col in fila:
                    fila[col] = fila_costos_actual.iloc[0][col]

    if "CAMBIO DE CARGO" in cambios:
        detalle = cambios.pop("CAMBIO DE CARGO")
        porcentaje_raw = str(detalle.get("PORCENTAJE PR", "")).replace("%", "").strip()
        nuevo_cargo = detalle.get("CARGO CAMBIO", "").strip()
        try:
            porcentaje_float = float(porcentaje_raw)
        except:
            porcentaje_float = 0

        if porcentaje_float >= 1 and nuevo_cargo:
            fila_cargo = df_codCargos[df_codCargos["CARGO MELI"] == nuevo_cargo]
            if not fila_cargo.empty:
                for col in fila_cargo.columns:
                    if col in fila:
                        fila[col] = fila_cargo.iloc[0][col]

    if "PRORRATEO OPERACIÓN" in cambios:
        detalle = cambios.pop("PRORRATEO OPERACIÓN")
        porc = str(detalle.get("PORCENTAJE PR", "")).replace("%", "").strip()
        operaciones_raw = detalle.get("OPERACIÓN CAMBIO", "")
        if porc:
            try:
                porcentaje_total = float(porc) / 100
            except:
                porcentaje_total = None

            if porcentaje_total:
                operaciones = [op.strip() for op in operaciones_raw.split("-")] if operaciones_raw else []
                n_ops = len(operaciones) if operaciones else 1
                porc_unitario = porcentaje_total / n_ops

                for op in operaciones or [None]:
                    nueva = fila.copy()
                    for col in conceptos_prorrateo:
                        if col in nueva and pd.notna(nueva[col]):
                            try:
                                nueva[col] = float(nueva[col]) * porc_unitario
                            except:
                                pass

                    if op:
                        nueva["OPERACION"] = op
                        fila_costos = df_codCCostos[df_codCCostos["CODIGO"] == op]
                        if not fila_costos.empty:
                            for col in fila_costos.columns:
                                if col in nueva:
                                    nueva[col] = fila_costos.iloc[0][col]

                    nueva["TIPO_CAMBIO"] = "PRORRATEO OPERACIÓN"
                    nueva["PORCENTAJE APLICADO"] = f"{porc_unitario:.2%}"
                    nueva["CAMBIOS_DETALLE"] = cambios.copy()
                    nuevas_filas.append(nueva)

                fila = None

    if "PRORRATEO DIAS" in cambios:
        detalle = cambios.pop("PRORRATEO DIAS")
        cantidad_dias = detalle.get("CANTIDAD PR")
        operacion = detalle.get("OPERACIÓN CAMBIO")

        try:
            dias_prorratear = float(cantidad_dias)
        except:
            dias_prorratear = None

        if dias_prorratear and fila is not None:
            nueva = fila.copy()
            dias_pago_total = fila.get("DIAS_PAGO_NOMINA", 0)
            try:
                dias_pago_total = float(dias_pago_total)
                proporcion = dias_prorratear / dias_pago_total if dias_pago_total > 0 else 0
            except:
                proporcion = 0

            for col in columnas_sap_prst:
                if col in nueva and pd.notna(nueva[col]):
                    try:
                        monto = float(nueva[col])
                        nueva[col] = monto * proporcion
                        fila[col] = monto - nueva[col]
                    except:
                        pass

            for col in columnas_no_sap_prst:
                if col in nueva and pd.notna(nueva[col]):
                    nueva[col] = 0

            if "DIAS_PAGO_NOMINA" in fila:
                try:
                    fila["DIAS_PAGO_NOMINA"] = float(fila["DIAS_PAGO_NOMINA"]) - dias_prorratear
                except:
                    pass

            nueva["DIAS_PAGO_NOMINA"] = dias_prorratear

            if operacion:
                nueva["OPERACION"] = operacion
                fila_costos = df_codCCostos[df_codCCostos["CODIGO"] == operacion]
                if not fila_costos.empty:
                    for col in fila_costos.columns:
                        if col in nueva:
                            nueva[col] = fila_costos.iloc[0][col]

            nueva["TIPO_CAMBIO"] = "PRORRATEO DIAS"
            nueva["PORCENTAJE APLICADO"] = f"{proporcion:.2%}"
            nueva["CAMBIOS_DETALLE"] = cambios.copy()
            nuevas_filas.append(nueva)

    if fila is not None:
        fila["CAMBIOS_DETALLE"] = cambios

    return fila, nuevas_filas

#--------------------------- FUNCION PARA PRORRATEO DE RN --------------------------
def aplicar_prorrateo_rn(df_acumuladoNov, df_codProrrateo):
    conceptos_rn = df_codProrrateo[df_codProrrateo["CODIGO"] == "RN"]["CONCEPTO"].tolist()
    conceptos_no_rn = df_codProrrateo[df_codProrrateo["CODIGO"] != "RN"]["CONCEPTO"].tolist()

    for documento, grupo in df_acumuladoNov.groupby("NUMERO DOCUMENTO"):
        filas_cambios = grupo[grupo["CAMBIOS_DETALLE"].apply(lambda x: isinstance(x, dict) and "PRORRATEO RN" in x)]

        for idx, fila in filas_cambios.iterrows():
            detalle = fila["CAMBIOS_DETALLE"]["PRORRATEO RN"]
            operacion_cambio = detalle.get("OPERACIÓN CAMBIO")
            porcentaje_raw = detalle.get("PORCENTAJE PR", "100%").replace("%", "").strip()

            try:
                porcentaje_float = float(porcentaje_raw)
            except:
                porcentaje_float = 100.0

            operaciones_destino = [op.strip() for op in operacion_cambio.split("-")]
            proporcion = porcentaje_float / 100
            n_ops = len(operaciones_destino)
            proporcion_unitaria = proporcion if n_ops == 1 else proporcion / n_ops

            subset = df_acumuladoNov[df_acumuladoNov["NUMERO DOCUMENTO"] == documento]
            sumas = subset[conceptos_rn].sum(numeric_only=True)

            for j, (idx2, fila2) in enumerate(subset.iterrows()):
                if fila2["OPERACION"] in operaciones_destino:
                    for col in conceptos_rn:
                        df_acumuladoNov.at[idx2, col] = sumas[col] * proporcion_unitaria
                    for col in conceptos_no_rn:
                        if col in df_acumuladoNov.columns:
                            df_acumuladoNov.at[idx2, col] = 0
                else:
                    for col in conceptos_rn:
                        df_acumuladoNov.at[idx2, col] = 0

            # Marcar el tipo de cambio en la fila original
            tipo_cambio_actual = str(df_acumuladoNov.at[idx, "TIPO_CAMBIO"])
            nuevo_valor = "PRORRATEO RN"
            if tipo_cambio_actual and tipo_cambio_actual.strip() not in ["", "nan", "NaN"]:
                df_acumuladoNov.at[idx, "TIPO_CAMBIO"] = tipo_cambio_actual.strip() + "; " + nuevo_valor
            else:
                df_acumuladoNov.at[idx, "TIPO_CAMBIO"] = nuevo_valor

            df_acumuladoNov.at[idx, "CAMBIOS_DETALLE"].pop("PRORRATEO RN", None)

    return df_acumuladoNov

# Aplicar la función crear_diccionario_por_fila
df_acumuladoNov["CAMBIOS_DETALLE"] = df_acumuladoNov.apply(crear_diccionario_por_fila, axis=1)

# Lista para almacenar nuevas filas
filas_nuevas = []

# Aplicar cambios uno por uno por fila
for i in df_acumuladoNov.index:
    fila_original = df_acumuladoNov.loc[i].copy()
    fila_modificada, nuevas = aplicar_cambios_final(fila_original, df_codProrrateo, df_codCargos, df_codCCostos)

    if fila_modificada is not None:
        df_acumuladoNov.loc[i] = fila_modificada
    else:
        df_acumuladoNov.drop(index=i, inplace=True)

    filas_nuevas.extend(nuevas)

# Agregar las nuevas filas al DataFrame
if filas_nuevas:
    df_acumuladoNov = pd.concat([df_acumuladoNov, pd.DataFrame(filas_nuevas)], ignore_index=True)

# Aplicar el prorrateo RN final
df_acumuladoNov = aplicar_prorrateo_rn(df_acumuladoNov, df_codProrrateo)

#----------------- FUNCION PARA REALIZAR EL CAMBIO DE FT A PT --------------------
def aplicar_cambio_pt_a_ft(df_acumuladoNov, df_codCargos, df_codProrrateo):
    nuevas_filas = []

    columnas_sap_prst = df_codProrrateo[df_codProrrateo["CODIGO"].isin(["SAP", "PRST"])]["CONCEPTO"].tolist()
    columnas_no_sap_prst = df_codProrrateo[~df_codProrrateo["CODIGO"].isin(["SAP", "PRST"])]["CONCEPTO"].tolist()

    for idx, fila in df_acumuladoNov[df_acumuladoNov["CAMBIOS_DETALLE"].apply(lambda x: isinstance(x, dict) and "CAMBIO PT A FT" in x)].iterrows():
        detalle = fila["CAMBIOS_DETALLE"]["CAMBIO PT A FT"]
        cantidad_pr = detalle.get("CANTIDAD PR", "").strip()
        nuevo_cargo = detalle.get("CARGO CAMBIO", "").strip()

        try:
            cantidad_pr = float(cantidad_pr)
        except:
            continue  # Saltar si no es un número

        try:
            dias_actuales = float(fila["DIAS_PAGO_NOMINA"])
        except:
            dias_actuales = 0

        if cantidad_pr <= 0 or cantidad_pr > dias_actuales:
            continue  # No se puede prorratear más de lo que tiene

        dias_restantes = dias_actuales - cantidad_pr
        proporcion_nueva = cantidad_pr / dias_actuales
        proporcion_original = dias_restantes / dias_actuales if dias_actuales > 0 else 0

        # Crear copia modificada con nuevo cargo y días prorrateados
        nueva_fila = fila.copy()
        nueva_fila["DIAS_PAGO_NOMINA"] = cantidad_pr

        # Prorrateo columnas SAP/PRST
        for col in columnas_sap_prst:
            if col in fila and pd.notna(fila[col]):
                try:
                    valor_total = float(fila[col])
                    valor_nuevo = valor_total * proporcion_nueva
                    valor_original = valor_total * proporcion_original
                    nueva_fila[col] = valor_nuevo
                    df_acumuladoNov.at[idx, col] = valor_original
                except:
                    pass

        # Columnas que no son SAP/PRST en la nueva fila = 0
        for col in columnas_no_sap_prst:
            if col in nueva_fila:
                nueva_fila[col] = 0

        # Ajustar días de la fila original en el DataFrame
        df_acumuladoNov.at[idx, "DIAS_PAGO_NOMINA"] = dias_restantes

        # Buscar datos del nuevo cargo y reemplazar columnas
        fila_cargo = df_codCargos[df_codCargos["CARGO MELI"] == nuevo_cargo]
        if not fila_cargo.empty:
            for col in fila_cargo.columns:
                if col in nueva_fila:
                    nueva_fila[col] = fila_cargo.iloc[0][col]

        # Actualizar tipo de cambio en original (concatenar si ya hay uno)
        tipo_cambio_actual = str(df_acumuladoNov.at[idx, "TIPO_CAMBIO"])
        nuevo_tipo = "CAMBIO PT A FT"
        if tipo_cambio_actual and tipo_cambio_actual.strip().lower() not in ["", "nan"]:
            df_acumuladoNov.at[idx, "TIPO_CAMBIO"] = tipo_cambio_actual.strip() + "; " + nuevo_tipo
        else:
            df_acumuladoNov.at[idx, "TIPO_CAMBIO"] = nuevo_tipo

        # Limpiar instrucción en original
        df_acumuladoNov.at[idx, "CAMBIOS_DETALLE"].pop("CAMBIO PT A FT", None)

        # Limpiar instrucción en nueva fila también
        nueva_cambios = fila["CAMBIOS_DETALLE"].copy()
        nueva_cambios.pop("CAMBIO PT A FT", None)
        nueva_fila["CAMBIOS_DETALLE"] = nueva_cambios

        nueva_fila["TIPO_CAMBIO"] = nuevo_tipo
        nueva_fila["PORCENTAJE APLICADO"] = f"{proporcion_nueva:.2%}"

        nuevas_filas.append(nueva_fila)

    # Agregar nuevas filas al dataframe
    if nuevas_filas:
        df_acumuladoNov = pd.concat([df_acumuladoNov, pd.DataFrame(nuevas_filas)], ignore_index=True)

    return df_acumuladoNov

df_acumuladoNov = aplicar_cambio_pt_a_ft(df_acumuladoNov, df_codCargos, df_codProrrateo)

""" Concatenar df_acumulado vs df_acumuladoNov """
df_nominaProrrateos = pd.concat([df_acumulado, df_acumuladoNov], axis=0)

""" Eliminar Columnas """
df_nominaProrrateos = eliminar(df_nominaProrrateos, "TIPO DE CARGO","TIPO DE DOTACION")

"""Eliminar duplicados """
df_nominaProrrateos = df_nominaProrrateos.drop_duplicates(subset="NUMERO DOCUMENTO", keep="first")

""" Cargar df de Base de Personal Nacional """
df_personalNacional = cargar_excel("Base Personal Nacional.xlsx", sheet="BD Personal DHL")

""" Dejar columnas necesarias """
df_personalNacional = df_personalNacional[["ID", "CARGO MELI",]]

""" Eliminar duplicados """
df_personalNacional = df_personalNacional.drop_duplicates(subset=["ID"], keep="last")

""" Merge Acumulado Nov vs Novedades Nomina """
df_nominaProrrateos = fusionar_dataframes(
    df_izquierdo=df_nominaProrrateos,
    df_derecho=df_personalNacional,
    col_izq="NUMERO DOCUMENTO",
    col_der="ID",
    como="left",
    nombre_union="Nomina Prorrateo vs Personal Nacional"
)

""" Merge entre df_nominaProrrateos y df_codCargos """
df_merge = df_nominaProrrateos.merge(
    df_codCargos, 
    how="left",
    left_on="CARGO MELI_y", 
    right_on="CARGO MELI",
    suffixes=("", "_cod")
)

# Idnetificar columnas existentes entre df
columnas_actualizables = list(
    set(df_nominaProrrateos.columns).intersection(df_codCargos.columns)
)
columnas_actualizables = [col for col in columnas_actualizables if col != "CARGO MELI"]  # evitar la clave

# Actualizar valores
for col in columnas_actualizables:
    df_merge[col] = df_merge[f"{col}_cod"].combine_first(df_merge[col])

# Eliminar columnas adicionales del merge 
df_nominaProrrateos = df_merge[df_nominaProrrateos.columns]

# Ordenar df
df_nominaProrrateos = df_nominaProrrateos[["EMPRESA", "TIPO_DE_VINCULACIÓN",
                                         "MES","CENTRO DE COSTOS","NOMBRE CENTRO DE COSTOS",
                                         "POBLACIÓN","NUMERO DOCUMENTO","NOMBRE COMPLETO",
                                         "CARGO NOMINA_x","CARGO MELI_y","TIPO_DE_DOTACION",
                                         "TIPO_DE_CARGO","FECHA DE INGRESO","FECHA DE BAJA",
                                         "SALARIO MENSUAL","DIAS_PAGO_NOMINA","DIAS VACACIONES",
                                         "SALARIO_A_PAGAR","SUBSIDIO_TRANSPORTE","HRS_HORA_EXTRA_DIURNA - 1,25",
                                         "VR._HORA_EXTRA_DIURNA - 1,25","HRS._HORA_EXTRA_NOCTURNA - 1,75",
                                         "VR._HORA_EXTRA_NOCTURNA - 1,75","NO.HORA_ORD_DOMINICAL_175",
                                         "VR.HORA_ORD_DOMINICAL_175","HRS._EXTRA_HORA_DOM/FEST._NOCTURNA_2.50%",
                                         "VR._EXTRA_HORA_DOM/FEST._NOCTURNA_2.50%","HRS._HORA_EXTRA_DOMINICAL_Y_FESTIVA_DIURNA_2.00%",
                                         "VR._HORA_EXTRA_DOMINICAL_Y_FESTIVA_DIURNA_2.00%","TOTAL # H.E.",
                                         "TOTAL_HORAS_EXTRAS_SIN_R.N.","HRS._DOMINICAL_DIURNO - 1,75",
                                         "VR._DOMINICAL_DIURNO - 1,75","HRS._FESTIVO_DIURNO - 1,75",
                                         "VR._FESTIVO_DIURNO - 1,75","HRS. RECARGO DOMINICAL NOCTURNO - 2,1",
                                         "VR._RECARGO_DOMINICAL_NOCTURNO - 2,1","HRS._RECARGO_FESTIVO_NOCTURNO - 2,1",
                                         "VR._RECARGO_FESTIVO_NOCTURNO - 2,1","HRS._HORA_DOMINICAL_Y_FESTIVO_CON_COMPENSATORIO_DIUR_1.00%",
                                         "VR._HORA_DOMINICAL_Y_FESTIVO_CON_COMPENSATORIO_DIUR_1.00%","HRS_HORA_DOMINICAL_Y_FESTIVO_CON_COMPENSATORIO_NOC_1.35%",
                                         "VR._HORA_DOMINICAL_Y_FESTIVO_CON_COMPENSATORIO_NOC_1.35%",
                                         "HRS_RECARGO_NOCTURNO - 0,35","VR._RECARGO_NOCTURNO - 0,35",
                                         "TOTAL NO. RECARGOS","TOTAL_$_RECARGOS","REAJUSTE_RECARGOS",
                                         "REAJUSTE_H.E","REAJUSTE_SALARIAL","REAJUSTE_AUSENCIAS_JUSTIFICADAS",
                                         "REAJUSTE_VACACIONES","DIAS_AUSENCIAS_JUSTIFICADAS_SIN_COBRO (Vac. Habiles, inc 66,67%)",
                                         "VALOR_AUSENCIAS_JUSTIFICADAS_SIN_COBRO_(Vac. Habiles, inc 66,67%)",
                                         "BONIFICACION_NO_CONSTITUTIVA_DE_SALARIO","BONIFICACION_SALARIAL",
                                         "TRANSPORTE_EXTRALEGAL_AUT._POR_CL","AUXILIO_DE_RODAMIENTO",
                                         "MAYOR_VALOR_PAGADO_AUX._DE_RODAMIENTO","MAY._VALOR_PAGADO_EN_SALARIO",
                                         "MAY._VALOR_PAGADO_EN_AUX._TRANS","BENEFICIOS","EXAMENES_MEDICOS_SERVICIOS",
                                         "VACACIONES","OTROS_CONCEPTOS_FACTURABLES_PRESTACIONALES",
                                         "CONCEPTOS_NO_CONTEMPLADOS_SUPPLA_NO_PRESTACIONALES_CON_SERVICIOS",
                                         "SALUD_PATRONO","PENSION_12%","ARP","TOTAL_S.S.","CAJA_DE_COMP_4%",
                                         "SENA","ICBF","VALOR_PARAFISCALES","CESANTIAS_8.33%","INT._CESANTIAS_1%",
                                         "PRIMA_8.33%","VACACIONES_4.34%","IMPREVISTOS","VALOR_PRESTACIONES",
                                         "TOTAL_NOMINA_S.S.PARAFI_PRESTA","ADMINISTRACION","BONIFICACION_DIRECTIVO",
                                         "SUBTOTAL FACTURA","OTROS CONCEPTOS FACTURABLES PRESTACIONALES",
                                         "EXCEDENTE SS", "PRORRATEO","TOTAL NOMINA","ESTATUS_DIAS",
                                         "OBSERVACION","OPERACION"
                                         ]]

""" Crear df vacio de no facturable """
columnas = [
    "EMPRESA", "TIPO_DE_VINCULACIÓN", "MES", "CENTRO DE COSTOS", "NOMBRE CENTRO DE COSTOS",
    "POBLACIÓN", "NUMERO DOCUMENTO", "NOMBRE COMPLETO", "CARGO NOMINA_x", "CARGO MELI_y",
    "TIPO_DE_DOTACION", "TIPO_DE_CARGO", "FECHA DE INGRESO", "FECHA DE BAJA", "SALARIO MENSUAL",
    "DIAS_PAGO_NOMINA", "DIAS VACACIONES", "SALARIO_A_PAGAR", "SUBSIDIO_TRANSPORTE",
    "HRS_HORA_EXTRA_DIURNA - 1,25", "VR._HORA_EXTRA_DIURNA - 1,25", "HRS._HORA_EXTRA_NOCTURNA - 1,75",
    "VR._HORA_EXTRA_NOCTURNA - 1,75", "NO.HORA_ORD_DOMINICAL_175", "VR.HORA_ORD_DOMINICAL_175",
    "HRS._EXTRA_HORA_DOM/FEST._NOCTURNA_2.50%", "VR._EXTRA_HORA_DOM/FEST._NOCTURNA_2.50%",
    "HRS._HORA_EXTRA_DOMINICAL_Y_FESTIVA_DIURNA_2.00%", "VR._HORA_EXTRA_DOMINICAL_Y_FESTIVA_DIURNA_2.00%",
    "TOTAL # H.E.", "TOTAL_HORAS_EXTRAS_SIN_R.N.", "HRS._DOMINICAL_DIURNO - 1,75",
    "VR._DOMINICAL_DIURNO - 1,75", "HRS._FESTIVO_DIURNO - 1,75", "VR._FESTIVO_DIURNO - 1,75",
    "HRS. RECARGO DOMINICAL NOCTURNO - 2,1", "VR._RECARGO_DOMINICAL_NOCTURNO - 2,1",
    "HRS._RECARGO_FESTIVO_NOCTURNO - 2,1", "VR._RECARGO_FESTIVO_NOCTURNO - 2,1",
    "HRS._HORA_DOMINICAL_Y_FESTIVO_CON_COMPENSATORIO_DIUR_1.00%",
    "VR._HORA_DOMINICAL_Y_FESTIVO_CON_COMPENSATORIO_DIUR_1.00%",
    "HRS_HORA_DOMINICAL_Y_FESTIVO_CON_COMPENSATORIO_NOC_1.35%",
    "VR._HORA_DOMINICAL_Y_FESTIVO_CON_COMPENSATORIO_NOC_1.35%",
    "HRS_RECARGO_NOCTURNO - 0,35", "VR._RECARGO_NOCTURNO - 0,35", "TOTAL NO. RECARGOS",
    "TOTAL_$_RECARGOS", "REAJUSTE_RECARGOS", "REAJUSTE_H.E", "REAJUSTE_SALARIAL",
    "REAJUSTE_AUSENCIAS_JUSTIFICADAS", "REAJUSTE_VACACIONES",
    "DIAS_AUSENCIAS_JUSTIFICADAS_SIN_COBRO (Vac. Habiles, inc 66,67%)",
    "VALOR_AUSENCIAS_JUSTIFICADAS_SIN_COBRO_(Vac. Habiles, inc 66,67%)",
    "BONIFICACION_NO_CONSTITUTIVA_DE_SALARIO", "BONIFICACION_SALARIAL",
    "TRANSPORTE_EXTRALEGAL_AUT._POR_CL", "AUXILIO_DE_RODAMIENTO",
    "MAYOR_VALOR_PAGADO_AUX._DE_RODAMIENTO", "MAY._VALOR_PAGADO_EN_SALARIO",
    "MAY._VALOR_PAGADO_EN_AUX._TRANS", "BENEFICIOS", "EXAMENES_MEDICOS_SERVICIOS", "VACACIONES",
    "OTROS_CONCEPTOS_FACTURABLES_PRESTACIONALES",
    "CONCEPTOS_NO_CONTEMPLADOS_SUPPLA_NO_PRESTACIONALES_CON_SERVICIOS",
    "SALUD_PATRONO", "PENSION_12%", "ARP", "TOTAL_S.S.", "CAJA_DE_COMP_4%", "SENA", "ICBF",
    "VALOR_PARAFISCALES", "CESANTIAS_8.33%", "INT._CESANTIAS_1%", "PRIMA_8.33%", "VACACIONES_4.34%",
    "IMPREVISTOS", "VALOR_PRESTACIONES", "TOTAL_NOMINA_S.S.PARAFI_PRESTA", "ADMINISTRACION",
    "BONIFICACION_DIRECTIVO", "SUBTOTAL FACTURA", "OTROS CONCEPTOS FACTURABLES PRESTACIONALES",
    "EXCEDENTE SS", "PRORRATEO", "TOTAL NOMINA", "ESTATUS_DIAS", "OBSERVACION", "OPERACION"
]

df_noFact = pd.DataFrame(columns=columnas)

""" Seleccionar valores negativos """
df_acumuladoNovCopy = df_acumuladoNov[df_acumuladoNov["CONCEPTOS_NO_CONTEMPLADOS_SUPPLA_NO_PRESTACIONALES_CON_SERVICIOS"] < 0]

""" Seleccionar columnas del df_noFactur"""
df_acumuladoNovCopy = df_acumuladoNovCopy[["EMPRESA", "TIPO_DE_VINCULACIÓN",
                                         "MES","CENTRO DE COSTOS","NOMBRE CENTRO DE COSTOS",
                                         "POBLACIÓN","NUMERO DOCUMENTO","NOMBRE COMPLETO",
                                         "FECHA DE INGRESO","FECHA DE BAJA",
                                         "SALARIO MENSUAL","DIAS_PAGO_NOMINA",
                                         "CONCEPTOS_NO_CONTEMPLADOS_SUPPLA_NO_PRESTACIONALES_CON_SERVICIOS"
                                         ]]

""" Concatenar df_acumulado con no facturables """
df_noFact = pd.concat([df_noFact, df_acumuladoNovCopy], axis=0)




# %% Celda 2

""" Descargar reporte """
#df_nominaProrrateos.to_excel("Nomina con Prorrateos.xlsx")
df_acumulado.to_excel("Prueba_Cambios.xlsx")
#df_noFact.to_excel("Reporte No Facturables.xlsx")

#df_acumulado.to_excel("Reporte_Nomina.xlsx")
#df_summ_acumulado.to_excel("Comparativo_Nomina_vs_Interfaz.xlsx")


# %%
