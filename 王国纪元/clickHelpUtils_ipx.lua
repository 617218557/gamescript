--小号刷帮助 ipx机型
function startClickHelp()
	targetX,targetY = getClickBuilding()
	toast("开始",1)

	if getColor(2273,75) == 0xf5b950 then
		tap(2273,75)
		mSleep(500)
	end

	while true do

		--升级
		tap(targetX,targetY)
		mSleep(400)
		tap(1727,1001)
		mSleep(400)
		tap(1727,1001)
		mSleep(1200)

		-- 帮助按钮
		tap(708,285 )
		mSleep(500)

		--取消升级
		mSleep(1800)
		tap(targetX,targetY)
		mSleep(400)
		tap(1528,1010)
		mSleep(400)
		tap(1374,546)
		mSleep(1500)
	end
end

function getClickBuilding()
	dialog("点击需要刷帮助的建筑",3)
	x,y = catchTouchPoint()
	return y, screenWidth - x
end

