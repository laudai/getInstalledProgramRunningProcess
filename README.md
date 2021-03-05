## getInstalledProgramRunningProcess

Author : _LauDai_

# English Version

## Project Description

A project that get Windows User `Installed Program`,`Running Process` via **Windows WMI**, **Python.Subprocess** ,**Python.Socket**.

Default Disabling show `"svchost.exe", "firefox.exe", "chrome.exe"` in Running Process.

### Roadmap

- json
- ip boardcast
- thread or process or asyncio to writeAllDataToLocal

# 中文版

## 專案描述

一個透過 **Windows WMI**, **Python.Subprocess**, **Python.Socket**取得 Windows 使用者`已安裝程式`、`正在執行程式`的專案。
在正在執行程式的呈現中，預設不會顯示`"svchost.exe", "firefox.exe", "chrome.exe"`

### 需要修正項目

1. 邏輯修正:
   1. 目前 send 3,5 都會將所有資料先取得再寫入本地，但實際上應該取得要寫入資料後才寫入
   2. 修正前為 3 本地寫入兩種資料，取得 running_process 資料，5 本地寫入兩種資料，取得 installed_program 資料
   3. 修正後應該為 3 取得資料後，寫入該種資料至本地；5 取得資料後，寫入該種資料至本地。
2. 測試程式如何正確使用 default 值送出資料。
