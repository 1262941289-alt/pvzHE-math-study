Attribute VB_Name = "modJson"
Option Explicit

'===================================================================
' modJson —— 剪贴板 JSON 的读取与 U9BomCheck 协议校验
'
' 校验规则（不满足立即停止，不猜测字段）：
'   protocol = "U9BomCheck"
'   version  = "1.0"
'   success  = True
'   pageType = "MaterialBom"
'   components 存在且为数组（Collection）
'   parentItemCode / collectedAt 存在（可为空字符串，但字词必须存在）
'
' 返回一个 Dictionary，包含规范化后的页面数据：
'   "pageType", "parentItemCode", "collectedAt",
'   "components"（Collection，每个为 Dictionary，字段见下）
'
' 组件字段：sequence / itemCode / itemName / usageQty / usageUom
'===================================================================

Public Const PAGE_TYPE_BOM As String = "MaterialBom"

' 读取剪贴板并解析为 U9BomCheck 页面数据。
' 出错时抛出带意图的错误（Err.Description 为中文提示）。
Public Function ParsePageJson(Optional ByVal jsonText As String = vbNullString) As Object
    If Len(Trim$(jsonText)) = 0 Then
        jsonText = modClipboard.GetClipboardText()
    End If

    If Len(Trim$(jsonText)) = 0 Then
        Err.Raise vbObjectError + 1001, "U9_执行BOM核对", "剪贴板中没有页面数据。请先在 Edge 插件中执行“采集并复制到剪贴板”。"
    End If

    Dim root As Object
    On Error GoTo JsonParseFail
    Set root = JsonConverter.ParseJson(jsonText)
    On Error GoTo 0

    If root Is Nothing Then
        Err.Raise vbObjectError + 1003, "U9_执行BOM核对", "剪贴板内容不是有效的 JSON。"
    End If

    ' ---- protocol ----
    If Not HasField(root, "protocol") Then
        Err.Raise vbObjectError + 1002, "U9_执行BOM核对", "剪贴板数据缺少 protocol 字段，不是 U9 BOM 核对数据。"
    End If
    If CStr(root("protocol")) <> "U9BomCheck" Then
        Err.Raise vbObjectError + 1002, "U9_执行BOM核对", "剪贴板数据协议不正确（期望 U9BomCheck，实际：" & CStr(root("protocol")) & "）。"
    End If

    ' ---- version ----
    If Not HasField(root, "version") Then
        Err.Raise vbObjectError + 1004, "U9_执行BOM核对", "剪贴板数据缺少 version 字段。"
    End If
    If CStr(root("version")) <> "1.0" Then
        Err.Raise vbObjectError + 1004, "U9_执行BOM核对", "剪贴板数据版本不支持（期望 1.0，实际：" & CStr(root("version")) & "）。"
    End If

    ' ---- success ----
    If Not HasField(root, "success") Then
        Err.Raise vbObjectError + 1005, "U9_执行BOM核对", "剪贴板数据缺少 success 字段。"
    End If
    If Not CBool(root("success")) Then
        Dim pageError As String
        pageError = ""
        If HasField(root, "error") Then pageError = CStr(root("error"))
        Err.Raise vbObjectError + 1005, "U9_执行BOM核对", "页面采集失败：" & pageError
    End If

    ' ---- source ----
    If HasField(root, "source") And Not IsEmpty(root("source")) Then
        If CStr(root("source")) <> "U9" Then
            Err.Raise vbObjectError + 1006, "U9_执行BOM核对", "数据来源不正确（期望 U9）。"
        End If
    End If

    ' ---- pageType ----
    If Not HasField(root, "pageType") Then
        Err.Raise vbObjectError + 1006, "U9_执行BOM核对", "剪贴板数据缺少 pageType 字段。"
    End If
    If CStr(root("pageType")) <> PAGE_TYPE_BOM Then
        Err.Raise vbObjectError + 1006, "U9_执行BOM核对", "剪贴板数据不是物料清单(BOM)页面数据（pageType 实际：" & CStr(root("pageType")) & "）。"
    End If

    ' ---- components ----
    If Not HasField(root, "components") Then
        Err.Raise vbObjectError + 1007, "U9_执行BOM核对", "剪贴板数据缺少 components 字段。"
    End If

    Dim comps As Variant
    comps = root("components")
    If Not IsObject(comps) Then
        Err.Raise vbObjectError + 1007, "U9_执行BOM核对", "components 字段类型不正确（应为数组）。"
    End If

    ' 规范化结果
    Dim result As Object
    Set result = CreateObject("Scripting.Dictionary")
    result("pageType") = CStr(root("pageType"))
    result("parentItemCode") = IIf(HasField(root, "parentItemCode"), CStr(root("parentItemCode")), "")
    result("collectedAt") = IIf(HasField(root, "collectedAt"), CStr(root("collectedAt")), "")
    result("components") = NormalizeComponents(comps)

    Set ParsePageJson = result
End Function

' 将页面 components 规范化为“每个组件一个 Dictionary”的 Collection。
Private Function NormalizeComponents(comps As Object) As Object
    Dim outCol As Object
    Set outCol = New Collection

    Dim i As Long
    For i = 1 To comps.Count
        Dim c As Variant
        c = comps(i)

        Dim d As Object
        Set d = CreateObject("Scripting.Dictionary")
        d("sequence") = GetFieldString(c, "sequence")
        d("itemCode") = GetFieldString(c, "itemCode")
        d("itemName") = GetFieldString(c, "itemName")
        d("usageQty") = GetFieldNumber(c, "usageQty")
        d("usageUom") = GetFieldString(c, "usageUom")
        outCol.Add d
    Next i

    Set NormalizeComponents = outCol
End Function

Private Function HasField(obj As Object, ByVal key As String) As Boolean
    On Error Resume Next
    Dim v As Variant
    v = obj(key)
    HasField = (Err.Number = 0)
    On Error GoTo 0
End Function

Private Function GetFieldString(obj As Object, ByVal key As String) As String
    If HasField(obj, key) Then
        If IsNull(obj(key)) Or IsEmpty(obj(key)) Then
            GetFieldString = ""
        Else
            GetFieldString = CStr(obj(key))
        End If
    Else
        GetFieldString = ""
    End If
End Function

Private Function GetFieldNumber(obj As Object, ByVal key As String) As Double
    If HasField(obj, key) Then
        Dim v As Variant
        v = obj(key)
        If IsNumeric(v) Then
            GetFieldNumber = CDbl(v)
        ElseIf VarType(v) = vbBoolean Then
            GetFieldNumber = 0
        Else
            GetFieldNumber = 0
        End If
    Else
        GetFieldNumber = 0
    End If
End Function