Attribute VB_Name = "modBomCompare"
Option Explicit

'===================================================================
' modBomCompare —— 数据标准化与差异比较
'
' 主键：子项料号（itemCode，去首尾空格、忽略大小写）
' 比较字段：用量（usageQty，默认容差 0.0001）、单位（usageUom）
'
' 差异状态（固定）：
'   一致 / 页面缺少 / 页面多余 / 用量不一致 / 单位不一致 /
'   Excel重复 / 页面重复 / Excel数据无效 / 页面数据无效
'
' 本模块不写工作表，只返回结果数据，写入由 modResultWriter 负责。
'===================================================================

' ---- 差异状态常量 ----
Public Const ST_OK As String = "一致"
Public Const ST_MISS As String = "页面缺少"
Public Const ST_EXTRA As String = "页面多余"
Public Const ST_QTY As String = "用量不一致"
Public Const ST_UOM As String = "单位不一致"
Public Const ST_EXCEL_DUP As String = "Excel重复"
Public Const ST_PAGE_DUP As String = "页面重复"
Public Const ST_EXCEL_INVALID As String = "Excel数据无效"
Public Const ST_PAGE_INVALID As String = "页面数据无效"

' 数量比较容差
Public Const QTY_TOLERANCE As Double = 0.0001

'===================================================================
' 主入口：执行差异比较。
'
' 参数：
'   excelRows  Range("A2:D" & lastRow).Value2 得到的二维数组（1 起始）
'              col1=子项料号, col2=Excel用量, col3=Excel单位, col4=品名
'   nRows      Excel 数据行数（= lastRow - 1）
'   pageData   modJson.ParsePageJson 返回的 Dictionary
'
' 返回 Dictionary：
'   "perRow"      -> 2D Variant(nRows, 5)，与每行 Excel 对齐（状态/页面用量/页面单位/差异说明/核对时间）
'   "appended"    -> 2D Variant(m, 5)，页面侧额外发现（页面多余/页面重复/页面数据无效）
'   "parentItemCode" -> 母件料号
'   "collectedAt" -> 采集时间
'   以及各差异计数：excelTotal/pageTotal/matched/missing/extra/qtyDiff/uomDiff/
'                   excelDup/pageDup/excelInvalid/pageInvalid
'===================================================================
Public Function BuildResults(excelRows As Variant, ByVal nRows As Long, pageData As Object) As Object
    Dim ts As String
    ts = Format$(Now, "yyyy-mm-dd hh:nn:ss")

    Dim parentCode As String
    parentCode = pageData("parentItemCode")

    Dim pageCol As Object
    Set pageCol = pageData("components")

    ' ---- 建立 Excel 侧映射（key -> 首次出现行号，重复标记）----
    Dim excelMap As Object
    Dim excelDup As Object
    Set excelMap = CreateObject("Scripting.Dictionary")
    Set excelDup = CreateObject("Scripting.Dictionary")

    Dim i As Long
    Dim excelInvalidCount As Long
    excelInvalidCount = 0

    For i = 1 To nRows
        Dim ek As String
        ek = NormalizeKey(excelRows(i, 1))
        If ek = "" Then
            excelInvalidCount = excelInvalidCount + 1
        ElseIf excelMap.Exists(ek) Then
            excelDup(ek) = True
        Else
            excelMap.Add ek, i
        End If
    Next i

    ' ---- 建立页面侧映射（key -> 索引，重复标记）----
    Dim pageMap As Object
    Dim pageDup As Object
    Set pageMap = CreateObject("Scripting.Dictionary")
    Set pageDup = CreateObject("Scripting.Dictionary")

    Dim p As Long
    Dim pageInvalidCount As Long
    pageInvalidCount = 0

    For p = 1 To pageCol.Count
        Dim pk As String
        pk = NormalizeKey(GetP(pageCol(p), "itemCode"))
        If pk = "" Then
            pageInvalidCount = pageInvalidCount + 1
        ElseIf pageMap.Exists(pk) Then
            pageDup(pk) = True
        Else
            pageMap.Add pk, p
        End If
    Next p

    ' ---- 逐行比较 Excel ----
    Dim perRow As Variant
    ReDim perRow(1 To nRows, 1 To 5)

    Dim matchedCount As Long, missingCount As Long
    Dim qtyCount As Long, uomCount As Long, excelDupCount As Long

    For i = 1 To nRows
        Dim eKey As String
        eKey = NormalizeKey(excelRows(i, 1))

        ' 输出列：1=状态 2=页面用量 3=页面单位 4=差异说明 5=核对时间
        perRow(i, 5) = ts

        If eKey = "" Then
            perRow(i, 1) = ST_EXCEL_INVALID
            perRow(i, 4) = "子项料号为空，无法参与核对。"
        ElseIf excelDup.Exists(eKey) And excelMap(eKey) <> i Then
            excelDupCount = excelDupCount + 1
            perRow(i, 1) = ST_EXCEL_DUP
            perRow(i, 4) = "Excel 中料号 '" & CStr(excelRows(i, 1)) & "' 重复出现，本行不参与用量比较（首次出现行比较）。"
        ElseIf Not pageMap.Exists(eKey) Then
            missingCount = missingCount + 1
            perRow(i, 1) = ST_MISS
            perRow(i, 4) = "子项料号 '" & CStr(excelRows(i, 1)) & "' 在 U9 页面中未找到（页面缺少）。"
        Else
            ' 匹配成功，比较用量与单位
            Dim pIdx As Long
            pIdx = pageMap(eKey)

            Dim pageQty As Double
            Dim pageUom As String
            pageQty = GetP(pageCol(pIdx), "usageQty")
            pageUom = GetP(pageCol(pIdx), "usageUom")

            Dim excelQty As Variant
            excelQty = excelRows(i, 2)

            If AreQtyEqual(excelQty, pageQty) Then
                If AreUomEqual(excelRows(i, 3), pageUom) Then
                    matchedCount = matchedCount + 1
                    perRow(i, 1) = ST_OK
                    perRow(i, 2) = pageQty
                    perRow(i, 3) = pageUom
                    perRow(i, 4) = ""
                Else
                    uomCount = uomCount + 1
                    perRow(i, 1) = ST_UOM
                    perRow(i, 2) = pageQty
                    perRow(i, 3) = pageUom
                    perRow(i, 4) = "单位不一致：Excel=" & CStr(excelRows(i, 3)) & "，页面=" & pageUom & "。"
                End If
            Else
                qtyCount = qtyCount + 1
                perRow(i, 1) = ST_QTY
                perRow(i, 2) = pageQty
                perRow(i, 3) = pageUom
                perRow(i, 4) = "用量不一致：Excel=" & QtyText(excelQty) & "，页面=" & QtyText(pageQty) & "。"
            End If
        End If
    Next i

    ' ---- 页面侧额外发现（页面多余 / 页面重复 / 页面数据无效）----
    Dim appRows As Object
    Set appRows = New Collection

    Dim extraCount As Long, pageDupCount As Long

    For p = 1 To pageCol.Count
        Dim pk2 As String
        pk2 = NormalizeKey(GetP(pageCol(p), "itemCode"))

        If pk2 = "" Then
            extraCount = extraCount + 0
            pageInvalidCount = pageInvalidCount + 0
            appRows.Add MakeAppendedRow(ts, ST_PAGE_INVALID, "", "", _
                "页面子项料号为空，视为无效数据。")
        ElseIf pageDup.Exists(pk2) And pageMap(pk2) <> p Then
            pageDupCount = pageDupCount + 1
            appRows.Add MakeAppendedRow(ts, ST_PAGE_DUP, QtyText(GetP(pageCol(p), "usageQty")), _
                GetP(pageCol(p), "usageUom"), "页面中料号 '" & GetP(pageCol(p), "itemCode") & "' 重复出现。")
        ElseIf Not excelMap.Exists(pk2) Then
            extraCount = extraCount + 1
            appRows.Add MakeAppendedRow(ts, ST_EXTRA, QtyText(GetP(pageCol(p), "usageQty")), _
                GetP(pageCol(p), "usageUom"), "子项料号 '" & GetP(pageCol(p), "itemCode") & "' 仅在 U9 页面存在，Excel 中未找到（页面多余）。")
        End If
    Next p

    ' 将 Collection 转为二维数组
    Dim appended As Variant
    ReDim appended(1 To appRows.Count, 1 To 5)
    Dim r As Long
    For r = 1 To appRows.Count
        Dim ar As Variant
        ar = appRows(r)
        appended(r, 1) = ar(1)
        appended(r, 2) = ar(2)
        appended(r, 3) = ar(3)
        appended(r, 4) = ar(4)
        appended(r, 5) = ar(5)
    Next r

    ' ---- 汇总 ----
    Dim res As Object
    Set res = CreateObject("Scripting.Dictionary")
    res("perRow") = perRow
    res("appended") = appended
    res("parentItemCode") = parentCode
    res("collectedAt") = pageData("collectedAt")
    res("excelTotal") = nRows
    res("pageTotal") = pageCol.Count
    res("matched") = matchedCount
    res("missing") = missingCount
    res("extra") = extraCount
    res("qtyDiff") = qtyCount
    res("uomDiff") = uomCount
    res("excelDup") = excelDupCount
    res("pageDup") = pageDupCount
    res("excelInvalid") = excelInvalidCount
    res("pageInvalid") = pageInvalidCount

    Set BuildResults = res
End Function

'===================================================================
' 工具函数
'===================================================================

Private Function MakeAppendedRow(ByVal ts As String, ByVal status As String, _
    ByVal pageQty As String, ByVal pageUom As String, ByVal note As String) As Variant
    Dim arr(1 To 5) As Variant
    arr(1) = status
    arr(2) = pageQty
    arr(3) = pageUom
    arr(4) = note
    arr(5) = ts
    MakeAppendedRow = arr
End Function

' 读取页面组件字典字段（返回 String）
Private Function GetP(obj As Object, ByVal key As String) As Variant
    On Error Resume Next
    GetP = obj(key)
    If Err.Number <> 0 Then
        Err.Clear
        GetP = ""
    End If
    On Error GoTo 0
End Function

Private Function NormalizeKey(ByVal v As Variant) As String
    If IsNull(v) Or IsEmpty(v) Then
        NormalizeKey = ""
    Else
        NormalizeKey = LCase$(Trim$(CStr(v)))
    End If
End Function

' 用量是否相等（容差 0.0001）；Excel 用量非数字则视为不等
Private Function AreQtyEqual(ByVal excelQty As Variant, ByVal pageQty As Variant) As Boolean
    Dim de As Double, dp As Double

    On Error Resume Next
    de = CDbl(excelQty)
    If Err.Number <> 0 Then
        Err.Clear
        AreQtyEqual = False
        On Error GoTo 0
        Exit Function
    End If
    dp = CDbl(pageQty)
    If Err.Number <> 0 Then
        Err.Clear
        AreQtyEqual = False
        On Error GoTo 0
        Exit Function
    End If
    On Error GoTo 0

    AreQtyEqual = (Abs(de - dp) <= QTY_TOLERANCE)
End Function

Private Function AreUomEqual(ByVal excelUom As Variant, ByVal pageUom As Variant) As Boolean
    AreUomEqual = (LCase$(Trim$(CStr(excelUom))) = LCase$(Trim$(CStr(pageUom))))
End Function

Private Function QtyText(ByVal v As Variant) As String
    If IsNull(v) Or IsEmpty(v) Then
        QtyText = ""
    ElseIf IsNumeric(v) Then
        QtyText = Format$(CDbl(v), "0.########")
    Else
        QtyText = CStr(v)
    End If
End Function