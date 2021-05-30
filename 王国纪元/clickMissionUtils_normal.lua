-- 点内政 联盟任务 普通机型
function startClickMission(count)
	
	clickCount = 0
	if(tonumber(count)) then
		clickCount = tonumber(count)
	end
	
	for i=1,clickCount  do
		toast("还剩" .. clickCount - i .. "张",1);
		while true do
			for tmpi=1,3 do
				tap(1034,297)
				mSleep(150)
			end
			if checkHaveMission() == false then
				break
			end
		end
		if i < clickCount  then
			if refreshMission() == false then
				break
			end
		else
			break
		end
	end
	
end

--刷新任务
function refreshMission()
	tap(601,224)
	mSleep(150)
	--if checkRefreshMissionByGem() then
	--	return false
	--end
	tap(668,452)
	mSleep(1200)
	return true
end

--检查是否出现用水晶购买卷轴
--function checkRefreshMissionByGem()
--	--color = getColor(1161,655);
--	if color == 0xce8ef9 then
--		return true
--	end
--	return false
--end

--检查是否还有任务
function checkHaveMission()
	color = getColor(1128,333); --获取(100,100)的颜色值，赋值给color变量
	if color == 0x25d2ff then   --如果该点的颜色值等于0xffffff
		return true
	end
	return false
end