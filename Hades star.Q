[General]
SyntaxVersion=2
BeginHotkey=121
BeginHotkeyMod=0
PauseHotkey=0
PauseHotkeyMod=0
StopHotkey=123
StopHotkeyMod=0
RunOnce=1
EnableWindow=
MacroID=64c81ee7-2e6f-4ae9-af4b-9fcfa498002d
Description=Hades star
Enable=1
AutoRun=0
[Repeat]
Type=0
Number=1
[SetupUI]
Type=1
QUI=Form1
[Relative]
SetupOCXFile=
[Comment]

[Script]
//查找窗口类名(UnityWndClass)或者标题(Hades' Star),返回找到的句柄Hwnd
Hwnd = Plugin.Window.Find("UnityWndClass","Hades' Star")
TracePrint Hwnd
Delay (1000)

size = Plugin.Window.GetClientRect(Hwnd)
TracePrint size
Plugin.Window.SetClientSize Hwnd,1360,768

While True
	Call Plugin.Bkgnd.KeyPress(Hwnd, 27)
	Delay (1 * 1000)
	Call Plugin.Bkgnd.KeyPress(Hwnd, 32)
	Delay (10 * 1000)
    getHydrogenImmediately 
    Delay (3 * 60 * 1000)
Wend

//研究所
Function goResearch()
	Call Plugin.Bkgnd.KeyPress(Hwnd, 117)
End Function

//外交站
Function goDiplomacy()
	goResearch 
	Delay (1500)
	Call Plugin.Bkgnd.MoveTo(Hwnd, 519, 386)
	Call Plugin.Bkgnd.LeftClick(Hwnd, 519, 386)
End Function

//技能收集氢气
Function getHydrogenImmediately()
	//1号
	Call Plugin.Bkgnd.KeyPress(Hwnd, 49)
	Delay (5000)
	Call Plugin.Bkgnd.KeyPress(Hwnd, 81)
	Delay (1000)
	Call Plugin.Bkgnd.KeyPress(Hwnd, 81)
	Delay (1000)
	//2号
	Call Plugin.Bkgnd.KeyPress(Hwnd, 50)
	Delay (5000)
	Call Plugin.Bkgnd.KeyPress(Hwnd, 81)
	Delay (1000)
	Call Plugin.Bkgnd.KeyPress(Hwnd, 81)
	Delay (1000)
	//3号
	Call Plugin.Bkgnd.KeyPress(Hwnd, 51)
	Delay (5000)
	Call Plugin.Bkgnd.KeyPress(Hwnd, 81)
	Delay (1000)
	Call Plugin.Bkgnd.KeyPress(Hwnd, 81)
	Delay (1000)
	//4号
	Call Plugin.Bkgnd.KeyPress(Hwnd, 52)
	Delay (5000)
	Call Plugin.Bkgnd.KeyPress(Hwnd, 81)
	Delay (1000)
	Call Plugin.Bkgnd.KeyPress(Hwnd, 81)
	Delay (1000)
End Function
