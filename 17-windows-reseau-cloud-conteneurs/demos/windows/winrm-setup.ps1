# À exécuter UNE FOIS sur la machine Windows cible (PowerShell administrateur) pour activer WinRM.
# En production : préférez un certificat valide + HTTPS, ou OpenSSH (Windows Server 2019+).
$ErrorActionPreference = "Stop"
Enable-PSRemoting -Force
winrm quickconfig -q
# Écouteur HTTPS avec certificat auto-signé (LABO)
$cert = New-SelfSignedCertificate -DnsName $env:COMPUTERNAME -CertStoreLocation Cert:\LocalMachine\My
New-Item -Path WSMan:\localhost\Listener -Transport HTTPS -Address * -CertificateThumbPrint $cert.Thumbprint -Force
New-NetFirewallRule -DisplayName "WinRM HTTPS" -Direction Inbound -LocalPort 5986 -Protocol TCP -Action Allow
Set-Item -Path WSMan:\localhost\Service\Auth\Basic -Value $false
Write-Host "WinRM prêt sur le port 5986"
