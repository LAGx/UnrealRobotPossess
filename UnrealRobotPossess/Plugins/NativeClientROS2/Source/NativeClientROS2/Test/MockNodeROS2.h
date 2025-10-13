// Copyright Yurii (Kvark) Maruda. Free open sample.

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MockNodeROS2.generated.h"

UCLASS()
class NATIVECLIENTROS2_API AMockNodeROS2 : public AActor
{
	GENERATED_BODY()

public:
	AMockNodeROS2();

protected:
	virtual void BeginPlay() override;
	virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

public:
	virtual void Tick(float DeltaTime) override;

private:
	void StartRos();
	void StopRos();

	void* internalData = nullptr;
};
