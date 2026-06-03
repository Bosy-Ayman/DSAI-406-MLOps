# Assignment 1 

## Reading 

- Read Chapter 3 from the main book 

## Implementation 

**Goal**: Take the script from assignment 1 and make it reproducible.

- Part 1: Conda Environment 
  - Create a clean conda environment specifically for the project named "env_rl_project"
  - Install all necessary libraries
  - Export the requirements to a yaml file 

- Part 2: Containerization. Write a Dockerfile that
  - Starts from a lightweight Python base image.
  - Uses the efficient layering strategy (copy requirements.txt before the rest of the code).
  - Sets the WORKDIR.
  - Defines a CMD to run the training script