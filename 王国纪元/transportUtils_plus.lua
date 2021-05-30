--plus机型
--开始运输
function startTransport(a,b,c,d,e)
	require("utils")
	foodCount ,stoneCount ,woodCount ,ironCount ,goldCount=0,0,0,0,0
	if tonumber(a) then
		foodCount = tonumber(a)
	end

	if tonumber(b) then
		stoneCount = tonumber(b)
	end

	if tonumber(c) then
		woodCount = tonumber(c)
	end

	if tonumber(d) then
		ironCount = tonumber(d)
	end

	if tonumber(e) then
		goldCount = tonumber(e)
	end
	sysLogLst(foodCount,stoneCount,woodCount,ironCount,goldCount)

	if foodCount == 0 and stoneCount == 0 and woodCount == 0 and  ironCount== 0 and goldCount==0 then
		dialog("设置的运输量都为0，停止运行",3)
		return
	end

	if foodCount >0 then
		for i=1,foodCount do
			transportFood()
			mSleep(2300)
		end
	end

	if stoneCount >0 then
		for i=1,stoneCount do
			transportStone()
			mSleep(2300)
		end
	end

	if woodCount >0 then
		for i=1,woodCount do
			transportWood()
			mSleep(2300)
		end
	end

	if ironCount >0 then
		for i=1,ironCount do
			transportIron()
			mSleep(2300)
		end
	end

	if goldCount >0 then
		for i=1,goldCount do
			transportGold()
			mSleep(2300)
		end
	end
end

-- 运一次大米
function transportFood()
	openTransport()
	mSleep(1200)
	dragFoodProgress()
	mSleep(300)
	confirmTransport();
end

-- 运一次石头
function transportStone()
	openTransport()
	mSleep(1200)
	dragStoneProgress()
	mSleep(300)
	confirmTransport();
end

-- 运一次木头
function transportWood()
	openTransport()
	mSleep(1200)
	dragWoodProgress()
	mSleep(300)
	confirmTransport();
end

-- 运一次铁矿
function transportIron()
	openTransport()
	mSleep(1200)
	dragIronProgress()
	mSleep(300)
	confirmTransport();
end

-- 运一次金币
function transportGold()
	openTransport()
	mSleep(1200)
	dragGoldProgress()
	mSleep(300)
	confirmTransport();
end

--打开运输界面
function openTransport()
	tap(1566,212)
	mSleep(400)
	tap(1105,653)
	mSleep(150)
end

--大米进度条
function dragFoodProgress()
	swip(1074,524, 1164,524)
end

--石头进度条
function dragStoneProgress()
	swip(1074, 690, 1164, 690)
end

--木头进度条
function dragWoodProgress()
	swip(1074, 858, 1164, 858)
end

--铁矿进度条
function dragIronProgress()
	swip(1074, 1025, 1164, 1025)
end

--金币进度条
function dragGoldProgress()
	swip(1074, 1191, 1164, 1191)
end

--运输按钮
function confirmTransport()
	tap(1599,1131)
	mSleep(200);
	tap(1281,579)
end
