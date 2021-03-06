<a name="unreleased"></a>
## [Unreleased]


<a name="1.2.1"></a>
## [1.2.1] - 2021-07-14
### Fix
- **worker:** incorrect finished path passed


<a name="1.2.0"></a>
## [1.2.0] - 2021-07-13
### Chore
- **code:** formatting
- **version:** bump version

### Feat
- **executor:** Fail the task on exception instead of retry


<a name="1.1.6"></a>
## [1.1.6] - 2021-07-13
### Chore
- **version:** bump to 1.1.6

### Fix
- **executor:** bug, where custom metadata would be used on crash instead of original data


<a name="1.1.5"></a>
## [1.1.5] - 2021-07-12
### Chore
- **project:** Merge branch 'main' of github.com:SpotlightData/nanowire-service-py into main
- **version:** bump to 1.1.5

### Docs
- **readme:** update notes on types
- **readme:** update notes


<a name="1.1.4"></a>
## [1.1.4] - 2021-07-12
### Chore
- **version:** bump to 1.1.4

### Fix
- **worker:** update type definitions


<a name="1.1.3"></a>
## [1.1.3] - 2021-07-12
### Chore
- **version:** bump to 1.1.3

### Feat
- **worker:** allow to close path


<a name="1.1.2"></a>
## [1.1.2] - 2021-06-30
### Chore
- **project:** update hooks to check for codestyles
- **release:** bump to 1.1.2

### Fix
- **handler:** corrent types for class
- **module:** correct environment types in create function


<a name="1.1.1"></a>
## [1.1.1] - 2021-06-30
### Chore
- **codestyle:** format code
- **release:** bump to 1.1.1
- **release:** Update changelog


<a name="1.1.0"></a>
## [1.1.0] - 2021-06-30
### Chore
- **docs:** update change log to 1.0.1
- **release:** Bump to 1.1.0 version
- **version:** bump to 1.0.2

### Docs
- **readme:** fix incorrect method access
- **readme:** add a note about versioning impact on code

### Feat
- **executor:** add optional skip for publishing
- **executor:** swap action responsibilties to executor - Allows worker to be responsible for SQL queries instead - This means it can be utilised directly
- **handler:** allow optional worker for times when it's not needed
- **handler:** pass down worker to handler for advanced use cases.
- **handler:** allow for metadata to be validated
- **types:** add optional skip for publishing
- **worker:** retrieve plugin instances fix(worker): fix incorrect types passed to workflow instance
- **worker:**  allow to query the path
- **worker:** path access function
- **worker:** add more advanced functionality for task creation

### Fix
- **handler:** incorrect worker assignment
- **instance:** incorrect return typer
- **worker:** make branch an instance function


<a name="1.0.1"></a>
## [1.0.1] - 2021-06-24
### Chore
- **docs:** update changelog to 1.0.0
- **project:** version bump 1.0.1

### Fix
- **tests:** update formatting and fix type missmatch


<a name="1.0.0"></a>
## [1.0.0] - 2021-06-24
### Chore
- **docs:** update changelog
- **version:** bump

### Docs
- **readme:** update examples to add heartbeat

### Feat
- **build:** add changelog task
- **env:** separate scheduler pubsub and service id
- **executor:** run threads in daemon
- **executor:** create threaded heartbeat
- **instance:** Change register functions to include service id
- **worker:** adjust setup for new heartbeat variant.

### Fix
- **tests:** update tests to work under new conditions


<a name="0.3.3"></a>
## [0.3.3] - 2021-06-16
### Chore
- **version:** bump

### Feat
- **executor:** better error visiblity


<a name="0.3.2"></a>
## [0.3.2] - 2021-06-11
### Chore
- **version:** 0.3.2 release

### Docs
- **readme:** typo
- **readme:** typo

### Feat
- **project:** add hook to validate against pyproject version

### Fix
- **dependencies:** allow looser pydantic version


<a name="0.3.1"></a>
## [0.3.1] - 2021-06-08
### Fix
- **version:** update project version


<a name="0.3.0"></a>
## [0.3.0] - 2021-06-08
### Chore
- **changelog:** release changelog

### Docs
- **readme:** update readme

### Fix
- **version:** update project version


<a name="0.2.0"></a>
## [0.2.0] - 2021-06-08
### Build
- **project:** add changelog generator command
- **project:** install hooks together with other dependencies

### Chore
- **changelog:** release changelog

### Ci
- **github:** publishing only when tagged
- **github:** update secret references
- **github:** update secret references
- **github:** update secret references
- **github:** update secret references
- **github:** add release actions

### Docs
- **overview:** create improved docs
- **project:** enforce messages and create changelog autogen

### Feat
- **executor:** remove fastapi dependency
- **handler:** Simplify initialisation step of using the library
- **module:** Improve testability and simplicity of module setup

### Fix
- **module:** fix incorrect import
- **mypy:** Update library and fix exports of modules

### Style
- **project:** reformat code

### Test
- **setup:** move over test dependencies


<a name="0.1.5"></a>
## [0.1.5] - 2021-06-07

<a name="0.1.4"></a>
## [0.1.4] - 2021-06-07

<a name="0.1.3"></a>
## [0.1.3] - 2021-06-07

<a name="0.1.2"></a>
## [0.1.2] - 2021-06-04

<a name="0.1.1"></a>
## [0.1.1] - 2021-06-04

<a name="0.1.0"></a>
## 0.1.0 - 2021-06-03

[Unreleased]: https://github.com/SpotlightData/nanowire-service-py/compare/1.2.1...HEAD
[1.2.1]: https://github.com/SpotlightData/nanowire-service-py/compare/1.2.0...1.2.1
[1.2.0]: https://github.com/SpotlightData/nanowire-service-py/compare/1.1.6...1.2.0
[1.1.6]: https://github.com/SpotlightData/nanowire-service-py/compare/1.1.5...1.1.6
[1.1.5]: https://github.com/SpotlightData/nanowire-service-py/compare/1.1.4...1.1.5
[1.1.4]: https://github.com/SpotlightData/nanowire-service-py/compare/1.1.3...1.1.4
[1.1.3]: https://github.com/SpotlightData/nanowire-service-py/compare/1.1.2...1.1.3
[1.1.2]: https://github.com/SpotlightData/nanowire-service-py/compare/1.1.1...1.1.2
[1.1.1]: https://github.com/SpotlightData/nanowire-service-py/compare/1.1.0...1.1.1
[1.1.0]: https://github.com/SpotlightData/nanowire-service-py/compare/1.0.1...1.1.0
[1.0.1]: https://github.com/SpotlightData/nanowire-service-py/compare/1.0.0...1.0.1
[1.0.0]: https://github.com/SpotlightData/nanowire-service-py/compare/0.3.3...1.0.0
[0.3.3]: https://github.com/SpotlightData/nanowire-service-py/compare/0.3.2...0.3.3
[0.3.2]: https://github.com/SpotlightData/nanowire-service-py/compare/0.3.1...0.3.2
[0.3.1]: https://github.com/SpotlightData/nanowire-service-py/compare/0.3.0...0.3.1
[0.3.0]: https://github.com/SpotlightData/nanowire-service-py/compare/0.2.0...0.3.0
[0.2.0]: https://github.com/SpotlightData/nanowire-service-py/compare/0.1.5...0.2.0
[0.1.5]: https://github.com/SpotlightData/nanowire-service-py/compare/0.1.4...0.1.5
[0.1.4]: https://github.com/SpotlightData/nanowire-service-py/compare/0.1.3...0.1.4
[0.1.3]: https://github.com/SpotlightData/nanowire-service-py/compare/0.1.2...0.1.3
[0.1.2]: https://github.com/SpotlightData/nanowire-service-py/compare/0.1.1...0.1.2
[0.1.1]: https://github.com/SpotlightData/nanowire-service-py/compare/0.1.0...0.1.1
