MATHEMATICAL OPTIMISATION
prof. Lorenzo Castelli
exam project by
Massimo Trevi and Mike De Petris

Directory contents:

1-s2.0-S0377221722000078-main.pdf
	paper from https://www.sciencedirect.com/science/article/pii/S0377221722000078

Instances\
	directory with all input data files

Logs\
	directory with execution logs

2_input_from_files_as_paper.py
	model that reproduces paper results using the input data files given by paper authors

3_statistics_from_input_files.py
	processor program that parses and produces statistical data about the input data files, to understand frequency distributions and reproduce it to generate new scaled instances with random data

4_scale_random_instances.py
	model that finds optimization solutions for 20 random generated scaled instances

unlucky input.txt
	text file of instances selected from execution logs to investigate the model implementation behaviour with instances that give the worst optimal solutions

5_unlucky_files_create.py
	processor that creates input data files from "unlucky input.txt"

6_unlucky_case.py
	model that finds optimization solutions for the selected instances

7_scale_extended.py
	extended model that implements a new formulation with some hypothesis that keep in consideration the size of the goods to transport

