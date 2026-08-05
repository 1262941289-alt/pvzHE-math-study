Attribute VB_Name = "JsonConverter"
Option Explicit

'===================================================================
' JsonConverter —— 轻量 JSON 解析器（自包含，无外部依赖）
'
' 用法：
'   Dim pageData As Object
'   Set pageData = JsonConverter.ParseJson(jsonText)
'
' 返回类型 Variant，语义如下：
'   JSON 对象  -> Scripting.Dictionary（成员通过 pageData("key") 访问，
'                值为原始 String/Double/Boolean/Dictionary/Collection）
'   JSON 数组  -> Collection（1 起始，item(i) 访问）
'   JSON 字符串-> String
'   JSON 数字  -> Double
'   JSON 布尔  -> Boolean
'   JSON null  -> Empty
'
' 说明：本文件为满足“协议字段校验”的最小实现，足够解析 U9BomCheck JSON。
'===================================================================

Public Function ParseJson(ByVal JsonString As String) As Variant
    Dim Pos As Long
    Pos = 1
    ParseJson = ParseValue(JsonString, Pos)
End Function

'-------------------------------------------------------------------
' 顶层值解析（返回 Variant）
'-------------------------------------------------------------------
Private Function ParseValue(ByVal s As String, ByRef Pos As Long) As Variant
    SkipWhitespace s, Pos

    If Pos > Len(s) Then
        RaiseParseError "JSON 内容意外结束（空输入）。"
    End If

    Dim c As String
    c = Mid$(s, Pos, 1)

    Select Case c
        Case "{"
            Set ParseValue = ParseObject(s, Pos)
        Case "["
            Set ParseValue = ParseArray(s, Pos)
        Case """"
            ParseValue = ParseString(s, Pos)
        Case Else
            ParseValue = ParsePrimitive(s, Pos)
    End Select
End Function

'-------------------------------------------------------------------
' 对象 -> Dictionary
'-------------------------------------------------------------------
Private Function ParseObject(ByVal s As String, ByRef Pos As Long) As Object
    Dim dict As Object
    Set dict = CreateObject("Scripting.Dictionary")

    If Not SkipExpected(s, Pos, "{") Then
        RaiseParseError "对象必须以 { 开始。"
    End If

    SkipWhitespace s, Pos

    If PeekChar(s, Pos) = "}" Then
        Pos = Pos + 1
        Set ParseObject = dict
        Exit Function
    End If

    Do
        SkipWhitespace s, Pos
        If PeekChar(s, Pos) <> """" Then
            RaiseParseError "对象的键必须是字符串。"
        End If
        Dim key As String
        key = ParseString(s, Pos)

        SkipWhitespace s, Pos
        If Not SkipExpected(s, Pos, ":") Then
            RaiseParseError "对象键后缺少冒号(:)。"
        End If

        SkipWhitespace s, Pos
        Dim val As Variant
        val = ParseValue(s, Pos)
        dict(key) = val

        SkipWhitespace s, Pos
        Dim comma As String
        comma = PeekChar(s, Pos)
        If comma = "," Then
            Pos = Pos + 1
            SkipWhitespace s, Pos
        ElseIf comma = "}" Then
            Pos = Pos + 1
            Exit Do
        Else
            RaiseParseError "对象成员之间缺少逗号或结束符。"
        End If
    Loop

    Set ParseObject = dict
End Function

'-------------------------------------------------------------------
' 数组 -> Collection
'-------------------------------------------------------------------
Private Function ParseArray(ByVal s As String, ByRef Pos As Long) As Object
    Dim col As Object
    Set col = New Collection

    If Not SkipExpected(s, Pos, "[") Then
        RaiseParseError "数组必须以 [ 开始。"
    End If

    SkipWhitespace s, Pos

    If PeekChar(s, Pos) = "]" Then
        Pos = Pos + 1
        Set ParseArray = col
        Exit Function
    End If

    Do
        SkipWhitespace s, Pos
        Dim item As Variant
        item = ParseValue(s, Pos)
        col.Add item

        SkipWhitespace s, Pos
        Dim comma As String
        comma = PeekChar(s, Pos)
        If comma = "," Then
            Pos = Pos + 1
            SkipWhitespace s, Pos
        ElseIf comma = "]" Then
            Pos = Pos + 1
            Exit Do
        Else
            RaiseParseError "数组成员之间缺少逗号或结束符。"
        End If
    Loop

    Set ParseArray = col
End Function

'-------------------------------------------------------------------
' 解析字符串字面量（返回 String）
'-------------------------------------------------------------------
Private Function ParseString(ByVal s As String, ByRef Pos As Long) As String
    If PeekChar(s, Pos) <> """" Then
        RaiseParseError "字符串必须以 `引号` 开始。"
    End If
    Pos = Pos + 1
    Dim sb As String
    sb = ""
    Do While Pos <= Len(s)
        Dim c As String
        c = Mid$(s, Pos, 1)
        If c = """" Then
            Pos = Pos + 1
            ParseString = sb
            Exit Function
        ElseIf c = "\" Then
            Pos = Pos + 1
            If Pos > Len(s) Then
                RaiseParseError "字符串转义序列不完整。"
            End If
            Dim e As String
            e = Mid$(s, Pos, 1)
            Select Case e
                Case """": sb = sb & """"
                Case "\": sb = sb & "\"
                Case "/": sb = sb & "/"
                Case "b": sb = sb & Chr$(8)
                Case "f": sb = sb & Chr$(12)
                Case "n": sb = sb & vbLf
                Case "r": sb = sb & vbCr
                Case "t": sb = sb & vbTab
                Case "u"
                    If Pos + 4 > Len(s) Then
                        RaiseParseError "Unicode 转义 \uXXXX 不完整。"
                    End If
                    Dim hex4 As String
                    hex4 = Mid$(s, Pos + 1, 4)
                    sb = sb & ChrW$(ParseHex(hex4))
                    Pos = Pos + 4
                Case Else
                    RaiseParseError "不支持的反斜杠转义：\" & e
            End Select
            Pos = Pos + 1
        Else
            sb = sb & c
            Pos = Pos + 1
        End If
    Loop
    RaiseParseError "字符串未正确结束。"
End Function

'-------------------------------------------------------------------
' 数字 / 布尔 / null（返回 Variant）
'-------------------------------------------------------------------
Private Function ParsePrimitive(ByVal s As String, ByRef Pos As Long) As Variant
    Dim start As Long
    start = Pos

    Do While Pos <= Len(s)
        Dim c As String
        c = Mid$(s, Pos, 1)
        If c = "," Or c = "}" Or c = "]" Or c = ":" Or c = " " Or c = vbTab Or c = vbCr Or c = vbLf Then
            Exit Do
        End If
        Pos = Pos + 1
    Loop

    Dim token As String
    token = Mid$(s, start, Pos - start)

    Dim lower As String
    lower = LCase$(token)

    If lower = "true" Then
        ParsePrimitive = True
        Exit Function
    ElseIf lower = "false" Then
        ParsePrimitive = False
        Exit Function
    ElseIf lower = "null" Then
        ParsePrimitive = Empty
        Exit Function
    End If

    If IsNumeric(token) Then
        ParsePrimitive = CDbl(token)
        Exit Function
    End If

    RaiseParseError "无法识别的 JSON 值：" & token
End Function

'-------------------------------------------------------------------
' 工具函数
'-------------------------------------------------------------------
Private Function PeekChar(ByVal s As String, ByRef Pos As Long) As String
    If Pos > Len(s) Then
        PeekChar = ""
    Else
        PeekChar = Mid$(s, Pos, 1)
    End If
End Function

Private Sub SkipWhitespace(ByVal s As String, ByRef Pos As Long)
    Do While Pos <= Len(s)
        Dim c As String
        c = Mid$(s, Pos, 1)
        If c = " " Or c = vbTab Or c = vbCr Or c = vbLf Then
            Pos = Pos + 1
        Else
            Exit Do
        End If
    Loop
End Sub

Private Function SkipExpected(ByVal s As String, ByRef Pos As Long, ByVal expected As String) As Boolean
    SkipWhitespace s, Pos
    If PeekChar(s, Pos) = expected Then
        Pos = Pos + 1
        SkipExpected = True
    Else
        SkipExpected = False
    End If
End Function

Private Function ParseHex(ByVal hex As String) As Long
    Dim i As Long
    Dim v As Long
    v = 0
    For i = 1 To 4
        Dim ch As String
        ch = Mid$(hex, i, 1)
        v = v * 16
        If ch >= "0" And ch <= "9" Then
            v = v + (Asc(ch) - Asc("0"))
        ElseIf ch >= "a" And ch <= "f" Then
            v = v + (Asc(ch) - Asc("a") + 10)
        ElseIf ch >= "A" And ch <= "F" Then
            v = v + (Asc(ch) - Asc("A") + 10)
        Else
            RaiseParseError "无效的十六进制字符：" & ch
        End If
    Next i
    ParseHex = v
End Function

Private Sub RaiseParseError(ByVal msg As String)
    Err.Raise vbObjectError + 1050, "JsonConverter.ParseJson", msg
End Sub