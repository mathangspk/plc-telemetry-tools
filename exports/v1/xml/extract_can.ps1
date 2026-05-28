[xml] = Get-Content 'apollo-3cs-0.004bf - eolus- v5.xml'
 = New-Object System.Xml.XmlNamespaceManager(.NameTable)
.AddNamespace('ns', 'http://www.3s-software.com/plcopenxml/')

foreach ($dev in $xml.SelectNodes('//ns:Device', $ns)) {
    $name = $dev.SelectSingleNode('.//ns:DeviceIdentification/ns:Type/ns:Name', $ns).InnerText
    if ($name) {
        Write-Output "Device: $name"
        $prod = $dev.SelectSingleNode('.//ns:Value[@visiblename=""Heartbeat-Producer Time""]', $ns).InnerText
        $cons = $dev.SelectSingleNode('.//ns:Element[@visiblename=""HeartbeatTime""]', $ns).InnerText
        if ($prod) { Write-Output "  Producer: $prod" }
        if ($cons) { Write-Output "  Consumer: $cons" }
    }
}
