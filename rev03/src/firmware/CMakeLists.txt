# SPDX-License-Identifier: Apache-2.0

cmake_minimum_required(VERSION 3.20.0)

find_package(Zephyr REQUIRED HINTS $ENV{ZEPHYR_BASE})
project(kite)

set(ATCA_BUILD_SHARED_LIBS OFF CACHE INTERNAL "")
set(ATCA_PRINTF ON CACHE INTERNAL "")
set(ATCA_HAL_I2C ON CACHE INTERNAL "")
set(ATCA_ATECC608_SUPPORT ON CACHE INTERNAL "")
set(ATCA_POST_DELAY_MS ON CACHE INTERNAL 200)
set(ATCA_NO_HEAP ON CACHE INTERNAL "")
add_subdirectory(cryptoauthlib/lib)

include_directories(app ${CMAKE_CURRENT_BINARY_DIR}/cryptoauthlib/lib
			${CMAKE_CURRENT_SOURCE_DIR}/cryptoauthlib
			${CMAKE_CURRENT_SOURCE_DIR}/cryptoauthlib/lib
			${CMAKE_CURRENT_SOURCE_DIR}/cryptoauthlib/third_party/hal/zephyr)

target_link_libraries(cryptoauth PUBLIC zephyr_interface)
target_link_libraries(app PUBLIC cryptoauth)
target_sources(app PRIVATE src/main.c)
