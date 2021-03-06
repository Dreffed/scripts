param
(
	[alias("s")]
    [string]$serverName, 
   	[alias("d")]
    [string]$databaseName, 
   	[alias("f")]
    [string]$folderPath,
   	[alias("r")]
    [switch]$scriptDrops,
   	[alias("a")]
	[switch]$scriptData
)

# this will script out the following based on the params passed in...
# drop statements
# create statements, broken down into tables, view, sp etc.
#

[System.Reflection.Assembly]::LoadWithPartialName('Microsoft.SqlServer.SMO') | out-null
$s = new-object ('Microsoft.SqlServer.Management.Smo.Server') $serverName

$db=$s.Databases[$databaseName]

##$db.Script()
 
$scrp = new-object ('Microsoft.SqlServer.Management.Smo.Scripter') ($s)

$scrp.Options.AppendToFile = $True
$scrp.Options.DriAll = $True
$scrp.Options.IncludeHeaders = $True
$scrp.Options.ToFileOnly = $True
$scrp.Options.Indexes = $True
$scrp.Options.ClusteredIndexes = $True
$scrp.Options.IncludeIfNotExists = $true
$scrp.Options.Triggers = $True

[int]$i = 0
if ($scriptDrops)
{
	[string]$action = "drop"
	[string]$type = "table"

	$scrp.Options.ScriptDrops = $True 
	$i++
	$scrp.Options.FileName = "$folderPath\$db.$i.$action.$type.SQL" 
    write-host $type
	foreach ($Item in $db.tables) 
	{   
		if (!$item.IsSystemObject)
		{
			write-host '    ' $Item.name
			$scrp.Script($Item) 
		}
	}

	$i++
	$type = "view"
    write-host $type
	$scrp.Options.FileName = "$folderPath\$db.$i.$action.$type.SQL" 
	foreach ($Item in $db.Views) 
	{   
		if (!$item.IsSystemObject)
		{
			write-host '    ' $Item.name
			$scrp.Script($Item) 
		}
	}

	$i++
	$type = "proc"
    write-host $type
	$scrp.Options.FileName = "$folderPath\$db.$i.$action.$type.SQL" 
	foreach ($Item in $db.StoredProcedures) 
	{   
		if (!$item.IsSystemObject)
		{
			write-host '    ' $Item.name
			$scrp.Script($Item) 
		}
	}
}

#script data
$scrp.Options.ScriptDrops = $false
$scrp.Options.ScriptData = $false
$scrp.Options.AppendToFile = $true
$scrp.Options.ClusteredIndexes = $false
$scrp.Options.DriAll = $false
$scrp.Options.IncludeHeaders = $True
$scrp.Options.ToFileOnly = $True
$scrp.Options.Indexes = $false
$scrp.Options.IncludeIfNotExists = $true

$i++

$type = "table"
$action = "create"

if ($scriptData)
{
	$scrp.Options.ScriptData = $true
	$scrp.Options.AppendToFile = $false
	$action = "data"

    write-host $action $type
	foreach ($Item in $db.tables) 
	{   
		if (!$item.IsSystemObject)
		{
			write-host '    ' $Item.name
			$scrp.Options.FileName = "$folderPath\$db.$i.$action.$type.$item.SQL" 
			$scrp.EnumScript($Item) 
		}
	}
	$action = "create"
	$scrp.Options.ScriptData = $false
	$scrp.Options.AppendToFile = $true
}
else
{
	$scrp.Options.FileName = "$folderPath\$db.$i.$action.$type.SQL" 
    write-host $action $type
	foreach ($Item in $db.tables) 
	{   
		if (!$item.IsSystemObject)
		{
			write-host '    ' $Item.name
			$scrp.Script($Item) 
		}
	}
}

$i++
$type = "view"
$scrp.Options.FileName = "$folderPath\$db.$i.$action.$type.SQL" 
write-host $type
foreach ($Item in $db.Views) 
{   
	if (!$item.IsSystemObject)
	{
		write-host '    ' $Item.name
		$scrp.Script($Item) 
	}
}

$i++
$type = "proc"
$scrp.Options.FileName = "$folderPath\$db.$i.$action.$type.SQL" 
write-host $type
foreach ($Item in $db.StoredProcedures) 
{   
	if (!$item.IsSystemObject)
	{
		write-host '    ' $Item.name
		$scrp.Script($Item) 
	}
}

$i
