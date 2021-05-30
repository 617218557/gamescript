--点任务 ipx连点判断ok
init(1)
require "ui"
showStartUi()
mSleep(2000)
-- iOS:屏幕方向，0 - 竖屏，1 - Home 键在右边，2 - Home 键在左边
deviceType = 1   --1 iphoneX , 2  iPhone6 Plus/6s Plus/7 Plus/8 Plus,  3 iPhone6/7/8/(s)

screenWidth,screenHeight = getScreenSize()
if screenWidth == 1125 and screenHeight == 2436 then
	deviceType = 1
elseif screenWidth == 1242 and screenHeight == 2208 then
	deviceType = 2
elseif screenWidth == 750 and screenHeight == 1334 then
	deviceType = 3
	dialog("750*1334机型只支持点内政、联盟任务，勿使用其他功能")
elseif screenWidth == 1125 and  screenHeight == 2001 then
	--貌似有些情况下关闭放大模式也会识别到这里   目前只有1个人碰到过而且无法验证问题
	--dialog("请关闭plus机型的放大模式",3)
	--return
	deviceType = 2
else
	dialog("不支持本机型",3)
	return
end
if missionSelect == "运输" then
	toast("运输",1)
	-- 开启自动运输
	if(deviceType == 1) then
		require "transportUtils_ipx"
	elseif (deviceType == 2) then
		require "transportUtils_plus"
	end
	startTransport(transportFoodCount,transportStoneCount,transportWoodCount,transportIronCount,transportGoldCount)
elseif missionSelect == "点任务" then
	toast("点任务",1)
	-- 开始点任务
	if(deviceType == 1) then
		require "clickMissionUtils_ipx"
	elseif (deviceType == 2) then
		require "clickMissionUtils_plus"
	elseif (deviceType ==3) then
		require "clickMissionUtils_normal"
	end
	startClickMission(clickMissionCount)
elseif missionSelect == "刷帮助" then
	toast("刷帮助",1)
	if(deviceType == 1) then
		require "clickHelpUtils_ipx"
	elseif (deviceType == 2) then
		require "clickHelpUtils_plus"
	end
	startClickHelp()
end
dialog("脚本结束", 0)