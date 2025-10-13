// Copyright Yurii (Kvark) Maruda. Free open sample.


#include "MockNodeROS2.h"

#include "ROS2API.h"

using std::shared_ptr;
using std::unique_ptr;

struct InternalData
{
  shared_ptr<rclcpp::executors::SingleThreadedExecutor> Executor;
  shared_ptr<rclcpp::Node> Node;
  unique_ptr<std::thread> SpinThread;

  static InternalData* Convert(void* data)
  {
    return reinterpret_cast<InternalData*>(data);
  }
};


AMockNodeROS2::AMockNodeROS2()
{
	PrimaryActorTick.bCanEverTick = true;
}

void AMockNodeROS2::Tick(float DeltaTime)
{
  Super::Tick(DeltaTime);

  InternalData* data = InternalData::Convert(internalData);

  if (!internalData)
  {
    return;
  }

  if (!data->Node)
  {
    return;
  }

  auto names = data->Node->get_node_graph_interface()->get_node_names();
  auto pairs = data->Node->get_node_graph_interface()->get_node_names_and_namespaces();

  FString List;
  for (auto& p : pairs)
  {
    const FString N = UTF8_TO_TCHAR(p.first.c_str());
    const FString NS = UTF8_TO_TCHAR(p.second.c_str());
    List += FString::Printf(TEXT("  - %s@%s\n"), *N, *NS);
  }

  UE_LOG(LogTemp, Log, TEXT("[ROS2] Discovered %i nodes:\n%s"), (int)names.size(), *List);
}

void AMockNodeROS2::BeginPlay()
{
  Super::BeginPlay();
  StartRos();

  InternalData* data = InternalData::Convert(internalData);

  if (!data)
  {
    return;
  }

  const char* RmwId = rmw_get_implementation_identifier();
  const char* DomainEnv = nullptr; size_t Len = 0;
  rcutils_get_env("ROS_DOMAIN_ID", &DomainEnv);
  UE_LOG(LogTemp, Log, TEXT("[ROS2] RMW: %s, ROS_DOMAIN_ID: %s"),
         ANSI_TO_TCHAR(RmwId ? RmwId : "null"),
         ANSI_TO_TCHAR(DomainEnv && *DomainEnv ? DomainEnv : "unset"));
}

void AMockNodeROS2::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
  StopRos();
  Super::EndPlay(EndPlayReason);
}

void AMockNodeROS2::StartRos()
{
  if (internalData)
  {
    return;
  }

  internalData = new InternalData;
  InternalData* data = InternalData::Convert(internalData);

  int argc = 0; char** argv = nullptr;
  rclcpp::InitOptions init_opts;
  init_opts.auto_initialize_logging(false);
  init_opts.set_domain_id(44);

  auto ctx = std::make_shared<rclcpp::Context>();
  ctx->init(argc, argv, init_opts);

  rclcpp::ExecutorOptions exec_opts;
  exec_opts.context = ctx;
  data->Executor = std::make_shared<rclcpp::executors::SingleThreadedExecutor>(exec_opts);

  rclcpp::NodeOptions node_opts;
  node_opts.context(ctx);
  data->Node = std::make_shared<rclcpp::Node>("ue_graph_probe", node_opts);
  data->Executor->add_node(data->Node);

  data->SpinThread = std::make_unique<std::thread>([Exec = data->Executor]()
  {
    try { Exec->spin(); } catch(...) {}
  });
}

void AMockNodeROS2::StopRos()
{
  InternalData* data = InternalData::Convert(internalData);

  if (!data)
  {
    return;
  }

  if (data->Executor)
  {
    data->Executor->cancel();
  }

  if (data->SpinThread && data->SpinThread->joinable())
  {
    data->SpinThread->join();
  }
  data->Executor.reset();
  data->Node.reset();
  if (rclcpp::ok())
  {
    rclcpp::shutdown();
  }

  delete data;
  internalData = nullptr;
}
