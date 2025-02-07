
    $ReportServerUri = "http://hallmark2/Reports"
    $TargetFolder = "/DemoReports/RDLS"

    Import-Module SQLServer
    
    foreach ($file in ['C:\\Users\\bhargavhallmark\\rdl1\\rdl1\\rdls\\2024\\09.September\\03092024\\DemoReportProject\\03092024.rdl']) {
        $reportName = [System.IO.Path]::GetFileNameWithoutExtension($file)
        Write-Host "Deploying $reportName..."
        Publish-RsReport -Path $file -ReportServerUri $ReportServerUri -Destination $TargetFolder -Overwrite
    }
    Write-Host "Deployment complete!"
    