"""Replace the Go JNI libraries in a copy of an Android APK before signing."""

import argparse
import shutil
from copy import copy
from pathlib import Path
from zipfile import ZipFile


def is_signature(name: str) -> bool:
    directory, _, filename = name.upper().rpartition("/")
    return directory == "META-INF" and (
        filename == "MANIFEST.MF"
        or filename.startswith("SIG-")
        or filename.endswith((".SF", ".RSA", ".DSA", ".EC"))
    )


def repack(apk_path: Path, aar_path: Path, output_path: Path) -> list[str]:
    with ZipFile(apk_path) as apk, ZipFile(aar_path) as aar:
        native_libraries = {
            name: "jni/" + name.removeprefix("lib/")
            for name in apk.namelist()
            if name.startswith("lib/") and name.endswith("/libgojni.so")
        }
        if not native_libraries:
            raise ValueError("The input APK has no libgojni.so")
        for library in native_libraries.values():
            aar.getinfo(library)
        with ZipFile(output_path, "x") as output:
            for entry in apk.infolist():
                name = entry.filename
                if is_signature(name):
                    continue
                replacement = native_libraries.get(name)
                source = aar.open(replacement) if replacement else apk.open(entry)
                with source, output.open(copy(entry), "w") as destination:
                    shutil.copyfileobj(source, destination)
    return sorted(native_libraries)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("original_apk", type=Path)
    parser.add_argument("rebuilt_aar", type=Path)
    parser.add_argument("unsigned_apk", type=Path)
    arguments = parser.parse_args()
    for name in repack(arguments.original_apk, arguments.rebuilt_aar, arguments.unsigned_apk):
        print("Replaced", name)
