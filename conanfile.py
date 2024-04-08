# Copyright 2024 Khalil Estell
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

required_conan_version = ">=2.0.14"


def add_demo_requirements(conan_file: ConanFile, is_platform: bool = False):
    if not is_platform:
        platform = str(conan_file.options.platform)
        if platform.startswith("lpc40"):
            conan_file.output.warning("Using lpc40 platform library!!")
            conan_file.requires("libhal-lpc40/[^3.0.3]")

        elif platform.startswith("stm32f1"):
            conan_file.output.warning("Using stm32f1 platform library!!")
            conan_file.requires("libhal-stm32f1/[^3.0.0]")

    conan_file.requires("libhal-util/[^4.0.0]")


class demo:
    settings = "compiler", "build_type", "os", "arch", "libc"
    options = {"platform": ["ANY"]}
    default_options = {"platform": "unspecified"}

    def layout(self):
        platform_directory = "build/" + str(self.options.platform)
        cmake_layout(self, build_folder=platform_directory)

    def build_requirements(self):
        self.tool_requires("cmake/3.27.1")
        self.tool_requires("libhal-cmake-util/[^4.0.3]")

    def generate(self):
        virt = VirtualBuildEnv(self)
        virt.generate()
        cmake = CMakeDeps(self)
        cmake.generate()
        tc = CMakeToolchain(self)
        tc.cache_variables["CONAN_LIBC"] = str(self.settings.libc)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()


def add_library_requirements(conan_file: ConanFile,
                             override_libhal_version: str | None = None,
                             override_libhal_util_version: str | None = None):
    libhal_version = "3.1.0"
    libhal_util_version = "4.0.1"
    if override_libhal_version:
        libhal_version = override_libhal_version

    if override_libhal_util_version:
        libhal_util_version = override_libhal_util_version

    conan_file.requires(f"libhal/[^{libhal_version}]", transitive_headers=True)
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
        self.tool_requires("libhal-cmake-util/[^4.0.3]")
        self.test_requires("libhal-mock/[^3.0.0]")
        self.test_requires("boost-ext-ut/1.1.9")

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
        self.tool_requires("cmake/3.27.1")

    def layout(self):
        cmake_layout(self)

    def generate(self):
        virt = VirtualBuildEnv(self)
        virt.generate()
        tc = CMakeToolchain(self)
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
    version = "1.0.1"
    package_type = "python-require"
