$py = "C:\Users\hdh02\AppData\Local\Programs\Python\Python311\python.exe"
$tasks = @{
  "KunStudio_Sales"=@{script="C:\Users\hdh02\Desktop\cheonmyeongdang\departments\intelligence\sales_collector.py"};
  "KunStudio_Security"=@{script="C:\Users\hdh02\Desktop\cheonmyeongdang\departments\security\security_audit.py"};
  "KunStudio_Contests"=@{script="C:\Users\hdh02\Desktop\cheonmyeongdang\departments\intelligence\contests_watch.py"};
  "Cheonmyeongdang_PayPal_Daily_Monitor"=@{script="C:\Users\hdh02\Desktop\cheonmyeongdang\departments\sales-collection\paypal_daily_monitor.py"};
  "KunStudio_SupportQueue"=@{script="C:\Users\hdh02\Desktop\cheonmyeongdang\departments\ceo-briefing\support_agent.py"; extra="process"};
  "KunStudio_AdobeStockBatch"=@{script="D:\scripts\adobe_stock_korean_batch.py"; extra="--all --count-per-niche 3"};
  "KunStudio_CmdViral_12"=@{script="C:\Users\hdh02\Desktop\cheonmyeongdang\departments\media\post_cheonmyeongdang_viral.py"};
  "KunStudio_CmdViral_15"=@{script="C:\Users\hdh02\Desktop\cheonmyeongdang\departments\media\post_cheonmyeongdang_viral.py"};
  "KunStudio_KakaoVC_PitchSend"=$null
}
foreach ($name in $tasks.Keys) {
  $info = $tasks[$name]
  if ($info -eq $null) { continue }
  $arg = if ($info.extra) { "-X utf8 `"$($info.script)`" $($info.extra)" } else { "-X utf8 `"$($info.script)`"" }
  try {
    $action = New-ScheduledTaskAction -Execute $py -Argument $arg
    Set-ScheduledTask -TaskName $name -Action $action -ErrorAction Stop | Out-Null
    Write-Output "OK: $name"
  } catch {
    Write-Output "FAIL: $name => $($_.Exception.Message)"
  }
}
