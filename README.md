# Continuous Quality Evaliation of ML models

In this repo one can find all the necessary code and tools to build a continuous quality evaluation system using CI/CD engine of GitHub Actions.

There is a **[blog post](https://medium.com/@vovacher/continuous-quality-evaluation-for-ml-projects-using-github-actions-78f2f078e38f)** which covers all the concepts and ideas behind the system. The post also contains step-by-step tutorial and instructions on how to use this system and what the components are.

This README contains:
* Technical details to make the launch easier
* High-level overview of the structure

## Launch

The system is tested on Ubuntu 18.04 and Mac OSX 10.15.2.

All interaction with the system is done via [Makefile](./Makefile). Thus one should have `make` installed. All the code is run using [Docker containers](https://www.docker.com) which should be installed on the host machine.

Instructions for Ubuntu and OSX are below. For Windows, the system might also work but is not tested and I can not guarantee it.

* **Ubuntu**
  * Install make command-line tool
  ```sh
  apt-get update
  apt-get install build-essential
  ```

  * Setup Docker
  
    The most recent installation instructions for Ubuntu can be found [here](https://docs.docker.com/install/linux/docker-ce/ubuntu/). For the convenience purposes I would also recommend to enable docker management for non-root users (see [here](https://docs.docker.com/install/linux/linux-postinstall/)). Be careful because it can lead to possible security issues.

* **Mac OS X**
  * Install `make` command-line tool
  
    It is shipped in the set of command-line tools for XCode (see instructions [here](https://stackoverflow.com/a/11494872/7196628)).

  * Setup Docker
  
    The most recent installation instructions for Mac OS X can be found [here](https://docs.docker.com/docker-for-mac/install/).

  * Install some of the missing command-line utils
  
  ```sh
  brew install coreutils
  ```
  
  * **Adapt `Makefile`**
  
  Change "date" command to "gdate" command in line 13 of Makefile ([here](https://github.com/vladimir-chernykh/ml-quality-cicd/blob/master/Makefile#L13)). It allows Mac users to get UNIX timestamp with the milliseconds tolerance (which is not available with the default "date").
