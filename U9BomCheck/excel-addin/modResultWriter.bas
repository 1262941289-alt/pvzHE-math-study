Attribute VB_Name = "modResultWriter"
Option Explicit

'===================================================================
' modResultWriter —— 结果写入
'
' 约定：结果只写入 E:I 列（核对结果/页面用量/页面单位/差异说明/核对时间）。
' 原始输入列 A:D 不被修改。
'
' 布局：
'   - 每行 Excel 的对齐结果写 E2 起，行数 = Excel 数据行数。
'   - 页面侧额外发现（页面多余/页面重复/页面数据无效）追写在数据区下方，
'     起始行 = 最后输入行 + 2，只占 E:I，A:D 留空，避免扩展 A 列数据范围。
'===================================================================

' 将核对结果写入工作表。
' 参数：
'   ws            目标工作表
'   res           modBomCompare.BuildResults 返回的 Dictionary
'   lastInputRow  输入数据的最后一行（A 列定位）
Public Sub WriteResults(ws As Worksheet, res As Object, ByVal lastInputRow As Long)
    Dim perRow As Variant
    perRow = res("perRow")

    Dim appended As Variant
    appended = res("appended")

    ' 先清除旧输出（E:I，从第 2 行到最后使用行）
    Call ClearEtoI(ws)

    Dim nRows As Long
    nRows = UBound(perRow, 1)

    If nRows > 0 Then
        ws.Range(ws.Cells(2, 5), ws.Cells(1 + nRows, 9)).Value = perRow
    End If

    ' 页面侧追写
    Dim m As Long
    m = UBound(appended, 1)

    If m > 0 Then
        Dim startRow As Long
        startRow = lastInputRow + 2
        ws.Range(ws.Cells(startRow, 5), ws.Cells(startRow + m - 1, 9)).Value = appended
    End If
End Sub

' 清除 E:I 列第 2 行起的所有输出（含追加的页面侧结果）。
' 不触碰 A:D 输入列。
Public Sub ClearEtoI(ws As Worksheet)
    Dim lastRow As Long
    lastRow = ws.Cells(ws.Rows.Count, 5).End(xlUp).Row
    If lastRow < 2 Then
        Exit Sub
    End If
    ws.Range(ws.Cells(2, 5), ws.Cells(lastRow, 9)).ClearContents
    ws.Range(ws.Cells(2, 5), ws.Cells(lastRow, 9)).ClearFormats
End Sub