VBA_CODE = """
Sub DesvincularCeldas(sheetName As String)
    Dim ws As Worksheet
    Dim celda As Range

    Application.DisplayAlerts = False
    
    ' Definir la hoja especificada
    Set ws = ThisWorkbook.Sheets(sheetName)
    
    ' Recorrer cada celda usada en la hoja
    For Each celda In ws.UsedRange
        ' Si la celda contiene una fórmula con vínculo
        If celda.HasFormula Then
            ' Copiar solo el valor de la celda y desvincular la fórmula
            celda.Value = celda.Value
        End If
    Next celda
    
    Application.DisplayAlerts = True
End Sub

Sub TabularInformacionCorregido(sheetName As String)
    Dim ws As Worksheet
    Dim nuevaWs As Worksheet
    Dim ultimaFila As Long
    Dim i As Long, j As Long
    Dim filaNueva As Long
    Dim diaSemana1 As String, diaSemana2 As String
    Dim fecha1 As Date, fecha2 As Date
    Dim apertura As String, cierre As String
    Dim nLocal As String, nombre As String
    
    ' Definir la hoja origen y crear una nueva hoja para la tabla
    Set ws = ThisWorkbook.Sheets(sheetName)
    Set nuevaWs = ThisWorkbook.Sheets.Add
    nuevaWs.Name = "Tabla Tabulada"
    
    ' Escribir encabezados en la nueva hoja
    nuevaWs.Cells(1, 1).Value = "N° de Local"
    nuevaWs.Cells(1, 2).Value = "Nombre"
    nuevaWs.Cells(1, 3).Value = "Apertura"
    nuevaWs.Cells(1, 4).Value = "Cierre"
    nuevaWs.Cells(1, 5).Value = "Día Semana 1"
    nuevaWs.Cells(1, 6).Value = "Día Semana 2"
    nuevaWs.Cells(1, 7).Value = "Fecha 1"
    nuevaWs.Cells(1, 8).Value = "Fecha 2"
    
    filaNueva = 2 ' Empezar a llenar desde la segunda fila
    
    ' Encontrar la última fila con datos en la columna A (número de local)
    ultimaFila = ws.Cells(ws.Rows.Count, 1).End(xlUp).Row
    
    ' Recorrer las filas de la hoja original (desde la fila 6)
    For i = 6 To ultimaFila
        nLocal = ws.Cells(i, 1).Value
        nombre = ws.Cells(i, 2).Value
        
        ' Recorrer las columnas de días y horarios (C y D en adelante)
        For j = 3 To ws.Cells(4, ws.Columns.Count).End(xlToLeft).Column Step 2
            ' Leer los valores correspondientes
            diaSemana1 = ws.Cells(4, j).Value  ' Día semana apertura
            diaSemana2 = ws.Cells(4, j + 1).Value  ' Día semana cierre
            fecha1 = ws.Cells(5, j).Value  ' Fecha apertura
            fecha2 = ws.Cells(5, j + 1).Value  ' Fecha cierre
            apertura = ws.Cells(i, j).Value  ' Hora apertura
            cierre = ws.Cells(i, j + 1).Value  ' Hora cierre
            
            ' Validar que haya datos de apertura y cierre
            If apertura <> "CERRADO" And apertura <> "" And cierre <> "" Then
                ' Copiar la información a la nueva hoja
                nuevaWs.Cells(filaNueva, 1).Value = nLocal
                nuevaWs.Cells(filaNueva, 2).Value = nombre
                nuevaWs.Cells(filaNueva, 3).Value = apertura
                nuevaWs.Cells(filaNueva, 4).Value = cierre
                nuevaWs.Cells(filaNueva, 5).Value = diaSemana1
                nuevaWs.Cells(filaNueva, 6).Value = diaSemana2
                nuevaWs.Cells(filaNueva, 7).Value = fecha1
                nuevaWs.Cells(filaNueva, 8).Value = fecha2
                filaNueva = filaNueva + 1
            End If
        Next j
    Next i
    
    Application.DisplayAlerts = True
End Sub
"""

def insert_vba_code(workbook):
    try:
        vba_module = workbook.VBProject.VBComponents.Add(1)  # 1 = vbext_ct_StdModule
        vba_module.CodeModule.AddFromString(VBA_CODE)
    except Exception as e:
        print(f"Error al insertar código VBA: {str(e)}")
        print("Por favor, asegúrese de que 'Confiar en el acceso al modelo de objetos del proyecto de VBA' esté habilitado en la configuración de seguridad de Excel.") 