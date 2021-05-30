--小号刷帮助 ipx机型
function startClickHelp()
	targetX,targetY = getClickBuilding()
	sysLog(targetX.."----"..targetY.."!!!!")
	toast("开始",1)

	if getColor(2132,86) == 0xfdb732 then
		tap(2132,86)
		mSleep(500)
	end

	while true do

		--升级
		tap(targetX,targetY)
		mSleep(400)
		tap(1665,1118)
		mSleep(400)
		tap(1665,1118)
		mSleep(1200)

		-- 帮助按钮
		tap(681,313)
		mSleep(500)

		--取消升级
		mSleep(1800)
		tap(targetX,targetY)
		mSleep(400)
		tap(1447,1112)
		mSleep(400)
		tap(1279,609)
		mSleep(1500)
	end
end

function getClickBuilding()
	dialog("点击需要刷帮助的建筑",3)
	x,y = catchTouchPoint()
	return y, screenWidth - x
end

