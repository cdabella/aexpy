from typing import override
import zipfile
from dataclasses import dataclass, field
from email.message import Message
from email.parser import Parser
from logging import Logger
from pathlib import Path

from aexpy import getCacheDirectory, utils
from . import Preprocessor

FILE_ORIGIN = "https://files.pythonhosted.org/"
FILE_TSINGHUA = "https://pypi.tuna.tsinghua.edu.cn/"
INDEX_ORIGIN = "https://pypi.org/simple/"
INDEX_TSINGHUA = "https://pypi.tuna.tsinghua.edu.cn/simple/"


def readPackageInfo(path: Path):
    return Parser().parsestr(path.read_text())


@dataclass
class CompatibilityTag:
    python: str = "py3"
    abi: str = "none"
    platform: list[str] = field(default_factory=lambda: ["any"])

    @classmethod
    def fromfile(cls, filename: str):
        filename = Path(filename).stem
        try:
            segs = filename.split("-")
            return CompatibilityTag(segs[-3], segs[-2], segs[-1].split("."))
        except:
            return None


@dataclass
class DistInfo:
    metadata: Message
    topLevel: list[str]
    wheel: Message

    @property
    def name(self):
        return str(self.metadata.get("name"))

    @property
    def version(self):
        return str(self.metadata.get("version"))

    @property
    def pyversion(self) -> str | None:
        tags = self.wheel.get_all("tag")
        if tags:
            for rawTag in tags:
                tag = CompatibilityTag.fromfile(rawTag) or CompatibilityTag()
                if "any" in tag.platform:
                    requires = str(self.metadata.get("requires-python"))
                    requires = list(map(lambda x: x.strip(), requires.split(",")))
                    if len(requires) == 0:
                        return None
                    for item in requires:
                        if item.startswith(">="):
                            version = item.removeprefix(">=").strip()
                            if version.startswith("3."):
                                if int(version.split(".")[1]) < 8:
                                    return "3.8"
                                else:
                                    return version
                            else:
                                continue
                        elif item.startswith("<="):
                            return item.removeprefix("<=").strip()
                    return "3.8"
                else:
                    for i in range(7, 13):
                        if f"py3{i}" in tag.python or f"cp3{i}" in tag.python:
                            return f"3.{i}"
        return "3.8"

    @classmethod
    def fromdir(cls, path: Path, project: str = ""):
        distinfoDir = list(path.glob(f"{project}*.dist-info"))
        if len(distinfoDir) == 0:
            return None
        distinfoDir = distinfoDir[0]
        try:
            metadata: Message = readPackageInfo(distinfoDir / "METADATA")
            tp = distinfoDir / "top_level.txt"

            if tp.exists():
                toplevel = [s.strip() for s in tp.read_text().splitlines() if s.strip()]
            elif metadata.get("Name", None):
                toplevel = [str(metadata.get("Name")).replace("-", "_")]
            else:
                toplevel = []

            return DistInfo(
                metadata=metadata,
                topLevel=toplevel,
                wheel=readPackageInfo(distinfoDir / "WHEEL"),
            )
        except:
            return None


def unpackWheel(wheelFile: Path, targetDir: Path):
    utils.ensureDirectory(targetDir)
    with zipfile.ZipFile(wheelFile) as f:
        f.extractall(targetDir)


class WheelUnpackPreprocessor(Preprocessor):
    def __init__(self, cacheDir: Path | None, logger: Logger | None = None):
        super().__init__(logger)
        self.cacheDir = cacheDir or getCacheDirectory()
        utils.ensureDirectory(self.cacheDir)

    @override
    def preprocess(self, product):
        assert (
            product.wheelFile and product.wheelFile.exists()
        ), "No wheel file provided."

        targetDir = self.cacheDir / product.wheelFile.stem
        assert (
            not targetDir.exists()
        ), f"The unpacked directory has been existed: {targetDir}"
        unpackWheel(product.wheelFile, targetDir)
        product.rootPath = targetDir


class WheelMetadataPreprocessor(Preprocessor):
    @override
    def preprocess(self, product):
        assert product.rootPath, "No root path provided."

        distInfo = DistInfo.fromdir(product.rootPath, product.release.project)
        if distInfo:
            if distInfo.pyversion:
                if not product.pyversion:
                    product.pyversion = distInfo.pyversion
            if distInfo.name:
                if product.release.project:
                    assert (
                        product.release.project == distInfo.name
                    ), "Different name between release and dist-info."
                else:
                    product.release.project = distInfo.name
            if distInfo.version:
                if product.release.version:
                    assert (
                        product.release.version == distInfo.version
                    ), "Different version between release and dist-info."
                else:
                    product.release.version = distInfo.version
            product.topModules.extend(distInfo.topLevel)
            if distInfo.metadata:
                product.description = str(distInfo.metadata.get_payload())
                product.metadata = [(x, str(y)) for x, y in distInfo.metadata.items()]
