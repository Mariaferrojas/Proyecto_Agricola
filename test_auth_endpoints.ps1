#!/usr/bin/env pwsh


$BaseURL = "http://127.0.0.1:8000/api/auth"

function Print-Section {
    param([string]$Title)
    Write-Host "`n$('='*60)" -ForegroundColor Cyan
    Write-Host "  $Title" -ForegroundColor Cyan
    Write-Host "$('='*60)`n" -ForegroundColor Cyan
}

function Print-Response {
    param([string]$Response, [string]$Title = "Respuesta")
    Write-Host "$Title:" -ForegroundColor Yellow
    try {
        $parsed = $Response | ConvertFrom-Json
        Write-Host ($parsed | ConvertTo-Json -Depth 10) -ForegroundColor Green
    } catch {
        Write-Host $Response -ForegroundColor Green
    }
    Write-Host ""
}

# Test 1: Registro
Print-Section "PRUEBA 1: REGISTRAR USUARIO"

$registerData = @{
    username = "agricola_user_$(Get-Random)"
    email = "user_$(Get-Random)@ejemplo.com"
    password = "SecurePass123!"
    password2 = "SecurePass123!"
} | ConvertTo-Json

Write-Host "POST $BaseURL/register/" -ForegroundColor Cyan
Write-Host "Body: $registerData`n" -ForegroundColor Gray

$response = curl -X POST "$BaseURL/register/" `
    -H "Content-Type: application/json" `
    -d $registerData 2>$null

Print-Response $response "Respuesta"

# Guardar username para el siguiente test
$username = ($registerData | ConvertFrom-Json).username

# Test 2: Login
Print-Section "PRUEBA 2: LOGIN"

$loginData = @{
    username = $username
    password = "SecurePass123!"
} | ConvertTo-Json

Write-Host "POST $BaseURL/login/" -ForegroundColor Cyan
Write-Host "Body: $loginData`n" -ForegroundColor Gray

$loginResponse = curl -X POST "$BaseURL/login/" `
    -H "Content-Type: application/json" `
    -d $loginData 2>$null

Print-Response $loginResponse "Respuesta"

# Extraer tokens
$tokens = $loginResponse | ConvertFrom-Json
$accessToken = $tokens.access
$refreshToken = $tokens.refresh

Write-Host "Access Token: $($accessToken.Substring(0, 20))..." -ForegroundColor Gray
Write-Host "Refresh Token: $($refreshToken.Substring(0, 20))...`n" -ForegroundColor Gray

# Test 3: Verificar Token
Print-Section "PRUEBA 3: VERIFICAR TOKEN"

$verifyData = @{
    token = $accessToken
} | ConvertTo-Json

Write-Host "POST $BaseURL/token/verify/" -ForegroundColor Cyan
Write-Host "Body: {`"token`": `"<token_aqui>`"}`n" -ForegroundColor Gray

$verifyResponse = curl -X POST "$BaseURL/token/verify/" `
    -H "Content-Type: application/json" `
    -d $verifyData 2>$null

Print-Response $verifyResponse "Respuesta"

# Test 4: Refrescar Token
Print-Section "PRUEBA 4: REFRESCAR TOKEN"

$refreshData = @{
    refresh = $refreshToken
} | ConvertTo-Json

Write-Host "POST $BaseURL/token/refresh/" -ForegroundColor Cyan
Write-Host "Body: {`"refresh`": `"<token_aqui>`"}`n" -ForegroundColor Gray

$refreshResponse = curl -X POST "$BaseURL/token/refresh/" `
    -H "Content-Type: application/json" `
    -d $refreshData 2>$null

Print-Response $refreshResponse "Respuesta"

# Test 5: Password Reset
Print-Section "PRUEBA 5: SOLICITAR RESET DE CONTRASEÑA"

$email = ($registerData | ConvertFrom-Json).email
$resetData = @{
    email = $email
} | ConvertTo-Json

Write-Host "POST $BaseURL/password-reset/" -ForegroundColor Cyan
Write-Host "Body: $resetData`n" -ForegroundColor Gray

$resetResponse = curl -X POST "$BaseURL/password-reset/" `
    -H "Content-Type: application/json" `
    -d $resetData 2>$null

Print-Response $resetResponse "Respuesta"

# Test 6: Login Inválido
Print-Section "PRUEBA 6: LOGIN CON CONTRASEÑA INCORRECTA"

$badLoginData = @{
    username = $username
    password = "WrongPassword123!"
} | ConvertTo-Json

Write-Host "POST $BaseURL/login/" -ForegroundColor Cyan
Write-Host "Body: $badLoginData`n" -ForegroundColor Gray

$badLoginResponse = curl -X POST "$BaseURL/login/" `
    -H "Content-Type: application/json" `
    -d $badLoginData 2>$null

Print-Response $badLoginResponse "Respuesta (Debería ser 401)"

Write-Host "`n✓ Pruebas completadas. Consulta Swagger en: http://127.0.0.1:8000/swagger/" -ForegroundColor Green
