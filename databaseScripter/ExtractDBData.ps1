param
(
    [string]$serverName, 
    [string]$databaseName, 
    [string]$folderPath,
    [int]$count,
    [string[]]$tables
)

# this script will allow the user to dump out the data from the specified list of tables...

# initialiaze the connection to the server and database
# expects the user to have SSP1 integrated access...
[System.Reflection.Assembly]::LoadWithPartialName('Microsoft.SqlServer.SMO') | out-null
$s = new-object ('Microsoft.SqlServer.Management.Smo.Server') $serverName

# grab the database and create an object to it
$db=$s.Databases[$databaseName]

##$db.Script()

$scrp = new-object ('Microsoft.SqlServer.Management.Smo.Scripter') ($s)

$scrp.Options.AppendToFile = $True
$scrp.Options.ClusteredIndexes = $True
$scrp.Options.DriAll = $True
$scrp.Options.IncludeHeaders = $True
$scrp.Options.ToFileOnly = $True
$scrp.Options.Indexes = $True
$scrp.Options.IncludeIfNotExists = $true

$scrp.Options.ScriptData = $true
$scrp.Options.AppendToFile = $false

[int]$i = $count
$i++

$type = "table"
$action = "data"

write-host $action $type
foreach ($Item in $db.tables) 
{   
    if ($tables -contains $Item.name)
    {
        write-host '    ' $Item.name
	    $scrp.Options.FileName = "$folderPath\$db.$i.$action.$type.$item.SQL" 
	    $scrp.EnumScript($Item) 
    }
}
