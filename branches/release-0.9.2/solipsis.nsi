; Script generated by the HM NIS Edit Script Wizard.

; HM NIS Edit Wizard helper defines
!define PRODUCT_NAME "Solipsis"
!define PRODUCT_VERSION "0.9.2"
!define PRODUCT_PUBLISHER "FTR&D"
!define PRODUCT_WEB_SITE "http://solipsis.netofpeers.net"
!define PRODUCT_DIR_REGKEY "Software\Microsoft\Windows\CurrentVersion\App Paths\w9xpopen.exe"
!define PRODUCT_UNINST_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}"
!define PRODUCT_UNINST_ROOT_KEY "HKLM"
!define PRODUCT_STARTMENU_REGVAL "NSIS:StartMenuDir"

SetCompressor lzma

; MUI 1.67 compatible ------
!include "MUI.nsh"

; MUI Settings
!define MUI_ABORTWARNING
!define MUI_ICON "${NSISDIR}\Contrib\Graphics\Icons\modern-install.ico"
!define MUI_UNICON "${NSISDIR}\Contrib\Graphics\Icons\modern-uninstall.ico"

; Language Selection Dialog Settings
!define MUI_LANGDLL_REGISTRY_ROOT "${PRODUCT_UNINST_ROOT_KEY}"
!define MUI_LANGDLL_REGISTRY_KEY "${PRODUCT_UNINST_KEY}"
!define MUI_LANGDLL_REGISTRY_VALUENAME "NSIS:Language"

; Welcome page
!insertmacro MUI_PAGE_WELCOME
; License page
!insertmacro MUI_PAGE_LICENSE "LICENSE"
; Directory page
!insertmacro MUI_PAGE_DIRECTORY
; Start menu page
var ICONS_GROUP
!define MUI_STARTMENUPAGE_NODISABLE
!define MUI_STARTMENUPAGE_DEFAULTFOLDER "Solipsis"
!define MUI_STARTMENUPAGE_REGISTRY_ROOT "${PRODUCT_UNINST_ROOT_KEY}"
!define MUI_STARTMENUPAGE_REGISTRY_KEY "${PRODUCT_UNINST_KEY}"
!define MUI_STARTMENUPAGE_REGISTRY_VALUENAME "${PRODUCT_STARTMENU_REGVAL}"
!insertmacro MUI_PAGE_STARTMENU Application $ICONS_GROUP
; Instfiles page
!insertmacro MUI_PAGE_INSTFILES
; Finish page
!define MUI_FINISHPAGE_RUN "$INSTDIR\navigator.exe"
!define MUI_FINISHPAGE_SHOWREADME "$INSTDIR\README.txt"
!insertmacro MUI_PAGE_FINISH

; Uninstaller pages
!insertmacro MUI_UNPAGE_INSTFILES

; Language files
!insertmacro MUI_LANGUAGE "English"
!insertmacro MUI_LANGUAGE "French"
!insertmacro MUI_LANGUAGE "German"
!insertmacro MUI_LANGUAGE "Japanese"
!insertmacro MUI_LANGUAGE "Slovenian"

; Reserve files
!insertmacro MUI_RESERVEFILE_INSTALLOPTIONS

; MUI end ------

Name "${PRODUCT_NAME} ${PRODUCT_VERSION}"
OutFile "Install.exe"
InstallDir "$PROGRAMFILES\Solipsis"
InstallDirRegKey HKLM "${PRODUCT_DIR_REGKEY}" ""
ShowInstDetails show
ShowUnInstDetails show

Function .onInit
  !insertmacro MUI_LANGDLL_DISPLAY
FunctionEnd

Section "Solipsis" SEC01
  SetOutPath "$INSTDIR"
  SetOverwrite try
  File "dist\_socket.pyd"
  File "dist\_ssl.pyd"
  File "dist\bz2.pyd"
  File "dist\pyexpat.pyd"
  File "dist\select.pyd"
  File "dist\unicodedata.pyd"
  File "dist\zlib.pyd"
  File "dist\_imaging.pyd"
  File "dist\_imagingft.pyd"
  File "dist\_imagingtk.pyd"
  File "dist\_iocp.pyd"
  File "dist\_c_urlarg.pyd"
  File "dist\cBanana.pyd"
  File "dist\_activex.pyd"
  File "dist\_animate.pyd"
  File "dist\_calendar.pyd"
  File "dist\_controls_.pyd"
  File "dist\_core_.pyd"
  File "dist\_gdi_.pyd"
  File "dist\_gizmos.pyd"
  File "dist\_glcanvas.pyd"
  File "dist\_grid.pyd"
  File "dist\_html.pyd"
  File "dist\_media.pyd"
  File "dist\_misc_.pyd"
  File "dist\_stc.pyd"
  File "dist\_webkit.pyd"
  File "dist\_windows_.pyd"
  File "dist\_wizard.pyd"
  File "dist\_xrc.pyd"
  File "dist\wxmsw26uh_animate_vc.dll"
  File "dist\wxmsw26uh_gizmos_vc.dll"
  File "dist\wxmsw26uh_gizmos_xrc_vc.dll"
  File "dist\wxmsw26uh_gl_vc.dll"
  File "dist\wxmsw26uh_stc_vc.dll"
  File "dist\wxmsw26uh_vc.dll"
  File "dist\_zope_interface_coptimizations.pyd"
  File "dist\library.zip"
  File "dist\w9xpopen.exe"
  File "dist\entities.met"
  File "dist\LICENSE"
  File "dist\README.txt"
  SetOutPath "$INSTDIR\img"
  File "dist\img\logo.gif"
  File "dist\img\mask.png"
  File "dist\img\tmp_small_chat_blue.png"
  File "dist\img\send_blue.png"
  File "dist\img\b_filter_n.png"
  File "dist\img\logo2.gif"
  File "dist\img\im_chat.png"
  File "dist\img\small_transfer_red.png"
  File "dist\img\chat_red.png"
  File "dist\img\avat_gh.png"
  File "dist\img\icon_solipsis.png"
  File "dist\img\picto_chat.png"
  File "dist\img\picto_file.png"
  File "dist\img\small_chat_blue.png"
  File "dist\img\transfer_red.png"
  File "dist\img\avat_grey.png"
  File "dist\img\avat_small_01.png"
  File "dist\img\send_red.png"
  File "dist\img\avat_small_02.png"
  File "dist\img\chat_blue.png"
  File "dist\img\top_banner.png"
  File "dist\img\picto_avat.png"
  File "dist\img\im_solipsis.png"
  File "dist\img\im_2D.png"
  File "dist\img\avat_white.png"
  File "dist\img\solipsis.ico"
  File "dist\img\transfer_blue.png"
  File "dist\img\b_filter_a.png"
  File "dist\img\avat_orange.png"
  File "dist\img\tmp_small_transfer_red.png"
  SetOutPath "$INSTDIR"
  File "dist\msvcr71.dll"
  SetOutPath "$INSTDIR\conf"
  File "dist\conf\solipsis.conf"
  SetOutPath "$INSTDIR\solipsis\services"
  File "dist\solipsis\services\plugin.py"
  File "dist\solipsis\services\__init__.py"
  File "dist\solipsis\services\wxcollector.py"
  File "dist\solipsis\services\collector.py"
  SetOutPath "$INSTDIR\solipsis\services\avatar"
  File "dist\solipsis\services\avatar\gui.py"
  File "dist\solipsis\services\avatar\network.py"
  File "dist\solipsis\services\avatar\plugin.py"
  File "dist\solipsis\services\avatar\__init__.py"
  File "dist\solipsis\services\avatar\repository.py"
  SetOutPath "$INSTDIR\solipsis\services\avatar\po"
  File "dist\solipsis\services\avatar\po\messages.pot"
  SetOutPath "$INSTDIR\solipsis\services\avatar\po\de\LC_MESSAGES"
  File "dist\solipsis\services\avatar\po\de\LC_MESSAGES\solipsis_avatar.po"
  File "dist\solipsis\services\avatar\po\de\LC_MESSAGES\solipsis_avatar.mo"
  SetOutPath "$INSTDIR\solipsis\services\avatar\po\fr\LC_MESSAGES"
  File "dist\solipsis\services\avatar\po\fr\LC_MESSAGES\solipsis_avatar.po"
  File "dist\solipsis\services\avatar\po\fr\LC_MESSAGES\solipsis_avatar.mo"
  SetOutPath "$INSTDIR\solipsis\services\avatar\po\ja\LC_MESSAGES"
  File "dist\solipsis\services\avatar\po\ja\LC_MESSAGES\solipsis_avatar.po"
  File "dist\solipsis\services\avatar\po\ja\LC_MESSAGES\solipsis_avatar.mo"
  SetOutPath "$INSTDIR\solipsis\services\avatar\po\sl\LC_MESSAGES"
  File "dist\solipsis\services\avatar\po\sl\LC_MESSAGES\solipsis_avatar.po"
  File "dist\solipsis\services\avatar\po\sl\LC_MESSAGES\solipsis_avatar.mo"
  SetOutPath "$INSTDIR\solipsis\services\chat"
  File "dist\solipsis\services\chat\gui.py"
  File "dist\solipsis\services\chat\gui.xrc"
  File "dist\solipsis\services\chat\plugin.py"
  File "dist\solipsis\services\chat\__init__.py"
  SetOutPath "$INSTDIR\solipsis\services\chat\po"
  File "dist\solipsis\services\chat\po\messages.pot"
  SetOutPath "$INSTDIR\solipsis\services\chat\po\de\LC_MESSAGES"
  File "dist\solipsis\services\chat\po\de\LC_MESSAGES\solipsis_chat.po"
  File "dist\solipsis\services\chat\po\de\LC_MESSAGES\solipsis_chat.mo"
  SetOutPath "$INSTDIR\solipsis\services\chat\po\fr\LC_MESSAGES"
  File "dist\solipsis\services\chat\po\fr\LC_MESSAGES\solipsis_chat.po"
  File "dist\solipsis\services\chat\po\fr\LC_MESSAGES\solipsis_chat.mo"
  SetOutPath "$INSTDIR\solipsis\services\chat\po\ja\LC_MESSAGES"
  File "dist\solipsis\services\chat\po\ja\LC_MESSAGES\solipsis_chat.po"
  File "dist\solipsis\services\chat\po\ja\LC_MESSAGES\solipsis_chat.mo"
  SetOutPath "$INSTDIR\solipsis\services\chat\po\sl\LC_MESSAGES"
  File "dist\solipsis\services\chat\po\sl\LC_MESSAGES\solipsis_chat.po"
  File "dist\solipsis\services\chat\po\sl\LC_MESSAGES\solipsis_chat.mo"
  SetOutPath "$INSTDIR\solipsis\services\profile"
  File "dist\solipsis\services\profile\data.py"
  File "dist\solipsis\services\profile\view.py"
  File "dist\solipsis\services\profile\prefs.py"
  File "dist\solipsis\services\profile\simple_facade.py"
  File "dist\solipsis\services\profile\pathutils.py"
  File "dist\solipsis\services\profile\file_document.py"
  File "dist\solipsis\services\profile\document.py"
  File "dist\solipsis\services\profile\preview.css"
  File "dist\solipsis\services\profile\filter_document.py"
  File "dist\solipsis\services\profile\regex.html"
  File "dist\solipsis\services\profile\network.py"
  File "dist\solipsis\services\profile\preview.html"
  File "dist\solipsis\services\profile\plugin.py"
  File "dist\solipsis\services\profile\__init__.py"
  File "dist\solipsis\services\profile\cache_document.py"
  File "dist\solipsis\services\profile\facade.py"
  SetOutPath "$INSTDIR\solipsis\services\profile\gui"
  File "dist\solipsis\services\profile\gui\gui.wxg"
  File "dist\solipsis\services\profile\gui\profiling.py"
  File "dist\solipsis\services\profile\gui\CustomPanel.py"
  File "dist\solipsis\services\profile\gui\AboutDialog.py"
  File "dist\solipsis\services\profile\gui\FilePanel.py"
  File "dist\solipsis\services\profile\gui\FileDialog.py"
  File "dist\solipsis\services\profile\gui\__init__.py"
  File "dist\solipsis\services\profile\gui\FilterFrame.py"
  File "dist\solipsis\services\profile\gui\gui-viewer.wxg"
  File "dist\solipsis\services\profile\gui\PreviewPanel.py"
  File "dist\solipsis\services\profile\gui\EditorFrame.py"
  File "dist\solipsis\services\profile\gui\viewer.py"
  File "dist\solipsis\services\profile\gui\PersonalPanel.py"
  File "dist\solipsis\services\profile\gui\BlogPanel.py"
  File "dist\solipsis\services\profile\gui\BlogDialog.py"
  File "dist\solipsis\services\profile\gui\FileFilterPanel.py"
  File "dist\solipsis\services\profile\gui\MatchFrame.py"
  File "dist\solipsis\services\profile\gui\PersonalFilterPanel.py"
  File "dist\solipsis\services\profile\gui\MatchPanel.py"
  File "dist\solipsis\services\profile\gui\ViewerFrame.py"
  File "dist\solipsis\services\profile\gui\ProfileDialog.py"
  File "dist\solipsis\services\profile\gui\OthersPanel.py"
  File "dist\solipsis\services\profile\gui\gui-filter.wxg"
  File "dist\solipsis\services\profile\gui\filter.py"
  File "dist\solipsis\services\profile\gui\gui-editor.wxg"
  File "dist\solipsis\services\profile\gui\editor.py"
  File "dist\solipsis\services\profile\gui\DownloadDialog.py"
  SetOutPath "$INSTDIR\solipsis\services\profile\images"
  File "dist\solipsis\services\profile\images\bulb.gif"
  File "dist\solipsis\services\profile\images\icon.gif"
  File "dist\solipsis\services\profile\images\add.gif"
  File "dist\solipsis\services\profile\images\tore.gif"
  File "dist\solipsis\services\profile\images\edit_file.gif"
  File "dist\solipsis\services\profile\images\add_file.gif"
  File "dist\solipsis\services\profile\images\profile_male.gif"
  File "dist\solipsis\services\profile\images\download_complete.gif"
  File "dist\solipsis\services\profile\images\delete_file.gif"
  File "dist\solipsis\services\profile\images\comment.gif"
  File "dist\solipsis\services\profile\images\down_file.gif"
  File "dist\solipsis\services\profile\images\bulb3.gif"
  File "dist\solipsis\services\profile\images\add_file.jpeg"
  File "dist\solipsis\services\profile\images\profile_female.gif"
  File "dist\solipsis\services\profile\images\bulb_off.gif"
  File "dist\solipsis\services\profile\images\browse.jpeg"
  File "dist\solipsis\services\profile\images\question_mark.gif"
  File "dist\solipsis\services\profile\images\__init__.py"
  File "dist\solipsis\services\profile\images\del_file.jpeg"
  File "dist\solipsis\services\profile\images\loupe.gif"
  SetOutPath "$INSTDIR\solipsis\services\profile\po"
  File "dist\solipsis\services\profile\po\messages.pot"
  SetOutPath "$INSTDIR\solipsis\services\profile\po\fr\LC_MESSAGES"
  File "dist\solipsis\services\profile\po\fr\LC_MESSAGES\solipsis_profile.po"
  SetOutPath "$INSTDIR\solipsis\services\profile\tests"
  File "dist\solipsis\services\profile\tests\runtests.py"
  File "dist\solipsis\services\profile\tests\unittest_data.py"
  File "dist\solipsis\services\profile\tests\unittest_network.py"
  File "dist\solipsis\services\profile\tests\unittest_file_document.py"
  File "dist\solipsis\services\profile\tests\unittest_document.py"
  File "dist\solipsis\services\profile\tests\unittest_html_view.py"
  File "dist\solipsis\services\profile\tests\unittest_plugin.py"
  File "dist\solipsis\services\profile\tests\unittest_prefs.py"
  File "dist\solipsis\services\profile\tests\__init__.py"
  File "dist\solipsis\services\profile\tests\unittest_facade.py"
  File "dist\solipsis\services\profile\tests\unittest_filter_document.py"
  File "dist\solipsis\services\profile\tests\unittest_profiles.py"
  SetOutPath "$INSTDIR\solipsis\services\profile\tests\data"
  File "dist\solipsis\services\profile\tests\data\date.txt"
  SetOutPath "$INSTDIR\solipsis\services\profile\tests\data\profiles"
  File "dist\solipsis\services\profile\tests\data\profiles\demi.prf"
  File "dist\solipsis\services\profile\tests\data\profiles\test.prf"
  File "dist\solipsis\services\profile\tests\data\profiles\atao.prf"
  File "dist\solipsis\services\profile\tests\data\profiles\demi_010.blog"
  File "dist\solipsis\services\profile\tests\data\profiles\bruce.blog"
  File "dist\solipsis\services\profile\tests\data\profiles\bruce.prf"
  SetOutPath "$INSTDIR\solipsis\services\profile\tests\data\subdir1"
  File "dist\solipsis\services\profile\tests\data\subdir1\TOtO.txt"
  File "dist\solipsis\services\profile\tests\data\subdir1\date.doc"
  SetOutPath "$INSTDIR\solipsis\services\profile\tests\data\subdir1\subsubdir"
  File "dist\solipsis\services\profile\tests\data\subdir1\subsubdir\default.solipsis"
  File "dist\solipsis\services\profile\tests\data\subdir1\subsubdir\dummy.txt"
  SetOutPath "$INSTDIR\avatars"
  File "dist\avatars\ant.gif"
  File "dist\avatars\seal.gif"
  File "dist\avatars\usb.gif"
  File "dist\avatars\chat.jpg"
  File "dist\avatars\bee.gif"
  File "dist\avatars\oeil.jpg"
  File "dist\avatars\ours.jpg"
  File "dist\avatars\coccinelle.jpg"
  File "dist\avatars\scorpion-md-v0.1.gif"
  File "dist\avatars\bug_02.gif"
  File "dist\avatars\ch_teau-fort_01.gif"
  File "dist\avatars\rhythmbox.gif"
  File "dist\avatars\puffin-md.gif"
  File "dist\avatars\spider.gif"
  File "dist\avatars\insecte2.jpg"
  File "dist\avatars\beagle_copper.gif"
  File "dist\avatars\monitor.gif"
  File "dist\avatars\ecureuil.jpg"
  File "dist\avatars\home10.gif"
  File "dist\avatars\papillon.jpg"
  File "dist\avatars\beagle.jpg"
  File "dist\avatars\dolphin.gif"
  File "dist\avatars\mouette.jpg"
  File "dist\avatars\oiseau.jpg"
  File "dist\avatars\CREDITS.txt"
  File "dist\avatars\home1.gif"
  File "dist\avatars\seahorse.gif"
  File "dist\avatars\toyota_land_cruiser.gif"
  File "dist\avatars\jouet.jpg"
  File "dist\avatars\oie_egypte.jpg"
  File "dist\avatars\insecte.jpg"
  SetOutPath "$INSTDIR\log"
  File "dist\log\solipsis.log"
  SetOutPath "$INSTDIR\state"
  File "dist\state\url_jump.port"
  File "dist\state\config.bin"
  SetOutPath "$INSTDIR\resources"
  File "dist\resources\navigator.xrc"
  SetOutPath "$INSTDIR\po"
  File "dist\po\messages.pot"
  SetOutPath "$INSTDIR\po\de\LC_MESSAGES"
  File "dist\po\de\LC_MESSAGES\solipsis.mo"
  File "dist\po\de\LC_MESSAGES\solipsis.po"
  SetOutPath "$INSTDIR\po\fr\LC_MESSAGES"
  File "dist\po\fr\LC_MESSAGES\solipsis.mo"
  File "dist\po\fr\LC_MESSAGES\solipsis.po"
  SetOutPath "$INSTDIR\po\ja\LC_MESSAGES"
  File "dist\po\ja\LC_MESSAGES\solipsis.mo"
  File "dist\po\ja\LC_MESSAGES\solipsis.po"
  SetOutPath "$INSTDIR\po\sl\LC_MESSAGES"
  File "dist\po\sl\LC_MESSAGES\solipsis.mo"
  File "dist\po\sl\LC_MESSAGES\solipsis.po"
  SetOutPath "$INSTDIR"
  File "dist\python24.dll"
  File "dist\twistednode.exe"
  File "dist\navigator.exe"
  File "dist\navigator.exe.log"

; Shortcuts
  !insertmacro MUI_STARTMENU_WRITE_BEGIN Application
  CreateShortCut "$DESKTOP\Node.lnk" "$INSTDIR\twistednode.exe"
  CreateDirectory "$SMPROGRAMS\$ICONS_GROUP"
  CreateShortCut "$SMPROGRAMS\$ICONS_GROUP\Node.lnk" "$INSTDIR\twistednode.exe"
  CreateShortCut "$SMPROGRAMS\$ICONS_GROUP\Solipsis.lnk" "$INSTDIR\navigator.exe"
  CreateShortCut "$DESKTOP\Solipsis.lnk" "$INSTDIR\navigator.exe"
  !insertmacro MUI_STARTMENU_WRITE_END
SectionEnd

Section -AdditionalIcons
  !insertmacro MUI_STARTMENU_WRITE_BEGIN Application
  WriteIniStr "$INSTDIR\${PRODUCT_NAME}.url" "InternetShortcut" "URL" "${PRODUCT_WEB_SITE}"
  CreateShortCut "$SMPROGRAMS\$ICONS_GROUP\Website.lnk" "$INSTDIR\${PRODUCT_NAME}.url"
  CreateShortCut "$SMPROGRAMS\$ICONS_GROUP\Uninstall.lnk" "$INSTDIR\uninst.exe"
  !insertmacro MUI_STARTMENU_WRITE_END
SectionEnd

Section -Post
  WriteUninstaller "$INSTDIR\uninst.exe"
  WriteRegStr HKLM "${PRODUCT_DIR_REGKEY}" "" "$INSTDIR\w9xpopen.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayName" "$(^Name)"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "UninstallString" "$INSTDIR\uninst.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayIcon" "$INSTDIR\w9xpopen.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayVersion" "${PRODUCT_VERSION}"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "URLInfoAbout" "${PRODUCT_WEB_SITE}"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "Publisher" "${PRODUCT_PUBLISHER}"
SectionEnd


Function un.onUninstSuccess
  HideWindow
  MessageBox MB_ICONINFORMATION|MB_OK "$(^Name) a �t� d�sinstall� avec succ�s de votre ordinateur."
FunctionEnd

Function un.onInit
!insertmacro MUI_UNGETLANGUAGE
  MessageBox MB_ICONQUESTION|MB_YESNO|MB_DEFBUTTON2 "�tes-vous certains de vouloir d�sinstaller totalement $(^Name) et tous ses composants ?" IDYES +2
  Abort
FunctionEnd

Section Uninstall
  !insertmacro MUI_STARTMENU_GETFOLDER "Application" $ICONS_GROUP
  Delete "$INSTDIR\${PRODUCT_NAME}.url"
  Delete "$INSTDIR\uninst.exe"
  Delete "$INSTDIR\navigator.exe.log"
  Delete "$INSTDIR\navigator.exe"
  Delete "$INSTDIR\twistednode.exe"
  Delete "$INSTDIR\python24.dll"
  Delete "$INSTDIR\po\sl\LC_MESSAGES\solipsis.po"
  Delete "$INSTDIR\po\sl\LC_MESSAGES\solipsis.mo"
  Delete "$INSTDIR\po\ja\LC_MESSAGES\solipsis.po"
  Delete "$INSTDIR\po\ja\LC_MESSAGES\solipsis.mo"
  Delete "$INSTDIR\po\fr\LC_MESSAGES\solipsis.po"
  Delete "$INSTDIR\po\fr\LC_MESSAGES\solipsis.mo"
  Delete "$INSTDIR\po\de\LC_MESSAGES\solipsis.po"
  Delete "$INSTDIR\po\de\LC_MESSAGES\solipsis.mo"
  Delete "$INSTDIR\po\messages.pot"
  Delete "$INSTDIR\resources\navigator.xrc"
  Delete "$INSTDIR\state\config.bin"
  Delete "$INSTDIR\state\url_jump.port"
  Delete "$INSTDIR\log\solipsis.log"
  Delete "$INSTDIR\avatars\insecte.jpg"
  Delete "$INSTDIR\avatars\oie_egypte.jpg"
  Delete "$INSTDIR\avatars\jouet.jpg"
  Delete "$INSTDIR\avatars\toyota_land_cruiser.gif"
  Delete "$INSTDIR\avatars\seahorse.gif"
  Delete "$INSTDIR\avatars\home1.gif"
  Delete "$INSTDIR\avatars\CREDITS.txt"
  Delete "$INSTDIR\avatars\oiseau.jpg"
  Delete "$INSTDIR\avatars\mouette.jpg"
  Delete "$INSTDIR\avatars\dolphin.gif"
  Delete "$INSTDIR\avatars\beagle.jpg"
  Delete "$INSTDIR\avatars\papillon.jpg"
  Delete "$INSTDIR\avatars\home10.gif"
  Delete "$INSTDIR\avatars\ecureuil.jpg"
  Delete "$INSTDIR\avatars\monitor.gif"
  Delete "$INSTDIR\avatars\beagle_copper.gif"
  Delete "$INSTDIR\avatars\insecte2.jpg"
  Delete "$INSTDIR\avatars\spider.gif"
  Delete "$INSTDIR\avatars\puffin-md.gif"
  Delete "$INSTDIR\avatars\rhythmbox.gif"
  Delete "$INSTDIR\avatars\ch_teau-fort_01.gif"
  Delete "$INSTDIR\avatars\bug_02.gif"
  Delete "$INSTDIR\avatars\scorpion-md-v0.1.gif"
  Delete "$INSTDIR\avatars\coccinelle.jpg"
  Delete "$INSTDIR\avatars\ours.jpg"
  Delete "$INSTDIR\avatars\oeil.jpg"
  Delete "$INSTDIR\avatars\bee.gif"
  Delete "$INSTDIR\avatars\chat.jpg"
  Delete "$INSTDIR\avatars\usb.gif"
  Delete "$INSTDIR\avatars\seal.gif"
  Delete "$INSTDIR\avatars\ant.gif"
  Delete "$INSTDIR\solipsis\services\profile\tests\data\subdir1\subsubdir\dummy.txt"
  Delete "$INSTDIR\solipsis\services\profile\tests\data\subdir1\subsubdir\default.solipsis"
  Delete "$INSTDIR\solipsis\services\profile\tests\data\subdir1\date.doc"
  Delete "$INSTDIR\solipsis\services\profile\tests\data\subdir1\TOtO.txt"
  Delete "$INSTDIR\solipsis\services\profile\tests\data\profiles\bruce.prf"
  Delete "$INSTDIR\solipsis\services\profile\tests\data\profiles\bruce.blog"
  Delete "$INSTDIR\solipsis\services\profile\tests\data\profiles\demi_010.blog"
  Delete "$INSTDIR\solipsis\services\profile\tests\data\profiles\atao.prf"
  Delete "$INSTDIR\solipsis\services\profile\tests\data\profiles\test.prf"
  Delete "$INSTDIR\solipsis\services\profile\tests\data\profiles\demi.prf"
  Delete "$INSTDIR\solipsis\services\profile\tests\data\date.txt"
  Delete "$INSTDIR\solipsis\services\profile\tests\unittest_profiles.py"
  Delete "$INSTDIR\solipsis\services\profile\tests\unittest_filter_document.py"
  Delete "$INSTDIR\solipsis\services\profile\tests\unittest_facade.py"
  Delete "$INSTDIR\solipsis\services\profile\tests\__init__.py"
  Delete "$INSTDIR\solipsis\services\profile\tests\unittest_prefs.py"
  Delete "$INSTDIR\solipsis\services\profile\tests\unittest_plugin.py"
  Delete "$INSTDIR\solipsis\services\profile\tests\unittest_html_view.py"
  Delete "$INSTDIR\solipsis\services\profile\tests\unittest_document.py"
  Delete "$INSTDIR\solipsis\services\profile\tests\unittest_file_document.py"
  Delete "$INSTDIR\solipsis\services\profile\tests\unittest_network.py"
  Delete "$INSTDIR\solipsis\services\profile\tests\unittest_data.py"
  Delete "$INSTDIR\solipsis\services\profile\tests\runtests.py"
  Delete "$INSTDIR\solipsis\services\profile\po\fr\LC_MESSAGES\solipsis_profile.po"
  Delete "$INSTDIR\solipsis\services\profile\po\messages.pot"
  Delete "$INSTDIR\solipsis\services\profile\images\loupe.gif"
  Delete "$INSTDIR\solipsis\services\profile\images\del_file.jpeg"
  Delete "$INSTDIR\solipsis\services\profile\images\__init__.py"
  Delete "$INSTDIR\solipsis\services\profile\images\question_mark.gif"
  Delete "$INSTDIR\solipsis\services\profile\images\browse.jpeg"
  Delete "$INSTDIR\solipsis\services\profile\images\bulb_off.gif"
  Delete "$INSTDIR\solipsis\services\profile\images\profile_female.gif"
  Delete "$INSTDIR\solipsis\services\profile\images\add_file.jpeg"
  Delete "$INSTDIR\solipsis\services\profile\images\bulb3.gif"
  Delete "$INSTDIR\solipsis\services\profile\images\down_file.gif"
  Delete "$INSTDIR\solipsis\services\profile\images\comment.gif"
  Delete "$INSTDIR\solipsis\services\profile\images\delete_file.gif"
  Delete "$INSTDIR\solipsis\services\profile\images\download_complete.gif"
  Delete "$INSTDIR\solipsis\services\profile\images\profile_male.gif"
  Delete "$INSTDIR\solipsis\services\profile\images\add_file.gif"
  Delete "$INSTDIR\solipsis\services\profile\images\edit_file.gif"
  Delete "$INSTDIR\solipsis\services\profile\images\tore.gif"
  Delete "$INSTDIR\solipsis\services\profile\images\add.gif"
  Delete "$INSTDIR\solipsis\services\profile\images\icon.gif"
  Delete "$INSTDIR\solipsis\services\profile\images\bulb.gif"
  Delete "$INSTDIR\solipsis\services\profile\gui\DownloadDialog.py"
  Delete "$INSTDIR\solipsis\services\profile\gui\editor.py"
  Delete "$INSTDIR\solipsis\services\profile\gui\gui-editor.wxg"
  Delete "$INSTDIR\solipsis\services\profile\gui\filter.py"
  Delete "$INSTDIR\solipsis\services\profile\gui\gui-filter.wxg"
  Delete "$INSTDIR\solipsis\services\profile\gui\OthersPanel.py"
  Delete "$INSTDIR\solipsis\services\profile\gui\ProfileDialog.py"
  Delete "$INSTDIR\solipsis\services\profile\gui\ViewerFrame.py"
  Delete "$INSTDIR\solipsis\services\profile\gui\MatchPanel.py"
  Delete "$INSTDIR\solipsis\services\profile\gui\PersonalFilterPanel.py"
  Delete "$INSTDIR\solipsis\services\profile\gui\MatchFrame.py"
  Delete "$INSTDIR\solipsis\services\profile\gui\FileFilterPanel.py"
  Delete "$INSTDIR\solipsis\services\profile\gui\BlogDialog.py"
  Delete "$INSTDIR\solipsis\services\profile\gui\BlogPanel.py"
  Delete "$INSTDIR\solipsis\services\profile\gui\PersonalPanel.py"
  Delete "$INSTDIR\solipsis\services\profile\gui\viewer.py"
  Delete "$INSTDIR\solipsis\services\profile\gui\EditorFrame.py"
  Delete "$INSTDIR\solipsis\services\profile\gui\PreviewPanel.py"
  Delete "$INSTDIR\solipsis\services\profile\gui\gui-viewer.wxg"
  Delete "$INSTDIR\solipsis\services\profile\gui\FilterFrame.py"
  Delete "$INSTDIR\solipsis\services\profile\gui\__init__.py"
  Delete "$INSTDIR\solipsis\services\profile\gui\FileDialog.py"
  Delete "$INSTDIR\solipsis\services\profile\gui\FilePanel.py"
  Delete "$INSTDIR\solipsis\services\profile\gui\AboutDialog.py"
  Delete "$INSTDIR\solipsis\services\profile\gui\CustomPanel.py"
  Delete "$INSTDIR\solipsis\services\profile\gui\profiling.py"
  Delete "$INSTDIR\solipsis\services\profile\gui\gui.wxg"
  Delete "$INSTDIR\solipsis\services\profile\facade.py"
  Delete "$INSTDIR\solipsis\services\profile\cache_document.py"
  Delete "$INSTDIR\solipsis\services\profile\__init__.py"
  Delete "$INSTDIR\solipsis\services\profile\plugin.py"
  Delete "$INSTDIR\solipsis\services\profile\preview.html"
  Delete "$INSTDIR\solipsis\services\profile\network.py"
  Delete "$INSTDIR\solipsis\services\profile\regex.html"
  Delete "$INSTDIR\solipsis\services\profile\filter_document.py"
  Delete "$INSTDIR\solipsis\services\profile\preview.css"
  Delete "$INSTDIR\solipsis\services\profile\document.py"
  Delete "$INSTDIR\solipsis\services\profile\file_document.py"
  Delete "$INSTDIR\solipsis\services\profile\pathutils.py"
  Delete "$INSTDIR\solipsis\services\profile\simple_facade.py"
  Delete "$INSTDIR\solipsis\services\profile\prefs.py"
  Delete "$INSTDIR\solipsis\services\profile\view.py"
  Delete "$INSTDIR\solipsis\services\profile\data.py"
  Delete "$INSTDIR\solipsis\services\chat\po\sl\LC_MESSAGES\solipsis_chat.mo"
  Delete "$INSTDIR\solipsis\services\chat\po\sl\LC_MESSAGES\solipsis_chat.po"
  Delete "$INSTDIR\solipsis\services\chat\po\ja\LC_MESSAGES\solipsis_chat.mo"
  Delete "$INSTDIR\solipsis\services\chat\po\ja\LC_MESSAGES\solipsis_chat.po"
  Delete "$INSTDIR\solipsis\services\chat\po\fr\LC_MESSAGES\solipsis_chat.mo"
  Delete "$INSTDIR\solipsis\services\chat\po\fr\LC_MESSAGES\solipsis_chat.po"
  Delete "$INSTDIR\solipsis\services\chat\po\de\LC_MESSAGES\solipsis_chat.mo"
  Delete "$INSTDIR\solipsis\services\chat\po\de\LC_MESSAGES\solipsis_chat.po"
  Delete "$INSTDIR\solipsis\services\chat\po\messages.pot"
  Delete "$INSTDIR\solipsis\services\chat\__init__.py"
  Delete "$INSTDIR\solipsis\services\chat\plugin.py"
  Delete "$INSTDIR\solipsis\services\chat\gui.xrc"
  Delete "$INSTDIR\solipsis\services\chat\gui.py"
  Delete "$INSTDIR\solipsis\services\avatar\po\sl\LC_MESSAGES\solipsis_avatar.mo"
  Delete "$INSTDIR\solipsis\services\avatar\po\sl\LC_MESSAGES\solipsis_avatar.po"
  Delete "$INSTDIR\solipsis\services\avatar\po\ja\LC_MESSAGES\solipsis_avatar.mo"
  Delete "$INSTDIR\solipsis\services\avatar\po\ja\LC_MESSAGES\solipsis_avatar.po"
  Delete "$INSTDIR\solipsis\services\avatar\po\fr\LC_MESSAGES\solipsis_avatar.mo"
  Delete "$INSTDIR\solipsis\services\avatar\po\fr\LC_MESSAGES\solipsis_avatar.po"
  Delete "$INSTDIR\solipsis\services\avatar\po\de\LC_MESSAGES\solipsis_avatar.mo"
  Delete "$INSTDIR\solipsis\services\avatar\po\de\LC_MESSAGES\solipsis_avatar.po"
  Delete "$INSTDIR\solipsis\services\avatar\po\messages.pot"
  Delete "$INSTDIR\solipsis\services\avatar\repository.py"
  Delete "$INSTDIR\solipsis\services\avatar\__init__.py"
  Delete "$INSTDIR\solipsis\services\avatar\plugin.py"
  Delete "$INSTDIR\solipsis\services\avatar\network.py"
  Delete "$INSTDIR\solipsis\services\avatar\gui.py"
  Delete "$INSTDIR\solipsis\services\collector.py"
  Delete "$INSTDIR\solipsis\services\wxcollector.py"
  Delete "$INSTDIR\solipsis\services\__init__.py"
  Delete "$INSTDIR\solipsis\services\plugin.py"
  Delete "$INSTDIR\conf\solipsis.conf"
  Delete "$INSTDIR\msvcr71.dll"
  Delete "$INSTDIR\img\tmp_small_transfer_red.png"
  Delete "$INSTDIR\img\avat_orange.png"
  Delete "$INSTDIR\img\b_filter_a.png"
  Delete "$INSTDIR\img\transfer_blue.png"
  Delete "$INSTDIR\img\solipsis.ico"
  Delete "$INSTDIR\img\avat_white.png"
  Delete "$INSTDIR\img\im_2D.png"
  Delete "$INSTDIR\img\im_solipsis.png"
  Delete "$INSTDIR\img\picto_avat.png"
  Delete "$INSTDIR\img\top_banner.png"
  Delete "$INSTDIR\img\chat_blue.png"
  Delete "$INSTDIR\img\avat_small_02.png"
  Delete "$INSTDIR\img\send_red.png"
  Delete "$INSTDIR\img\avat_small_01.png"
  Delete "$INSTDIR\img\avat_grey.png"
  Delete "$INSTDIR\img\transfer_red.png"
  Delete "$INSTDIR\img\small_chat_blue.png"
  Delete "$INSTDIR\img\picto_file.png"
  Delete "$INSTDIR\img\picto_chat.png"
  Delete "$INSTDIR\img\icon_solipsis.png"
  Delete "$INSTDIR\img\avat_gh.png"
  Delete "$INSTDIR\img\chat_red.png"
  Delete "$INSTDIR\img\small_transfer_red.png"
  Delete "$INSTDIR\img\im_chat.png"
  Delete "$INSTDIR\img\logo2.gif"
  Delete "$INSTDIR\img\b_filter_n.png"
  Delete "$INSTDIR\img\send_blue.png"
  Delete "$INSTDIR\img\tmp_small_chat_blue.png"
  Delete "$INSTDIR\img\mask.png"
  Delete "$INSTDIR\img\logo.gif"
  Delete "$INSTDIR\README.txt"
  Delete "$INSTDIR\LICENSE"
  Delete "$INSTDIR\entities.met"
  Delete "$INSTDIR\w9xpopen.exe"
  Delete "$INSTDIR\library.zip"
  Delete "$INSTDIR\_zope_interface_coptimizations.pyd"
  Delete "$INSTDIR\wxmsw26uh_vc.dll"
  Delete "$INSTDIR\wxmsw26uh_stc_vc.dll"
  Delete "$INSTDIR\wxmsw26uh_gl_vc.dll"
  Delete "$INSTDIR\wxmsw26uh_gizmos_xrc_vc.dll"
  Delete "$INSTDIR\wxmsw26uh_gizmos_vc.dll"
  Delete "$INSTDIR\wxmsw26uh_animate_vc.dll"
  Delete "$INSTDIR\_xrc.pyd"
  Delete "$INSTDIR\_wizard.pyd"
  Delete "$INSTDIR\_windows_.pyd"
  Delete "$INSTDIR\_webkit.pyd"
  Delete "$INSTDIR\_stc.pyd"
  Delete "$INSTDIR\_misc_.pyd"
  Delete "$INSTDIR\_media.pyd"
  Delete "$INSTDIR\_html.pyd"
  Delete "$INSTDIR\_grid.pyd"
  Delete "$INSTDIR\_glcanvas.pyd"
  Delete "$INSTDIR\_gizmos.pyd"
  Delete "$INSTDIR\_gdi_.pyd"
  Delete "$INSTDIR\_core_.pyd"
  Delete "$INSTDIR\_controls_.pyd"
  Delete "$INSTDIR\_calendar.pyd"
  Delete "$INSTDIR\_animate.pyd"
  Delete "$INSTDIR\_activex.pyd"
  Delete "$INSTDIR\cBanana.pyd"
  Delete "$INSTDIR\_c_urlarg.pyd"
  Delete "$INSTDIR\_iocp.pyd"
  Delete "$INSTDIR\_imagingtk.pyd"
  Delete "$INSTDIR\_imagingft.pyd"
  Delete "$INSTDIR\_imaging.pyd"
  Delete "$INSTDIR\zlib.pyd"
  Delete "$INSTDIR\unicodedata.pyd"
  Delete "$INSTDIR\select.pyd"
  Delete "$INSTDIR\pyexpat.pyd"
  Delete "$INSTDIR\bz2.pyd"
  Delete "$INSTDIR\_ssl.pyd"
  Delete "$INSTDIR\_socket.pyd"

  Delete "$SMPROGRAMS\$ICONS_GROUP\Uninstall.lnk"
  Delete "$SMPROGRAMS\$ICONS_GROUP\Website.lnk"
  Delete "$DESKTOP\Solipsis.lnk"
  Delete "$SMPROGRAMS\$ICONS_GROUP\Solipsis.lnk"
  Delete "$SMPROGRAMS\$ICONS_GROUP\Node.lnk"
  Delete "$DESKTOP\Node.lnk"

  RMDir "$SMPROGRAMS\$ICONS_GROUP"
  RMDir "$INSTDIR\state"
  RMDir "$INSTDIR\solipsis\services\profile\tests\data\subdir1\subsubdir"
  RMDir "$INSTDIR\solipsis\services\profile\tests\data\subdir1"
  RMDir "$INSTDIR\solipsis\services\profile\tests\data\profiles"
  RMDir "$INSTDIR\solipsis\services\profile\tests\data"
  RMDir "$INSTDIR\solipsis\services\profile\tests"
  RMDir "$INSTDIR\solipsis\services\profile\po\fr\LC_MESSAGES"
  RMDir "$INSTDIR\solipsis\services\profile\po"
  RMDir "$INSTDIR\solipsis\services\profile\images"
  RMDir "$INSTDIR\solipsis\services\profile\gui"
  RMDir "$INSTDIR\solipsis\services\profile"
  RMDir "$INSTDIR\solipsis\services\chat\po\sl\LC_MESSAGES"
  RMDir "$INSTDIR\solipsis\services\chat\po\ja\LC_MESSAGES"
  RMDir "$INSTDIR\solipsis\services\chat\po\fr\LC_MESSAGES"
  RMDir "$INSTDIR\solipsis\services\chat\po\de\LC_MESSAGES"
  RMDir "$INSTDIR\solipsis\services\chat\po"
  RMDir "$INSTDIR\solipsis\services\chat"
  RMDir "$INSTDIR\solipsis\services\avatar\po\sl\LC_MESSAGES"
  RMDir "$INSTDIR\solipsis\services\avatar\po\ja\LC_MESSAGES"
  RMDir "$INSTDIR\solipsis\services\avatar\po\fr\LC_MESSAGES"
  RMDir "$INSTDIR\solipsis\services\avatar\po\de\LC_MESSAGES"
  RMDir "$INSTDIR\solipsis\services\avatar\po"
  RMDir "$INSTDIR\solipsis\services\avatar"
  RMDir "$INSTDIR\solipsis\services"
  RMDir "$INSTDIR\resources"
  RMDir "$INSTDIR\po\sl\LC_MESSAGES"
  RMDir "$INSTDIR\po\ja\LC_MESSAGES"
  RMDir "$INSTDIR\po\fr\LC_MESSAGES"
  RMDir "$INSTDIR\po\de\LC_MESSAGES"
  RMDir "$INSTDIR\po"
  RMDir "$INSTDIR\log"
  RMDir "$INSTDIR\img"
  RMDir "$INSTDIR\conf"
  RMDir "$INSTDIR\avatars"
  RMDir "$INSTDIR"

  DeleteRegKey ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}"
  DeleteRegKey HKLM "${PRODUCT_DIR_REGKEY}"
  SetAutoClose true
SectionEnd