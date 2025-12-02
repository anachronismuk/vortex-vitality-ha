# vortex-vitality-ha
A docker container to bridge vortex vitality plant health probes and mqtt for home assistant


This container uses [mqtt](https://github.com/mqtt) to send information from Vortex [Vitality plant sensors](https://vortexvitality.uk).


Tested against a docker hosted [mosquitto broker](https://github.com/eclipse-mosquitto/mosquitto). To use, configure the `docker-compose.yml` to match your environment. You will need to generate an API key (from the vplants app Profile->Vprobe API).

You will also need to grab your probe serial numbers. They are added as a comma delimted list, dropping off the `Vprobe-SN` and any leading zeros. So `Vprobe-SN00000123` would be added as `123`.

The `VV_PROBE_FREQUENCY` variable should be set to how frequently you probe the API. If set to a value of less than 600 (ten minutes), this value will be ignored, a minimum of 10 minute polling being enforced.

Once you have configured the `docker_compose.yml` file for your environment, running `docker compose up -d` should be all that's needed to start the container.

API docs for the probe: https://vortexvitality.uk/smart-home-automation/rest-api/

Disclaimer: I do not work for, or represent Vortex Vitality in any way, I'm just a fan of their product. This is provided as is, in the hope that it may be useful to others, it's my first MQTT/HA program, so it is an ugly child - feel free to customise as required for your environment
