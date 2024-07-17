# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

<!-- towncrier release notes start -->

# Port_Ocean 0.1.65 (2024-07-10)

### Improvements

- Bumped ocean version to ^0.9.4 (#1)


# Port_Ocean 0.1.64 (2024-07-09)

### Improvements

- Bumped ocean version to ^0.9.3 (#1)


# Port_Ocean 0.1.63 (2024-07-07)

### Improvements

- Bumped ocean version to ^0.9.2 (#1)


# Port_Ocean 0.1.62 (2024-06-27)

### Bug Fixes

- Updated the jq mapping to make the vulnerabilities unique per project


# Port_Ocean 0.1.61 (2024-06-25)

### Improvements

- Utilizing the latest Targets API (2024-05-23~beta): Updated the integration to leverage the latest version of Snyk's Targets API. This change is crucial because it introduces a relationships attribute, containing the essential organisation id needed to accurately link each target to its parent organization. (#1)
- Updated the default blueprints to the following structure: Vuln -> Project -> Target -> Organization. 


# Port_Ocean 0.1.60 (2024-06-23)

### Improvements

- Bumped ocean version to ^0.9.1 (#1)


# Port_Ocean 0.1.59 (2024-06-19)

### Improvements

- Bumped ocean version to ^0.9.0 (#1)


# Port_Ocean 0.1.58 (2024-06-16)

### Improvements

- Bumped ocean version to ^0.8.0 (#1)


# Port_Ocean 0.1.57 (2024-06-13)

### Improvements

- Bumped ocean version to ^0.7.1 (#1)


# Port_Ocean 0.1.56 (2024-06-13)

### Improvements

- Bumped ocean version to ^0.7.0 (#1)


# Port_Ocean 0.1.55 (2024-06-10)

### Improvements

- Bumped ocean version to ^0.6.0 (#1)


# Port_Ocean 0.1.54 (2024-06-05)

### Improvements

- Bumped ocean version to ^0.5.27 (#1)


# Port_Ocean 0.1.53 (2024-06-03)

### Improvements

- Bumped ocean version to ^0.5.25 (#1)


# Port_Ocean 0.1.52 (2024-06-02)

### Improvements

- Bumped ocean version to ^0.5.24 (#1)


# Port_Ocean 0.1.51 (2024-05-30)

### Improvements

- Bumped ocean version to ^0.5.23 (#1)
- Updated the base image used in the Dockerfile that is created during integration scaffolding from `python:3.11-slim-buster` to `python:3.11-slim-bookworm`


# Port_Ocean 0.1.50 (2024-05-29)

### Improvements

- Bumped ocean version to ^0.5.22 (#1)


# Port_Ocean 0.1.49 (2024-05-26)

### Improvements

- Bumped ocean version to ^0.5.21 (#1)


# Port_Ocean 0.1.48 (2024-05-26)

### Improvements

- Bumped ocean version to ^0.5.20 (#1)
- Removed the config.yaml file due to unused overrides


# Port_Ocean 0.1.47 (2024-05-16)

### Improvements

- Bumped ocean version to ^0.5.19 (#1)


# Port_Ocean 0.1.46 (2024-05-12)

### Improvements

- Bumped ocean version to ^0.5.18 (#1)


# Port_Ocean 0.1.45 (2024-05-01)

### Improvements

- Bumped ocean version to ^0.5.17 (#1)


# Port_Ocean 0.1.44 (2024-05-01)

### Improvements

- Bumped ocean version to ^0.5.16 (#1)


# Port_Ocean 0.1.43 (2024-04-30)

### Improvements

- Bumped ocean version to ^0.5.15 (#1)


# Port_Ocean 0.1.42 (2024-04-24)

### Improvements

- Bumped ocean version to ^0.5.14 (#1)


# Port_Ocean 0.1.41 (2024-04-17)

### Improvements

- Bumped ocean version to ^0.5.12 (#1)


# Port_Ocean 0.1.40 (2024-04-11)

### Improvements

- Bumped ocean version to ^0.5.11 (#1)


# Port_Ocean 0.1.39 (2024-04-10)

### Improvements

- Bumped ocean version to ^0.5.10 (#1)


# Port_Ocean 0.1.38 (2024-04-04)

### Bug Fixes

- Fixed request json error in snyk client and removed code section that handles SNYK-9999 code.


# Port_Ocean 0.1.37 (2024-04-03)

### Bug Fixes

- Fixed a bug in the pagination logic that caused the integration to return SNYK-9999 error


# Port_Ocean 0.1.36 (2024-04-03)

### Bug Fixes

- Fixed handling of code SNYK-9999 from Snyk Api


# Port_Ocean 0.1.35 (2024-04-02)

### Bug Fixes

- Fixed _get_paginated_resources method to handle code SNYK-9999


# Port_Ocean 0.1.34 (2024-04-01)

### Improvements

- Bumped ocean version to ^0.5.9 (#1)


# Port_Ocean 0.1.33 (2024-04-01)

### Bug Fixes

- Fixed an issue when the snyk API returns internal error code SNYK-9999 and caused the resync to fail (PORT-7454)


# Port_Ocean 0.1.32 (2024-03-28)

### Improvements

- Bumped ocean version to ^0.5.8 (#1)


# Port_Ocean 0.1.31 (2024-03-21)

### Improvements

- Expand the origins Enum of the Snyk Target blueprint


# Port_Ocean 0.1.30 (2024-03-20)

### Improvements

- Bumped ocean version to ^0.5.7 (#1)


# Port_Ocean 0.1.29 (2024-03-17)

### Improvements

- Bumped ocean version to ^0.5.6 (#1)


# Port_Ocean 0.1.28 (2024-03-06)

### Improvements

- Bumped ocean version to ^0.5.5 (#1)


# Port_Ocean 0.1.27 (2024-03-03)

### Improvements

- Bumped ocean version to ^0.5.4 (#1)


# Port_Ocean 0.1.26 (2024-03-03)

### Improvements

- Bumped ocean version to ^0.5.3 (#1)


# Port_Ocean 0.1.25 (2024-02-21)

### Improvements

- Bumped ocean version to ^0.5.2 (#1)


# Port_Ocean 0.1.24 (2024-02-20)

### Improvements

- Bumped ocean version to ^0.5.1 (#1)


# Port_Ocean 0.1.23 (2024-02-18)

### Improvements

- Bumped ocean version to ^0.5.0 (#1)


# Port_Ocean 0.1.22 (2024-01-23)

### Improvements

- Bumped ocean version to ^0.4.17 (#1)


# Port_Ocean 0.1.21 (2024-01-12)

### Features
- Added support for Snyk Organization
- Added a new feature to enable automatic discovery and syncing of groups and associated organizations, providing users with the ability to filter and fetch all relevant data seamlessly. This helps to avoid the situation of having to install the exporter per every organization (#5551)

### Improvements

- The `organizationId` parameter, previously required, is now optional. Users are no longer obligated to provide this parameter, allowing for more flexibility in fetching data for multiple organizations


# Port_Ocean 0.1.20 (2024-01-11)

### Improvements

- Bumped ocean version to ^0.4.16 (#1)


# Port_Ocean 0.1.19 (2024-01-07)

### Improvements

- Bumped ocean version to ^0.4.15 (#1)


# Port_Ocean 0.1.18 (2024-01-07)

### Improvements

- Bumped ocean version to ^0.4.14 (#1)


# Port_Ocean 0.1.17 (2024-01-01)

### Improvements

- Bumped ocean version to ^0.4.13 (#1)


# Port_Ocean 0.1.16 (2023-12-24)

### Improvements

- Bumped ocean version to ^0.4.12 (#1)


# Port_Ocean 0.1.15 (2023-12-21)

### Improvements

- Bumped ocean version to ^0.4.11 (#1)


# Port_Ocean 0.1.14 (2023-12-21)

### Improvements

- Bumped ocean version to ^0.4.10 (#1)


# Port_Ocean 0.1.13 (2023-12-14)

### Improvements

- Bumped ocean version to ^0.4.8 (#1)


# Port_Ocean 0.1.12 (2023-12-05)

### Improvements

- Bumped ocean version to ^0.4.7 (#1)


# Port_Ocean 0.1.11 (2023-12-04)

### Improvements

- Bumped ocean version to ^0.4.6 (#1)


# Port_Ocean 0.1.10 (2023-11-30)

### Improvements

- Bumped ocean version to ^0.4.5 (#1)


# Port_Ocean 0.1.9 (2023-11-29)

### Improvements

- Bumped ocean version to ^0.4.4 (#1)
- Changed the httpx client to be the ocean's client for better connection error handling and request retries


# Port_Ocean 0.1.8 (2023-11-21)

### Improvements

- Bumped ocean version to ^0.4.3 (#1)


# Port_Ocean 0.1.7 (2023-11-08)

### Improvements

- Bumped ocean version to ^0.4.2 (#1)


# Port_Ocean 0.1.6 (2023-11-03)

### Improvements

- Bumped ocean version to ^0.4.1 (#1)


# Port_Ocean 0.1.5 (2023-11-01)

### Improvements

- Bumped ocean version to ^0.4.0 and handle ONCE event listener (#1)


# Port_Ocean 0.1.4 (2023-10-29)

### Improvements

- Bumped ocean version to 0.3.2 (#1)


# Snyk 0.1.3 (2023-10-16)

### Improvements

- Align README with configuration file (#3)


# Snyk 0.1.2 (2023-10-02)

### Improvements

- Try catch 404 error (#2)


# Snyk 0.1.1 (2023-09-27)

### Improvements

- Bumped ocean to version 0.3.1 (#1)

# 0.1.0 (2023-08-16)

### Features

- Implemented Snyk integration using Ocean
