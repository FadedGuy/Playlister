# video2audio

## Description
This is a microservices application that converts video files to audio files. It is written in Python and some of the modules it uses are Flask, MySQL, MongoDB, GridFS.
It uses Docker to create the containers and Kubernetes to orchestrate the whole thing.

## Notes
Tested locally using minikube with two main caveats.
* Used minikube tunnel to simulate sending request to mp3converter and rabbitmq by modifying /etc/hosts


