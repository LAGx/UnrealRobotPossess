//Copyright Yurii (Kvark) Maruda. Free open sample.

#include "NativeClientROS2.h"

#define LOCTEXT_NAMESPACE "FNativeClientROS2Module"

#if PLATFORM_WINDOWS

#define WIN32_LEAN_AND_MEAN 1
#include <windows.h>

static void LogLastError(const TCHAR* What, const FString& Path)
{
    DWORD code = ::GetLastError();
    wchar_t* msg = nullptr;
    ::FormatMessageW(FORMAT_MESSAGE_ALLOCATE_BUFFER|FORMAT_MESSAGE_FROM_SYSTEM|FORMAT_MESSAGE_IGNORE_INSERTS,
                     nullptr, code, 0, (LPWSTR)&msg, 0, nullptr);

    UE_LOG(LogTemp, Error, TEXT("[FNativeClientROS2Module ERROR] %s: %s (GetLastError=%lu)"), What, *Path, code);
    if (msg) { UE_LOG(LogTemp, Error, TEXT("%s"), msg); ::LocalFree(msg); }
}

static HMODULE LoadDllEx(const FString& FullPath)
{
    HMODULE h = ::LoadLibraryExW(*FullPath, nullptr,
        LOAD_LIBRARY_SEARCH_DLL_LOAD_DIR | LOAD_LIBRARY_SEARCH_USER_DIRS | LOAD_LIBRARY_SEARCH_SYSTEM32);
    if (!h)
    {
        LogLastError(TEXT("[ROS2] LoadLibraryEx failed"), FullPath);
    }
    return h;
}

static TArray<HMODULE> GRos2Dlls;

void FNativeClientROS2Module::StartupModule()
{
    const FString Bin = TEXT("C:/dev/ros2_iron/bin");
    ::AddDllDirectory(*Bin);

    ::SetEnvironmentVariableW(L"RMW_IMPLEMENTATION", L"rmw_cyclonedds_cpp");
    _wputenv_s(L"RMW_IMPLEMENTATION", L"rmw_cyclonedds_cpp");

    TArray<FString> Need;
    IFileManager::Get().FindFiles(Need, *(Bin / TEXT("*.dll")), /*Files*/true, /*Dirs*/false);

    bool bCycloneOnly = true;
    bool bPreloadRcl = false;
    bool bPreloadLogger = false;

    // 2) фильтрация
    Need.Sort(); // стабильный порядок
    Need = Need.FilterByPredicate([&](const FString& Name){
      const FString L = Name.ToLower();

      if (bCycloneOnly && (L == TEXT("rmw_fastrtps_cpp.dll") || L == TEXT("fastrtps.dll") || L == TEXT("fastcdr.dll")))
          return false;                      // убираем FastDDS

        if (!bPreloadRcl && (L == TEXT("rcl.dll") || L == TEXT("rclcpp.dll")))
            return false;                      // rcl/rclcpp оставим на delay-load

          if (!bPreloadLogger && (L == TEXT("rcl_logging_spdlog.dll") || L == TEXT("spdlog.dll")))
              return false;                      // логгер можно подложить позже

            return true;
          });
    
    for (FString name : Need)
    {
        const FString full = Bin / name;
        HMODULE h = LoadDllEx(full);
        if (!h)
        {
            UE_LOG(LogTemp, Error, TEXT("[FNativeClientROS2Module] Abort due to missing dependency"));
            return;
        }
        GRos2Dlls.Add(h);
    }
}
#else
void FNativeClientROS2Module::StartupModule()
{
    FPlatformProcess::AddDllDirectory(TEXT("C:/dev/ros2_iron/bin"));
}
#endif

void FNativeClientROS2Module::ShutdownModule()
{
}

#undef LOCTEXT_NAMESPACE

IMPLEMENT_MODULE(FNativeClientROS2Module, NativeClientROS2)