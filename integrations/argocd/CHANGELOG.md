# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

<!-- towncrier release notes start -->

# Port_Ocean 0.1.67 (2024-07-24)

### Improvements

- Bumped ocean version to ^0.9.5


# Port_Ocean 0.1.66 (2024-07-10)

### Improvements

- Added description to configuration properties in spec.yaml (PORT-9118)


# Port_Ocean 0.1.65 (2024-07-10)

### Improvements

- Bumped ocean version to ^0.9.4 (#1)


# Port_Ocean 0.1.64 (2024-07-09)

### Improvements

- Bumped ocean version to ^0.9.3 (#1)


# Port_Ocean 0.1.63 (2024-07-07)

### Improvements

- Bumped ocean version to ^0.9.2 (#1)


# Port_Ocean 0.1.62 (2024-06-23)

### Improvements

- Bumped ocean version to ^0.9.1 (#1)


# Port_Ocean 0.1.61 (2024-06-19)

### Improvements

- Bumped ocean version to ^0.9.0 (#1)


# Port_Ocean 0.1.60 (2024-06-16)

### Improvements

- Updated spec.yaml indication that saas installation is not supported


# Port_Ocean 0.1.59 (2024-06-16)

### Improvements

- Bumped ocean version to ^0.8.0 (#1)


# Port_Ocean 0.1.58 (2024-06-13)

### Improvements

- Bumped ocean version to ^0.7.1 (#1)


# Port_Ocean 0.1.57 (2024-06-13)

### Improvements

- Bumped ocean version to ^0.7.0 (#1)


# Port_Ocean 0.1.56 (2024-06-10)

### Improvements

- Bumped ocean version to ^0.6.0 (#1)


# Port_Ocean 0.1.55 (2024-06-05)

### Improvements

- Bumped ocean version to ^0.5.27 (#1)


# Port_Ocean 0.1.54 (2024-06-03)

### Improvements

- Bumped ocean version to ^0.5.25 (#1)


# Port_Ocean 0.1.53 (2024-06-02)

### Improvements

- Bumped ocean version to ^0.5.24 (#1)


# Port_Ocean 0.1.52 (2024-05-30)

### Improvements

- Bumped ocean version to ^0.5.23 (#1)
- Updated the base image used in the Dockerfile that is created during integration scaffolding from `python:3.11-slim-buster` to `python:3.11-slim-bookworm`


# Port_Ocean 0.1.51 (2024-05-29)

### Improvements

- Bumped ocean version to ^0.5.22 (#1)


# Port_Ocean 0.1.50 (2024-05-26)

### Improvements

- Bumped ocean version to ^0.5.21 (#1)


# Port_Ocean 0.1.49 (2024-05-26)

### Improvements

- Bumped ocean version to ^0.5.20 (#1)
- Update the config.yaml file to have only the overridden configuration


# Port_Ocean 0.1.48 (2024-05-16)

### Improvements

- Updated the icon on the image blueprint from AWS to Docker


# Port_Ocean 0.1.47 (2024-05-16)

### Improvements

- Bumped ocean version to ^0.5.19 (#1)


# Port_Ocean 0.1.46 (2024-05-12)

### Improvements

- Bumped ocean version to ^0.5.18 (#1)


# Port_Ocean 0.1.45 (2024-05-06)

### Improvements

- Updated the relationship between images and k8s resource from many to one
- Deleted all the properties from the image blueprint since none of the properties can be extracted from the k8s resource


# Port_Ocean 0.1.44 (2024-05-01)

### Improvements

- Bumped ocean version to ^0.5.17 (#1)


# Port_Ocean 0.1.43 (2024-05-01)

### Improvements

- Bumped ocean version to ^0.5.16 (#1)


# Port_Ocean 0.1.42 (2024-04-30)

### Improvements

- Updated the default mapping to ingest all images used by deployments and establish a relationship between them


# Port_Ocean 0.1.41 (2024-04-30)

### Improvements

- Bumped ocean version to ^0.5.15 (#1)


# Port_Ocean 0.1.40 (2024-04-25)

### Bug Fixes

- Fixed a bug in the managed-resources kind that caused the integration to throw a KeyError

### Improvements

- Added a default empty array to the deployment history mapping to stop spamming the logs with JQ NoneType error


# Port_Ocean 0.1.39 (2024-04-24)

### Improvements

- Bumped ocean version to ^0.5.14 (#1)


# Port_Ocean 0.1.38 (2024-04-17)

### Improvements

- Bumped ocean version to ^0.5.12 (#1)


# Port_Ocean 0.1.37 (2024-04-11)

### Deprecations
- Added deprecation warnings to the deployment-history and kubernetes-resource kind, urging users to utilize the itemsToParse functionality instead

### Improvements

- Reveresed the relation between cluster and namespace, and other general enhancements on blueprints (PORT-7550)
- Updated the default mapping for deployment-history and kubernetes-resource kind to reuse the application kind's response and parse items using the itemsToParse functionality for improved efficiency


# Port_Ocean 0.1.36 (2024-04-11)

### Improvements

- Bumped ocean version to ^0.5.11 (#1)


# Port_Ocean 0.1.35 (2024-04-10)

### Improvements

- Bumped ocean version to ^0.5.10 (#1)


# Port_Ocean 0.1.34 (2024-04-01)

### Improvements

- Bumped ocean version to ^0.5.9 (#1)


# Port_Ocean 0.1.33 (2024-03-28)

### Improvements

- Bumped ocean version to ^0.5.8 (#1)


# Port_Ocean 0.1.32 (2024-03-21)

### Improvements

- Added support for ArgoCD kubernetes resources (PORT-6911)


# Port_Ocean 0.1.31 (2024-03-20)

### Improvements

- Bumped ocean version to ^0.5.7 (#1)


# Port_Ocean 0.1.30 (2024-03-18)

### Improvements

- Added support for Application managed resources kind


# Port_Ocean 0.1.29 (2024-03-18)

### Improvements

- Enhanced the application blueprint by adding relation to the cluster and two revision properties (actual and target) (PORT-6528)
- Updated the deployment history revision property from string to url, linking the user the specific revision (PORT-6854)
- Added namespace blueprint and created relevant relations(PORT-7187)

# Port_Ocean 0.1.28 (2024-03-17)

### Improvements

- Bumped ocean version to ^0.5.6 (#1)


# Port_Ocean 0.1.27 (2024-03-06)

### Improvements

- Bumped ocean version to ^0.5.5 (#1)


# Port_Ocean 0.1.26 (2024-03-03)

### Improvements

- Bumped ocean version to ^0.5.4 (#1)


# Port_Ocean 0.1.25 (2024-03-03)

### Improvements

- Bumped ocean version to ^0.5.3 (#1)


# Port_Ocean 0.1.24 (2024-02-21)

### Improvements

- Bumped ocean version to ^0.5.2 (#1)


# Port_Ocean 0.1.23 (2024-02-20)

### Improvements

- Bumped ocean version to ^0.5.1 (#1)


# Port_Ocean 0.1.22 (2024-02-18)

### Improvements

- Bumped ocean version to ^0.5.0 (#1)


# Port_Ocean 0.1.21 (2024-01-25)

### Bug Fixes

- Fixed a bug in the pages templates where the page weren't inside a list, causing the parsing of the integration to fail (#1)


# Port_Ocean 0.1.20 (2024-01-23)

### Improvements

- Bumped ocean version to ^0.4.17 (#1)


# Port_Ocean 0.1.19 (2024-01-21)

### Improvements

- Added default page for ArgoCD (PORT-5959)


# Port_Ocean 0.1.18 (2024-01-12)

### Features

- Added support for ArgoCD deployments history (#5704)


# Port_Ocean 0.1.17 (2024-01-11)

### Improvements

- Bumped ocean version to ^0.4.16 (#1)


# Port_Ocean 0.1.16 (2024-01-07)

### Improvements

- Bumped ocean version to ^0.4.15 (#1)


# Port_Ocean 0.1.15 (2024-01-07)

### Improvements

- Bumped ocean version to ^0.4.14 (#1)


# Port_Ocean 0.1.14 (2024-01-01)

### Improvements

- Bumped ocean version to ^0.4.13 (#1)


# Port_Ocean 0.1.13 (2023-12-24)

### Improvements

- Bumped ocean version to ^0.4.12 (#1)


# Port_Ocean 0.1.12 (2023-12-21)

### Improvements

- Bumped ocean version to ^0.4.11 (#1)


# Port_Ocean 0.1.11 (2023-12-21)

### Improvements

- Bumped ocean version to ^0.4.10 (#1)


# Port_Ocean 0.1.10 (2023-12-14)

### Improvements

- Bumped ocean version to ^0.4.8 (#1)


# Port_Ocean 0.1.9 (2023-12-05)

### Improvements

- Bumped ocean version to ^0.4.7 (#1)


# Port_Ocean 0.1.8 (2023-12-04)

### Bug Fixes

- Updated ArgoCD application gitRepo property format from URL to string, allowing for various formats and resolving sync errors with private repositories (#8)


# Port_Ocean 0.1.7 (2023-12-04)

### Improvements

- Bumped ocean version to ^0.4.6 (#1)


# Port_Ocean 0.1.6 (2023-11-30)

### Improvements

- Bumped ocean version to ^0.4.5 (#1)


# Port_Ocean 0.1.5 (2023-11-29)

### Improvements

- Bumped ocean version to ^0.4.4 (#1)
- Changed the httpx client to be the ocean's client for better connection error handling and request retries


# Port_Ocean 0.1.4 (2023-11-21)

### Improvements

- Bumped ocean version to ^0.4.3 (#1)


# Port_Ocean 0.1.3 (2023-11-08)

### Improvements

- Bumped ocean version to ^0.4.2 (#1)


# Port_Ocean 0.1.2 (2023-11-03)

### Improvements

- Bumped ocean version to ^0.4.1 (#1)


# Port_Ocean 0.1.1 (2023-11-01)

### Improvements

- Bumped ocean version to ^0.4.0 (#1)


# 0.1.0 (2023-08-21)

### Features

- Implemented ArgoCD integration
