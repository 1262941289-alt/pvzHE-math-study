Attribute VB_Name = "modBomCheckEntry"
Option Explicit

'===================================================================
' modBomCheckEntry —— 公共入口（Alt+F8 调用）
'
' 公共宏：
'   U9_执行BOM核对   读取剪贴板 U9 BOM 数据并核对当前工作表
'   U9_清除核对结果   清除 E:I 列输出
'   U9_查看页面数据   查看剪贴板中的页面采集数据
'
' 说明：本模块明确操作当前活动工作簿(ActiveSheet/ActiveWorkbook)，
' 不把结果写入加载项自身工作簿；代码不依赖任何固定工作簿文件名。
'===================================================================

'===================================================================
' 主入口：执行 BOM 核对
'===================================================================
Public Sub U9_执行BOM核对()
    On Error GoTo Fail

    Dim ws As Worksheet
    Set ws = ActiveSheet

    ' 1) 定位数据范围（A 列最后一个非空单元格）
    Dim lastInputRow As Long
    lastInputRow = ws.Cells(ws.Rows.Count, 1).End(xlUp).Row

    If lastInputRow < 2 Then
        MsgBox "当前工作表没有 BOM 数据。" & vbCrLf & _
               "请确认：第 1 行为标题，数据从第 2 行开始，且 A 列存在子项料号。", _
               vbExclamation, "U9_执行BOM核对"
        Exit Sub
    End If

    ' 2) 一次性读取 A2:D 到数组（避免逐单元格交互）
    Dim excelRows As Variant
    excelRows = ws.Range("A2:D" & lastInputRow).Value2

    ' 3) 读取剪贴板并解析页面数据（含协议校验）
    Dim pageData As Object
    Set pageData = modJson.ParsePageJson()

    ' 4) 执行差异比较
    Dim res As Object
    Set res = modBomCompare.BuildResults(excelRows, lastInputRow - 1, pageData)

    ' 5) 写入结果
    modResultWriter.WriteResults ws, res, lastInputRow

    ' 6) 汇总提示
    Call ShowSummary(res)

    Exit Sub

Fail:
    MsgBox Err.Description, vbCritical, "U9_执行BOM核对"
End Sub

'===================================================================
' 清除 E:I 列核对结果
'===================================================================
Public Sub U9_清除核对结果()
    On Error GoTo Fail
    modResultWriter.ClearEtoI ActiveSheet
    MsgBox "已清除核对结果（E:I 列）。", vbInformation, "U9_清除核对结果"
    Exit Sub
Fail:
    MsgBox Err.Description, vbCritical, "U9_清除核对结果"
End Sub

'===================================================================
' 查看剪贴板中的页面采集数据
'===================================================================
Public Sub U9_查看页面数据()
    On Error GoTo Fail

    Dim pageData As Object
    Set pageData = modJson.ParsePageJson()

    Dim comps As Object
    Set comps = pageData("components")

    Dim sb As String
    sb = "母件料号：" & pageData("parentItemCode") & vbCrLf
    sb = sb & "页面类型：" & pageData("pageType") & vbCrLf
    sb = sb & "子项数量：" & comps.Count & vbCrLf
    sb = sb & "采集时间：" & pageData("collectedAt") & vbCrLf
    sb = sb & vbCrLf & "子项列表（前 20 条）：" & vbCrLf

    Dim upto As Long
    upto = comps.Count
    If upto > 20 Then upto = 20

    Dim i As Long
    For i = 1 To upto
        sb = sb & (i) & ") " & GetComp(comps(i), "itemCode") & _
                   "  用量=" & GetComp(comps(i), "usageQty") & _
                   "  单位=" & GetComp(comps(i), "usageUom") & vbCrLf
    Next i

    If comps.Count > 20 Then
        sb = sb & "……（共 " & comps.Count & " 条）"
    End If

    MsgBox sb, vbInformation, "U9_查看页面数据"
    Exit Sub

Fail:
    MsgBox Err.Description, vbCritical, "U9_查看页面数据"
End Sub

'===================================================================
' 内部工具
'===================================================================

Private Function GetComp(obj As Object, ByVal key As String) As Variant
    On Error Resume Next
    GetComp = obj(key)
    If Err.Number <> 0 Then
        Err.Clear
        GetComp = ""
    End If
    On Error GoTo 0
End Function

Private Sub ShowSummary(res As Object)
    Dim sb As String
    sb = "核对完成。母件料号：" & res("parentItemCode") & vbCrLf & vbCrLf
    sb = sb & "Excel 行数：" & res("excelTotal") & "　页面子项数：" & res("pageTotal") & vbCrLf
    sb = sb & "一致：" & res("matched") & vbCrLf
    sb = sb & "页面缺少：" & res("missing") & vbCrLf
    sb = sb & "页面多余：" & res("extra") & vbCrLf
    sb = sb & "用量不一致：" & res("qtyDiff") & vbCrLf
    sb = sb & "单位不一致：" & res("uomDiff") & vbCrLf
    sb = sb & "Excel重复：" & res("excelDup") & vbCrLf
    sb = sb & "页面重复：" & res("pageDup") & vbCrLf
    sb = sb & "Excel数据无效：" & res("excelInvalid") & vbCrLf
    sb = sb & "页面数据无效：" & res("pageInvalid")
    MsgBox sb, vbInformation, "U9_执行BOM核对"
End Sub