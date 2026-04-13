#define AppName "Manta Airfoil Tools"
#define AppPublisher "Fabio Giuliodori"
#define AppPublisherURL "https://duilio.cc"
#define AirfoilDbUrl "https://github.com/Giuliodori/airfoil-db-maker/releases/latest/download/airfoil.db"
#define XfoilZipUrl "https://web.mit.edu/drela/Public/web/xfoil/XFOIL6.99.zip"

#ifndef AppVersion
  #define AppVersion "1.0.0"
#endif

#ifndef AppExePath
  #error AppExePath must be passed via /DAppExePath=<full_exe_path>
#endif

#ifndef AppExeName
  #define AppExeName "Manta_Airfoil_Tools_portable.exe"
#endif

#ifndef AppSetupIconPath
  #define AppSetupIconPath "images\ico.ico"
#endif

#ifndef AppWizardImageBmpPath
  #define AppWizardImageBmpPath ""
#endif

#ifndef AppWizardSmallImageBmpPath
  #define AppWizardSmallImageBmpPath ""
#endif

[Setup]
AppId={{8CD0F2A9-EA3F-4D91-B7C5-271B68D295E1}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
AppPublisherURL={#AppPublisherURL}
AppSupportURL={#AppPublisherURL}
AppUpdatesURL={#AppPublisherURL}
AppComments=Brand: Manta Airlab
DefaultDirName={autopf}\{#AppName}
DefaultGroupName={#AppName}
UninstallDisplayIcon={app}\{#AppExeName}
OutputDir=dist
OutputBaseFilename=Manta_Airfoil_Tools_setup_{#AppVersion}
Compression=lzma
SolidCompression=yes
WizardStyle=modern
SetupIconFile={#AppSetupIconPath}
#if AppWizardImageBmpPath != ""
WizardImageFile={#AppWizardImageBmpPath}
#endif
#if AppWizardSmallImageBmpPath != ""
WizardSmallImageFile={#AppWizardSmallImageBmpPath}
#endif
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional icons:"
Name: "runtimeassets"; Description: "Download runtime assets (airfoil.db + XFOIL)"; GroupDescription: "Runtime assets:"

[Dirs]
Name: "{app}\database"
Name: "{app}\xfoil"

[Files]
Source: "{#AppExePath}"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\{#AppName}"; Filename: "{app}\{#AppExeName}"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#AppExeName}"; Description: "Launch {#AppName}"; Flags: nowait postinstall skipifsilent

[Code]
var
  DownloadPage: TDownloadWizardPage;

function FindXfoilExe(const Dir: String; var FoundPath: String): Boolean; forward;

procedure InitializeWizard;
begin
  DownloadPage := CreateDownloadPage(
    'Downloading runtime assets',
    'Downloading airfoil.db and XFOIL package...',
    nil
  );
  DownloadPage.ShowBaseNameInsteadOfUrl := True;
end;

procedure DownloadRuntimeAssetsIfSelected;
var
  DbTmpPath: String;
  ZipTmpPath: String;
  DbDestPath: String;
  XfoilDir: String;
  RootXfoilExe: String;
  FoundXfoilExe: String;
  ResultCode: Integer;
  PsCmd: String;
begin
  if not WizardIsTaskSelected('runtimeassets') then
    Exit;

  DbTmpPath := ExpandConstant('{tmp}\airfoil.db');
  ZipTmpPath := ExpandConstant('{tmp}\XFOIL6.99.zip');
  DbDestPath := ExpandConstant('{app}\database\airfoil.db');
  XfoilDir := ExpandConstant('{app}\xfoil');
  RootXfoilExe := AddBackslash(XfoilDir) + 'xfoil.exe';

  DownloadPage.Clear;
  DownloadPage.Add('{#AirfoilDbUrl}', 'airfoil.db', '');
  DownloadPage.Add('{#XfoilZipUrl}', 'XFOIL6.99.zip', '');
  DownloadPage.Show;
  try
    DownloadPage.Download;
  finally
    DownloadPage.Hide;
  end;

  ForceDirectories(ExtractFileDir(DbDestPath));
  ForceDirectories(XfoilDir);

  if not FileCopy(DbTmpPath, DbDestPath, False) then
    RaiseException('Failed to copy airfoil.db to install folder.');

  PsCmd :=
    '-NoProfile -ExecutionPolicy Bypass -Command ' +
    '"Expand-Archive -LiteralPath ''' + ZipTmpPath + ''' -DestinationPath ''' + XfoilDir + ''' -Force"';
  if not Exec('powershell.exe', PsCmd, '', SW_HIDE, ewWaitUntilTerminated, ResultCode) then
    RaiseException('Failed to start PowerShell for XFOIL extraction.');
  if ResultCode <> 0 then
    RaiseException('PowerShell extraction failed for XFOIL package.');
  FoundXfoilExe := '';
  if FindXfoilExe(XfoilDir, FoundXfoilExe) then
  begin
    if CompareText(FoundXfoilExe, RootXfoilExe) <> 0 then
    begin
      if not FileCopy(FoundXfoilExe, RootXfoilExe, False) then
        RaiseException('Failed to copy xfoil.exe to install folder.');
    end;
  end
  else
    RaiseException('xfoil.exe not found in downloaded XFOIL archive.');
end;

procedure CleanupXfoilDirKeepExe(const Dir, KeepPath: String);
var
  FindRec: TFindRec;
  Candidate: String;
begin
  if not DirExists(Dir) then
    Exit;
  if not FindFirst(AddBackslash(Dir) + '*', FindRec) then
    Exit;
  try
    repeat
      if (FindRec.Name = '.') or (FindRec.Name = '..') then
        Continue;
      Candidate := AddBackslash(Dir) + FindRec.Name;
      if (FindRec.Attributes and FILE_ATTRIBUTE_DIRECTORY) <> 0 then
      begin
        CleanupXfoilDirKeepExe(Candidate, KeepPath);
        RemoveDir(Candidate);
      end
      else if CompareText(Candidate, KeepPath) <> 0 then
        DeleteFile(Candidate);
    until not FindNext(FindRec);
  finally
    FindClose(FindRec);
  end;
end;

function FindXfoilExe(const Dir: String; var FoundPath: String): Boolean;
var
  FindRec: TFindRec;
  Candidate: String;
begin
  Result := False;
  if not FindFirst(AddBackslash(Dir) + '*', FindRec) then
    Exit;
  try
    repeat
      if (FindRec.Name = '.') or (FindRec.Name = '..') then
        Continue;
      Candidate := AddBackslash(Dir) + FindRec.Name;
      if (FindRec.Attributes and FILE_ATTRIBUTE_DIRECTORY) <> 0 then
      begin
        if FindXfoilExe(Candidate, FoundPath) then
        begin
          Result := True;
          Exit;
        end;
      end
      else if CompareText(FindRec.Name, 'xfoil.exe') = 0 then
      begin
        FoundPath := Candidate;
        Result := True;
        Exit;
      end;
    until not FindNext(FindRec);
  finally
    FindClose(FindRec);
  end;
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  RootXfoilExe: String;
  FoundXfoilExe: String;
begin
  if CurStep = ssInstall then
  begin
    DownloadRuntimeAssetsIfSelected;
    Exit;
  end;
  if CurStep = ssPostInstall then
  begin
    RootXfoilExe := ExpandConstant('{app}\xfoil\xfoil.exe');
    if FileExists(RootXfoilExe) then
    begin
      CleanupXfoilDirKeepExe(ExpandConstant('{app}\xfoil'), RootXfoilExe);
      Exit;
    end;
    FoundXfoilExe := '';
    if FindXfoilExe(ExpandConstant('{app}\xfoil'), FoundXfoilExe) then
    begin
      if CompareText(FoundXfoilExe, RootXfoilExe) <> 0 then
      begin
        if not FileCopy(FoundXfoilExe, RootXfoilExe, False) then
          Log('Warning: failed to copy ' + FoundXfoilExe + ' to ' + RootXfoilExe);
      end;
      CleanupXfoilDirKeepExe(ExpandConstant('{app}\xfoil'), RootXfoilExe);
    end;
  end;
end;
