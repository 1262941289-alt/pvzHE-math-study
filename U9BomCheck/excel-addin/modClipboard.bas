Attribute VB_Name = "modClipboard"
Option Explicit

'===================================================================
' modClipboard —— 剪贴板读取
'===================================================================

' 读取剪贴板文本。若剪贴板为空或不是文本，返回空字符串。
' 该函数只读取，不修改剪贴板内容。
Public Function GetClipboardText() As String
    Dim dataObject As Object

    On Error GoTo ReadFail
    Set dataObject = CreateObject("Forms.DataObject")
    dataObject.GetFromClipboard
    GetClipboardText = dataObject.GetText
    Exit Function

ReadFail:
    GetClipboardText = ""
End Function