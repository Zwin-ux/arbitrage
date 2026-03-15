#define AppName "Superior"
#ifndef AppVersion
  #define AppVersion "0.4.2"
#endif
#define AppPublisher "Superior"
#define AppExeName "market-data-recorder-app.exe"
#ifndef SourceBundleDir
  #define SourceBundleDir "..\..\dist\market-data-recorder-app"
#endif
#ifndef OutputDirPath
  #define OutputDirPath "..\..\dist\installer"
#endif
#ifndef SourceSmokeDir
  #define SourceSmokeDir ""
#endif

[Setup]
AppId={{1D6083E8-1E45-4A3E-8A0C-AB2CF9918B5E}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
DefaultDirName={localappdata}\Programs\{#AppName}
DefaultGroupName={#AppName}
UninstallDisplayIcon={app}\{#AppExeName}
OutputDir={#OutputDirPath}
OutputBaseFilename=market-data-recorder-setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
SetupIconFile=superior.ico
DisableProgramGroupPage=yes

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional icons:"
Name: "runatlogin"; Description: "Launch at login"; GroupDescription: "Startup:"

[Files]
Source: "{#SourceBundleDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "superior.ico"; DestDir: "{app}"; Flags: ignoreversion
#if SourceSmokeDir != ""
Source: "{#SourceSmokeDir}\*"; DestDir: "{app}\market-data-recorder-smoke"; Flags: ignoreversion recursesubdirs createallsubdirs
#endif

[Icons]
Name: "{autoprograms}\{#AppName}"; Filename: "{app}\{#AppExeName}"; IconFilename: "{app}\superior.ico"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExeName}"; IconFilename: "{app}\superior.ico"; Tasks: desktopicon

[Registry]
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "{#AppName}"; ValueData: """{app}\{#AppExeName}"" --auto-launch"; Flags: uninsdeletevalue; Tasks: runatlogin

[Run]
Filename: "{app}\{#AppExeName}"; Description: "Launch {#AppName}"; Flags: nowait postinstall skipifsilent unchecked
