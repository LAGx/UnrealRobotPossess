// Copyright Yurii (Kvark) Maruda. Free open sample.

// WARNING: avoid to include this in .h files.
#pragma once

THIRD_PARTY_INCLUDES_START

#pragma push_macro("check")
#ifdef check
  #undef check
#endif

#pragma push_macro("verify")
#ifdef verify
  #undef verify
#endif

#include <assert.h>
#ifndef assert
  #define assert(x) ((void)0) // fallback
#endif

#include <rclcpp/rclcpp.hpp>
#include <rcutils/env.h>
#include <rmw/rmw.h>

#pragma pop_macro("verify")
#pragma pop_macro("check")

THIRD_PARTY_INCLUDES_END