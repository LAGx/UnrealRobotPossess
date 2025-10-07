//Copyright Yurii (Kvark) Maruda. Free open sample.

using UnrealBuildTool;
using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;

public class NativeClientROS2 : ModuleRules
{
	public NativeClientROS2(ReadOnlyTargetRules Target) : base(Target)
	{
		PCHUsage = ModuleRules.PCHUsageMode.UseExplicitOrSharedPCHs;
		Type = ModuleType.CPlusPlus;
		bUseRTTI = true; // (/GR) ROS2 on windows for some reason need it
		bEnableExceptions = true; // ROS2 has API with exceptions, eliminating it in plugin API.
		
		string ROS = @"C:\dev\ros2_iron";
		// PublicIncludePaths.Add(System.IO.Path.Combine(ROS, "include"));
		
		// INCLUDE
		string Inc = System.IO.Path.Combine(ROS, "include");
		
		var includeDirs = new HashSet<string>(new[] { Inc }, System.StringComparer.OrdinalIgnoreCase);
		if (Directory.Exists(Inc))
		{
			foreach (var dir in Directory.EnumerateDirectories(Inc))
			{
				includeDirs.Add(dir);
			}
		}
		
		PrivateIncludePaths.AddRange(includeDirs.ToArray());
		
		string Bin = Path.Combine(ROS, "bin");
		string Lib = Path.Combine(ROS, "lib");


		bool CycloneOnly = true;

		var denyDll = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
		var denyLib = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
		if (CycloneOnly)
		{
			denyDll.UnionWith(new[]{
				"rmw_fastrtps_cpp.dll","fastrtps.dll","fastcdr.dll"
			});
			denyLib.UnionWith(new[]{
				"rmw_fastrtps_cpp.lib","fastrtps.lib","fastcdr.lib"
			});
		}


		var dllNames = new List<string>();
		if (Directory.Exists(Bin))
		{
			foreach (var f in Directory.EnumerateFiles(Bin, "*.dll", SearchOption.TopDirectoryOnly))
			{
				var name = Path.GetFileName(f);
				if (!denyDll.Contains(name))
					dllNames.Add(name);
			}
			
			dllNames = dllNames.Distinct(StringComparer.OrdinalIgnoreCase).ToList();

			
			PublicDelayLoadDLLs.AddRange(dllNames);
		
			foreach (var name in dllNames)
				RuntimeDependencies.Add(Path.Combine(Bin, name));
		}


		if (Directory.Exists(Lib))
		{
			var libPaths = Directory.EnumerateFiles(Lib, "*.lib", SearchOption.TopDirectoryOnly)
				.Where(p => !denyLib.Contains(Path.GetFileName(p)))
				.Distinct(StringComparer.OrdinalIgnoreCase);

			foreach (var p in libPaths)
				PublicAdditionalLibraries.Add(p);
		}
		
		//
		//string Lib = System.IO.Path.Combine(ROS, "lib");
		//PublicAdditionalLibraries.AddRange(new[] {
		//	System.IO.Path.Combine(Lib, "rclcpp.lib"),
		//	//System.IO.Path.Combine(Lib, "rcl.lib"),
		//	System.IO.Path.Combine(Lib, "rcutils.lib"),
		//	//System.IO.Path.Combine(Lib, "rcpputils.lib"),
		//	//System.IO.Path.Combine(Lib, "ament_index_cpp.lib"),
		//	//System.IO.Path.Combine(Lib, "rosidl_runtime_c.lib"),
		//	//System.IO.Path.Combine(Lib, "rosidl_typesupport_cpp.lib"),
		//	
		//	System.IO.Path.Combine(Lib, "rmw_implementation.lib"),
		//	System.IO.Path.Combine(Lib, "rmw_cyclonedds_cpp.lib"),
		//	//// System.IO.Path.Combine(L, "rmw_fastrtps_cpp.lib"),
		//});
		//
		//// msg
		////PublicAdditionalLibraries.AddRange(new[] {
		////	System.IO.Path.Combine(Lib, "builtin_interfaces__rosidl_typesupport_cpp.lib"),
		////	System.IO.Path.Combine(Lib, "std_msgs__rosidl_typesupport_cpp.lib"),
		////	System.IO.Path.Combine(Lib, "geometry_msgs__rosidl_typesupport_cpp.lib"),
		////	// + nav_msgs / sensor_msgs
		////});
		////
		//string B = System.IO.Path.Combine(ROS, "bin");
		//RuntimeDependencies.Add(System.IO.Path.Combine(B, "rclcpp.dll"));
		////RuntimeDependencies.Add(System.IO.Path.Combine(B, "rcl.dll"));
		//RuntimeDependencies.Add(System.IO.Path.Combine(B, "rcutils.dll"));
		////RuntimeDependencies.Add(System.IO.Path.Combine(B, "rcpputils.dll"));
		////RuntimeDependencies.Add(System.IO.Path.Combine(B, "ament_index_cpp.dll"));
		////RuntimeDependencies.Add(System.IO.Path.Combine(B, "rosidl_runtime_c.dll"));
		////RuntimeDependencies.Add(System.IO.Path.Combine(B, "rosidl_typesupport_cpp.dll"));
		////
		////RuntimeDependencies.Add(Path.Combine(B, "rosidl_runtime_cpp.dll"));
		//RuntimeDependencies.Add(Path.Combine(B, "rmw_implementation.dll"));
		//RuntimeDependencies.Add(Path.Combine(B, "rmw_cyclonedds_cpp.dll"));
		////RuntimeDependencies.Add(Path.Combine(B, "rmw_implementation.dll"));
		////RuntimeDependencies.Add(Path.Combine(B, "rcl_logging_spdlog.dll"));
		////
		////// DDS
		////RuntimeDependencies.Add(System.IO.Path.Combine(B, "rmw_cyclonedds_cpp.dll"));
		////RuntimeDependencies.Add(System.IO.Path.Combine(B, "cycloneddsidl.dll"));
		////RuntimeDependencies.Add(System.IO.Path.Combine(B, "spdlog.dll"));
		//
		////// FastDDS:
		////// RuntimeDependencies.Add(System.IO.Path.Combine(B, "rmw_fastrtps_cpp.dll"));
		////// RuntimeDependencies.Add(System.IO.Path.Combine(B, "fastrtps.dll"));
		////// RuntimeDependencies.Add(System.IO.Path.Combine(B, "fastcdr.dll"));
		//
		//// msg
		////RuntimeDependencies.Add(System.IO.Path.Combine(B, "builtin_interfaces__rosidl_typesupport_cpp.dll"));
		////RuntimeDependencies.Add(System.IO.Path.Combine(B, "std_msgs__rosidl_typesupport_cpp.dll"));
		////RuntimeDependencies.Add(System.IO.Path.Combine(B, "geometry_msgs__rosidl_typesupport_cpp.dll"));
		
		// LIB
		//string Lib = Path.Combine(ROS, "lib");
		//
		//PublicAdditionalLibraries.AddRange(new[] {
        //    Path.Combine(Lib, "rclcpp.lib"),
        //    Path.Combine(Lib, "rcl.lib"),
        //    Path.Combine(Lib, "rcutils.lib"),
        //    Path.Combine(Lib, "rcpputils.lib"),
        //    Path.Combine(Lib, "ament_index_cpp.lib"),
        //    Path.Combine(Lib, "rosidl_runtime_c.lib"),
        //    Path.Combine(Lib, "rosidl_typesupport_cpp.lib"),
        //    Path.Combine(Lib, "rmw_implementation.lib"),
        //    Path.Combine(Lib, "rmw_cyclonedds_cpp.lib"),
        //    Path.Combine(Lib, "rmw_dds_common.lib"),
        //});
		//
        //PublicAdditionalLibraries.AddRange(new[] {
        //    Path.Combine(Lib, "builtin_interfaces__rosidl_typesupport_cpp.lib"),
        //    Path.Combine(Lib, "std_msgs__rosidl_typesupport_cpp.lib"),
        //    Path.Combine(Lib, "geometry_msgs__rosidl_typesupport_cpp.lib"),
        //});
        //
        //PublicAdditionalLibraries.AddRange(new[] {
	    //    Path.Combine(Lib, "rcl_logging_spdlog.lib"),
	    //    //Path.Combine(Lib, "spdlog.lib"),
	    //    Path.Combine(Lib, "rclcpp_action.lib"),
	    //    Path.Combine(Lib, "rclcpp_lifecycle.lib"), 
        //});
        //
        //// DLL
        //string Bin = Path.Combine(ROS, "bin");
        //
        //string[] dlls = {
        //    "rclcpp.dll",
        //    "rcl.dll",
        //    "rcutils.dll",
        //    "rcpputils.dll",
        //    "ament_index_cpp.dll",
        //    "rosidl_runtime_c.dll",
        //    "rosidl_typesupport_cpp.dll",
        //    "rmw_implementation.dll",
        //    "rmw_cyclonedds_cpp.dll",
        //    "cyclonedds.dll",
        //    "rmw_dds_common.dll",
        //    "builtin_interfaces__rosidl_typesupport_cpp.dll",
        //    "std_msgs__rosidl_typesupport_cpp.dll",
        //    "geometry_msgs__rosidl_typesupport_cpp.dll",
        //    "rcl_logging_spdlog.dll",
        //    //"spdlog.dll",
        //    "rclcpp_action.dll",
        //    "rclcpp_lifecycle.dll",
        //};
        //
        //foreach (var name in dlls)
        //{
	    //    PublicDelayLoadDLLs.Add(name); 
	    //    RuntimeDependencies.Add(Path.Combine(Bin, name));  
        //}
        
        // ENGINE
		PublicDependencyModuleNames.AddRange(
			new string[]
			{
				"Core",
			}
			);
			
		
		PrivateDependencyModuleNames.AddRange(
			new string[]
			{
				"CoreUObject",
				"Engine",
			}
			);
		
		
		DynamicallyLoadedModuleNames.AddRange(
			new string[]
			{
			}
			);
	}
}
