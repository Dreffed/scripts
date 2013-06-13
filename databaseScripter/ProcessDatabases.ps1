# will run the scripts for the servers and databases, then launch a compare to highlight differences...
# Vars
#   ServerTable
#       serverName  databaseName
#   DataTables
#       Table / View Name
#   
#   OutputPath
#
# Process
#   for each server
#       create a dated output folder
#           run the ./GenerateDBScriptsData script
#       for each table
#           run the ./ExtractDBData script
#
#   for each output folder
#       perform a diff on each folder / file
#       
#   display the results...
#   generate patch file...

## ScriptTest.ps1
Write-Host "InvocationName:" $MyInvocation.InvocationName
Write-Host "Path:" $MyInvocation.MyCommand.Path

$ScriptPath = Split-Path $MyInvocation.MyCommand.Path
Write-Host @ScriptPath

[int]$size = 1

$serverTable = New-Object 'object[,]' $size,2

[int]$i = -1

$i++
$serverTable[$i,0] = '<server>'
$serverTable[$i,1] = '<database>'
write-host $serverTable[$i,0] $serverTable[$i,1]

# store the tables to dump data from...
[string[]]$tables = 'sysParm','INFORMATION_SCHEMA.COLUMNS','INFORMATION_SCHEMA.VIEW_COLUMN_USAGE','INFORMATION_SCHEMA.PARAMETERS'

#build a date string
[string]$retDate = get-date -format "yyyyMMdd"
[string]$folderPath = '<path to save schemas>'

for ([int]$j = 0; $j -le $i; $j++)
{   
    #process 

    # Assemble the path
    [string]$outputPath = $folderPath + '\dbSchemas\' + $serverTable[$j,0] + $serverTable[$j,1] + $retDate
    
    # check and create
    if (test-path $outputPath)
    {
    
    }
    else
    {
        # create the directory...
        New-Item -ItemType directory -Path $outputPath
    }
    
    # call the extract schema
    $command = "$scriptPath\GenerateDBScriptsData.ps1"
    $k = &$command -serverName $serverTable[$j,0] -databaseName $serverTable[$j,1] -folderPath $outputPath    
    
    # Call the ExtractData script
    $command = "$scriptPath\ExtractDBData.ps1"
    &$command -serverName $serverTable[$j,0] -databaseName $serverTable[$j,1] -folderPath $outputPath -count $k -tables $tables
}

