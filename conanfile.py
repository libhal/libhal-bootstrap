# Copyright 2024 - 2025 Khalil Estell and the libhal contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy
from conan.tools.build import check_min_cppstd, cross_building
from conan.tools.env import VirtualBuildEnv
import os

required_conan_version = ">=2.2.2"


def add_demo_requirements(conan_file: ConanFile, is_platform: bool = False):
    if not is_platform:
        platform = str(conan_file.options.platform)
        architecture = str(conan_file.settings.arch)

        if platform == "micromod":
            conan_file.output.warning(
                "libhal-micromod usable platform detected...")
            conan_file.requires("libhal-micromod/[^1.1.0]")
        elif architecture.startswith("cortex-m"):
            conan_file.output.warning(
                "libhal-arm-mcu usable platform detected...")
            conan_file.requires("libhal-arm-mcu/[^1.0.0]")
        else:
            conan_file.output.warning("No platform library added...")

    conan_file.requires("libhal-util/[^5.4.0]")


class demo:
    settings = "compiler", "build_type", "os", "arch"
    options = {
        "platform": ["ANY"],
        "micromod_board": ["ANY"],
    }
    default_options = {
        "platform": "unspecified",
        "micromod_board": "unspecified",
    }

    def layout(self):
        if "micromod" == str(self.options.platform):
            build_path = os.path.join("build",
                                      str(self.options.platform),
                                      str(self.options.micromod_board))
            cmake_layout(self, build_folder=build_path)
        else:
            build_path = os.path.join("build",
                                      str(self.options.platform))
            cmake_layout(self, build_folder=build_path)

    def build_requirements(self):
        self.tool_requires("make/4.4.1")
        self.tool_requires("cmake/3.27.1")
        self.tool_requires("libhal-cmake-util/[^4.3.3]")

    def generate(self):
        virt = VirtualBuildEnv(self)
        virt.generate()
        cmake = CMakeDeps(self)
        cmake.generate()
        tc = CMakeToolchain(self)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()


class app:
    settings = "compiler", "build_type", "os", "arch"
    options = {
        "platform": ["ANY"],
        "micromod_board": ["ANY"],
    }
    default_options = {
        "platform": "unspecified",
        "micromod_board": "unspecified",
    }

    def layout(self):
        if "micromod" == str(self.options.platform):
            build_path = os.path.join("build",
                                      str(self.options.platform),
                                      str(self.options.micromod_board))
            cmake_layout(self, build_folder=build_path)
        else:
            build_path = os.path.join("build",
                                      str(self.options.platform))
            cmake_layout(self, build_folder=build_path)

    def build_requirements(self):
        self.tool_requires("make/4.4.1")
        self.tool_requires("cmake/3.27.1")
        self.tool_requires("libhal-cmake-util/[^4.3.3]")

    def generate(self):
        virt = VirtualBuildEnv(self)
        virt.generate()
        cmake = CMakeDeps(self)
        cmake.generate()
        tc = CMakeToolchain(self)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()


def add_library_requirements(conan_file: ConanFile,
                             override_libhal_version: str = None,
                             override_libhal_util_version: str = None):
    libhal_version = "4.9.0"
    libhal_util_version = "5.4.0"
    if override_libhal_version:
        libhal_version = override_libhal_version

    if override_libhal_util_version:
        libhal_util_version = override_libhal_util_version

    conan_file.requires(
        f"libhal/[^{libhal_version}]",
        transitive_headers=True)
    conan_file.requires(
        f"libhal-util/[^{libhal_util_version}]", transitive_headers=True)


class library:
    settings = "compiler", "build_type", "os", "arch"
    exports_sources = ("include/*", "linker_scripts/*", "tests/*", "LICENSE",
                       "CMakeLists.txt", "src/*")

    @property
    def _min_cppstd(self):
        return "20"

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "11",
            "clang": "14",
            "apple-clang": "14.0.0"
        }

    def validate(self):
        if self.settings.get_safe("compiler.cppstd"):
            check_min_cppstd(self, self._min_cppstd)

    def layout(self):
        cmake_layout(self)

    def generate(self):
        virt = VirtualBuildEnv(self)
        virt.generate()
        tc = CMakeToolchain(self)
        tc.generate()
        cmake = CMakeDeps(self)
        cmake.generate()

    def build_requirements(self):
        self.tool_requires("make/4.4.1")
        self.tool_requires("cmake/3.27.1")
        self.tool_requires("libhal-cmake-util/[^4.3.3]")
        self.test_requires("libhal-mock/[^4.0.0]")
        self.test_requires("boost-ext-ut/2.1.0")

    def requirements(self):
        pass

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self,
             "LICENSE",
             dst=os.path.join(self.package_folder, "licenses"),
             src=self.source_folder)
        copy(self,
             "*.h",
             dst=os.path.join(self.package_folder, "include"),
             src=os.path.join(self.source_folder, "include"))
        copy(self,
             "*.hpp",
             dst=os.path.join(self.package_folder, "include"),
             src=os.path.join(self.source_folder, "include"))
        copy(self,
             "*.ld",
             dst=os.path.join(self.package_folder, "linker_scripts"),
             src=os.path.join(self.source_folder, "linker_scripts"))

        cmake = CMake(self)
        cmake.install()


class library_test_package:
    def build_requirements(self):
        self.tool_requires("make/4.4.1")
        self.tool_requires("cmake/3.27.1")

    def layout(self):
        cmake_layout(self)

    def _add_arm_specs_if_applicable(self, tc: CMakeToolchain):
        should_add_flags = (self.settings.os == "baremetal"
                            and self.settings.compiler == "gcc"
                            and str(self.settings.arch).startswith("cortex-m"))

        if not should_add_flags:
            return

        LIB_C_FLAGS = ["--specs=nano.specs", "--specs=nosys.specs"]
        LIB_C_FLAGS_STR = " ".join(LIB_C_FLAGS)
        self.output.info(f"Baremetal ARM GCC Profile detected!")
        self.output.info(f'💉 injecting >> "{LIB_C_FLAGS_STR}"')
        link_flags = tc.variables.get("CMAKE_EXE_LINKER_FLAGS", "")
        link_flags = link_flags + f" {LIB_C_FLAGS_STR}"
        link_flags = link_flags.strip()
        tc.variables["CMAKE_EXE_LINKER_FLAGS"] = link_flags
        FINAL_FLAGS = tc.variables["CMAKE_EXE_LINKER_FLAGS"]
        self.output.info(
            f'tc.variables["CMAKE_EXE_LINKER_FLAGS"] = "{FINAL_FLAGS}"')

    def generate(self):
        virt = VirtualBuildEnv(self)
        virt.generate()
        tc = CMakeToolchain(self)
        self._add_arm_specs_if_applicable(tc)
        tc.generate()
        cmake = CMakeDeps(self)
        cmake.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not cross_building(self):
            bin_path = os.path.join(self.cpp.build.bindirs[0], "test_package")
            self.run(bin_path, env="conanrun")


class libhal_bootstrap(ConanFile):
    name = "libhal-bootstrap"
    version = "4.3.1"
    package_type = "python-require"
