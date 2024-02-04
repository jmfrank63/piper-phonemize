import platform
from pathlib import Path
import shutil
import sys

# Available at setup time due to pyproject.toml
from pybind11.setup_helpers import Pybind11Extension, build_ext
from setuptools import setup
from setuptools.command.install import install

_DIR = Path(__file__).parent
_ESPEAK_DIR = _DIR / "install"
_LIB_DIR = _DIR / "lib" / f"Linux-{platform.machine()}"
_ONNXRUNTIME_DIR = _LIB_DIR / "onnxruntime"

__version__ = "1.2.0"

class CustomInstallCommand(install):
    """Customized setuptools install command to copy espeak-ng-data."""

    def run(self):
        # Call superclass install command
        super().run()

        # Check if the operating system is Windows
        if platform.system() != "Windows":
            print("Skipping custom installation steps: not running on Windows")
            return

        # Define the source directories for espeak-ng-data and libraries
        source_data_dir = _ESPEAK_DIR /  "share" / "espeak-ng-data"
        source_bin_dir = _ESPEAK_DIR / "bin"
        source_lib_dir = _ESPEAK_DIR / "lib"

        # Define the target directories within the Python environment
        target_data_dir = (
            Path(sys.prefix) / "Lib" / "site-packages" / "piper_phonemize" / "espeak-ng-data"
        )
        target_lib_dir = Path(sys.prefix) / "Library" / "bin"

        # Copy espeak-ng-data directory
        self.copy_directory(source_data_dir, target_data_dir)

        # Copy espeak-ng library from bin
        self.copy_directory(source_bin_dir, target_lib_dir, pattern="espeak-ng.dll")

        # Copy ONNX Runtime library
        self.copy_directory(source_lib_dir, target_lib_dir, pattern="onnxruntime.dll")

    def copy_directory(self, source, target, pattern="*"):
        if not source.exists():
            print(f"Source directory {source} does not exist. Skipping.")
            return

        if not target.exists():
            target.mkdir(parents=True, exist_ok=True)

        for item in source.glob(pattern):
            if item.is_file():
                shutil.copy(item, target)
                print(f"Copied {item} to {target}")

ext_modules = [
    Pybind11Extension(
        "piper_phonemize_cpp",
        [
            "src/python.cpp",
            "src/phonemize.cpp",
            "src/phoneme_ids.cpp",
            "src/tashkeel.cpp",
        ],
        define_macros=[("VERSION_INFO", __version__)],
        include_dirs=[str(_ESPEAK_DIR / "include"), str(_ONNXRUNTIME_DIR / "include")],
        library_dirs=[str(_ESPEAK_DIR / "lib"), str(_ONNXRUNTIME_DIR / "lib")],
        libraries=["espeak-ng", "onnxruntime"],
    ),
]

setup(
    name="piper_phonemize",
    version=__version__,
    author="Michael Hansen",
    author_email="mike@rhasspy.org",
    url="https://github.com/rhasspy/piper-phonemize",
    description="Phonemization libary used by Piper text to speech system",
    long_description="",
    packages=["piper_phonemize"],
    package_data={
        "piper_phonemize": [
            str(p) for p in (_DIR / "piper_phonemize" / "espeak-ng-data").rglob("*")
        ]
        + [str(_DIR / "libtashkeel_model.ort")]
    },
    include_package_data=True,
    ext_modules=ext_modules,
    cmdclass={"build_ext": build_ext},
    zip_safe=False,
    python_requires=">=3.7",
)
