# Overview
This script uses [Digilent's SDK scripts](https://github.com/Digilent/WaveForms-SDK-Getting-Started-PY/) to control an Analog Discovery 2 purposed as a chloridometer.
The script uses the W1 and W2 waveform channels, and both oscilloscope channels to measure Cl<sup>-</sup> concentration in aqueous solution.

W1 is connected to an [LT3092 programmable current source chip](https://www.analog.com/en/products/lt3092.html) to provide constant current to the generator circuit of the chloridometer.
The anode of the generator circuit is connected to a silver wire to generate Ag<sup>+</sup> ions in the solution.
The generator cathode can be constructed from graphite (pencil lead) and is connected to ground.
Both the silver and graphite electrodes are immersed in the solutionbeing measured.

W2 is connected to a second silver electrode in the indicator circuit, and a third silver electrode is connected to ground.
These silver electrodes are also immersed in the solution to be measured.

Oscilloscope channel 1 is connected across a resistor in series with the generator cathode to measure the current through the generator circuit.

Oscilloscope channel 2 is connected across a resistor in series with the indicator cathode to measure the current through the indicator circuit.

A circuit diagram of the chloridometer circuit can be found [here](./circuit.png).
