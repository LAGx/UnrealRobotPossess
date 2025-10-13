//Copyright Yurii (Kvark) Maruda. Free open sample.

#pragma once

#include "Modules/ModuleManager.h"

class FNativeClientROS2Module : public IModuleInterface
{
public:

	virtual void StartupModule() override;
	virtual void ShutdownModule() override;
};
