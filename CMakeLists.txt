# LittleBigRecomp -- LittleBigPlanet (BCES00141, v02.00) statically recompiled
# onto the ps3recomp runtime (vendored in ps3recomp/).
#
#   tools/relift.sh                     # lift game/EBOOT.elf -> src/recomp, src/gen
#   cmake -S . -B build -G Ninja && cmake --build build
#   ./build/LittleBigRecomp vfs/PS3_GAME/USRDIR/EBOOT.elf
cmake_minimum_required(VERSION 3.20)

if(NOT CMAKE_BUILD_TYPE AND NOT CMAKE_CONFIGURATION_TYPES)
    set(CMAKE_BUILD_TYPE Release CACHE STRING "build type" FORCE)
endif()

project(LittleBigRecomp C CXX)
set(CMAKE_C_STANDARD 17)
set(CMAKE_CXX_STANDARD 20)

set(PS3RECOMP_DIR "${CMAKE_CURRENT_SOURCE_DIR}/ps3recomp")
add_subdirectory("${PS3RECOMP_DIR}" "${CMAKE_BINARY_DIR}/ps3recomp_sdk" EXCLUDE_FROM_ALL)

file(GLOB RECOMP_SOURCES "src/recomp/*.cpp")
file(GLOB GEN_SOURCES    "src/gen/*.cpp" "src/gen/*.c")
file(GLOB_RECURSE SPU_SOURCES "src/spu_gen/*.c")
file(GLOB PORT_SOURCES   "src/port/*.cpp" "src/port/*.c")
if(NOT RECOMP_SOURCES)
    message(FATAL_ERROR "src/recomp/ is empty -- run tools/relift.sh first")
endif()

add_executable(LittleBigRecomp
    "${PS3RECOMP_DIR}/runtime/ppu/tests/boot_main.cpp"
    "${PS3RECOMP_DIR}/runtime/ppu/ppu_loader.cpp"
    "${PS3RECOMP_DIR}/runtime/ppu/ppu_hle.cpp"
    "${PS3RECOMP_DIR}/runtime/ppu/ppu_sysprx.cpp"
    "${PS3RECOMP_DIR}/runtime/ppu/ppu_fs.cpp"
    ${PORT_SOURCES}
    ${GEN_SOURCES}
    ${SPU_SOURCES}
    ${RECOMP_SOURCES}
)

target_include_directories(LittleBigRecomp PRIVATE
    "${CMAKE_CURRENT_SOURCE_DIR}/src/recomp"
    "${PS3RECOMP_DIR}/include"
    "${PS3RECOMP_DIR}/runtime/ppu"
    "${PS3RECOMP_DIR}/runtime/spu"
    "${PS3RECOMP_DIR}/runtime/memory"
    "${PS3RECOMP_DIR}/runtime/syscalls"
    "${PS3RECOMP_DIR}/runtime/platform"
    "${PS3RECOMP_DIR}/libs/video"
)
target_link_libraries(LittleBigRecomp PRIVATE ps3recomp_runtime)
set_target_properties(LittleBigRecomp PROPERTIES LINKER_LANGUAGE CXX)

# Lifted code type-puns guest memory, relies on wrapping signed arithmetic and
# must not grow FMAs the PPU did not have.
target_compile_options(LittleBigRecomp PRIVATE -fno-strict-aliasing -fwrapv -ffp-contract=off)
set_source_files_properties(${RECOMP_SOURCES} PROPERTIES COMPILE_OPTIONS "-w")
if(SPU_SOURCES)
    set_source_files_properties(${SPU_SOURCES} PROPERTIES
        INCLUDE_DIRECTORIES "${PS3RECOMP_DIR}/runtime/spu"
        COMPILE_DEFINITIONS SPU_USE_DISPATCH_MT
        COMPILE_OPTIONS "-w")
endif()
# Every guest call is a host call, so recompiled call chains nest deeply.
if(APPLE)
    target_link_options(LittleBigRecomp PRIVATE -Wl,-stack_size,0x10000000)
endif()
