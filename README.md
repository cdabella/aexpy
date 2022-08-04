# ![AexPy](https://socialify.git.ci/StardustDL/aexpy/image?description=1&font=Bitter&forks=1&issues=1&language=1&owner=1&pulls=1&stargazers=1&theme=Light "AexPy")

[![](https://github.com/StardustDL/aexpy/workflows/CI/badge.svg)](https://github.com/StardustDL/aexpy/actions) [![](https://img.shields.io/github/license/StardustDL/aexpy.svg)](https://github.com/StardustDL/coxbuild/blob/master/LICENSE) [![](https://img.shields.io/pypi/v/aexpy)](https://pypi.org/project/aexpy/) [![Downloads](https://pepy.tech/badge/aexpy?style=flat)](https://pepy.tech/project/aexpy) [![](https://img.shields.io/docker/pulls/stardustdl/aexpy?style=flat)](https://hub.docker.com/r/stardustdl/aexpy)

[AexPy](https://aexpy.netlify.app) */eɪkspaɪ/* is an **A**pi **EX**plorer in **PY**thon for detecting API breaking changes in Python packages.

> AexPy is the prototype implementation of the conference paper "**AexPy: Detecting API Breaking Changes in Python Packages**" in the 33rd IEEE International Symposium on Software Reliability Engineering (ISSRE 2022).
> 
> If you use our approach or results in your work, please cite it according to [the citation file](CITATIONS.bib).

https://user-images.githubusercontent.com/34736356/182772349-af0a5f20-d009-4daa-b4a9-593922ed66fe.mov

- Approach Design & Paper are in AexPy's conference paper.
- Main Repository & Implemetation are in [AexPy's repository](https://github.com/StardustDL/aexpy).
- Documents & Data are in [AexPy's website](https://aexpy.netlify.app/).

AexPy also provides a framework to process Python packages, extract APIs, and detect changes, which is designed for easily reusing and customizing. See the following "Advanced Tools" section and the source code for details.

## Install

We recommend using our Docker image for running AexPy. Other distributions may suffer from environment errors.

```sh
docker pull stardustdl/aexpy:latest
```

## Usage

### Front-end

AexPy provides a convenient frontend for exploring APIs and changes. Use the following command to start the server, and then access the front-end at `http://localhost:8008` in browser.

```sh
docker run -p 8008:8008 stardustdl/aexpy:latest serve
```

### Command-line

Use the following command to detect changes between v1.0 and v2.0 of a package named demo:

```sh
docker run stardustdl/aexpy:latest report demo@1.0:2.0

# e.g. detect API changes between jinja2 v3.1.1 and v3.1.2
docker run stardustdl/aexpy:latest report jinja2@3.1.1:3.1.2
```

Use the following command to extract API information of v1.0 of a package named demo:

```sh
docker run stardustdl/aexpy:latest extract demo@1.0

# e.g. extract APIs from click v8.1.3
docker run stardustdl/aexpy:latest extract click@8.1.3
```

For all available commands, use the following command:

```sh
docker run stardustdl/aexpy:latest --help
```

## Advanced Tools

### Batching

AexPy supports processing all available versions of a package in batch.

```sh
aexpy batch coxbuild
```

### Logging

The processing may cost time, you can use multiple `-v` for verbose logs.

```sh
docker run aexpy:latest -vvv extract click@8.1.3
```

### Data

You can mount cache directory to `/data` to save the processed data. AexPy will use the cache data if it exists, and produce results in JSON format under the cache directory.

```sh
docker run -v /path/to/cache:/data aexpy:latest extract click@8.1.3

cat /path/to/cache/extracting/types/click/8.1.3.json
```

### Pipeline

AexPy has five stages in its pipeline as follows, use the corresponding command to run the corresponding stage.

```sh
aexpy preprocess coxbuild@0.0.1
aexpy extract coxbuild@0.0.1
aexpy diff coxbuild@0.0.1:0.0.2
aexpy evaluate coxbuild@0.0.1:0.0.2
aexpy report coxbuild@0.0.1:0.0.2
```

The five stages are loosely coupled. The adjacent stages transfer data by JSON, defined [models](./src/aexpy/models/) directory for details. You can easily write your own implementation for every stage, and combine your implementation into the pipeline. See [third](./src/aexpy/third/) directory for an example on how to implement stages and integrate other tools.