$py = "C:\Users\hdh02\AppData\Local\Programs\Python\Python311\python.exe"
$tasks = @{
  "KunStudio_Twitter_Daily"=@{script="C:\Users\hdh02\Desktop\cheonmyeongdang\scripts\morning_post_twitter.py"};
  "KunStudio_SEO_BlogFactory_0600"=@{script="C:\Users\hdh02\Desktop\cheonmyeongdang\departments\seo_blog_factory\generate.py"};
  "KunStudio_SEO_BlogFactory_0900"=@{script="C:\Users\hdh02\Desktop\cheonmyeongdang\departments\seo_blog_factory\generate.py"};
  "KunStudio_SEO_BlogFactory_1300"=@{script="C:\Users\hdh02\Desktop\cheonmyeongdang\departments\seo_blog_factory\generate.py"};
  "KunStudio_SEO_BlogFactory_1700"=@{script="C:\Users\hdh02\Desktop\cheonmyeongdang\departments\seo_blog_factory\generate.py"};
  "KunStudio_SEO_BlogFactory_2100"=@{script="C:\Users\hdh02\Desktop\cheonmyeongdang\departments\seo_blog_factory\generate.py"};
  "HexDrop_Postiz_PM"=@{script="D:\scripts\hexdrop_postiz_pipeline.py"; extra="--slot evening"};
  "HexDrop_Postiz_AM"=@{script="D:\scripts\hexdrop_postiz_pipeline.py"; extra="--slot morning"};
}
foreach ($name in $tasks.Keys) {
  $info = $tasks[$name]
  $arg = if ($info.extra) { "-X utf8 `"$($info.script)`" $($info.extra)" } else { "-X utf8 `"$($info.script)`"" }
  try {
    $action = New-ScheduledTaskAction -Execute $py -Argument $arg
    Set-ScheduledTask -TaskName $name -Action $action -ErrorAction Stop | Out-Null
    Write-Output "OK: $name"
  } catch {
    Write-Output "FAIL: $name => $($_.Exception.Message)"
  }
}
