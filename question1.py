#!/usr/bin/env python3
import os
import subprocess
import shutil
import re

#set the working directory
current_dir = "/home/s2647596/final_exam"
os.chdir(current_dir)

'''The research lab works on the Plasmodium parasite, and they are particularly
interested in Plasmodium simium, a malaria parasite of non-human primates in the
Atlantic forest region of Brazil that was recently shown to cause zoonotic infection in
humans in the region.
The first thing that your new boss/employer will want you to do, as soon as you start,
is “write a Python3 programme that will enable us to run BLAST analyses of
whatever we want without using a browser”'''

#obtain the fasta file first
species_name = "Plasmodium simium"
def fasta_request(species_name, type):
    esearch_request = f"esearch -db {type} -query '{species_name}[organism]'"
    efetch_request = "efetch -format fasta"
    short_name = species_name[0:3]
    try:
        fa_result = subprocess.check_output(f"{esearch_request} | {efetch_request}", shell=True).decode("utf-8")
    except Exception as e:
        print("fail to obtain fasta file")
        print(e)
    finally:
        #save the result into a file
        with open(f"{short_name}_{type}.fasta", mode="w") as f:
            f.write(fa_result)

#can obtain the nucleotide sequence and the protein sequence
fasta_request(species_name, "nucleotide")
fasta_request(species_name, "protein")

#create the database
def create_database(species_name, type):
    short_name = species_name[0:3]
    dbtype = type[:4]
    db_name = f"{short_name}_{type}"
    request = f"makeblastdb -in {short_name}_{type}.fasta -dbtype {dbtype} -out {db_name}"
    try:
        subprocess.call(request, shell=True)
    except Exception as e:
        print("fail to create the database")
        print(e)

create_database(species_name, "nucleotide")
create_database(species_name, "protein")

# blast
def blast_request(species_name, db_type, query_file_dir):
    short_name = species_name[0:3]
    db_name = f"{short_name}_{db_type}"
    #need to identify the query type first
    with open(query_file_dir, mode="r") as f:
        lines = f.readlines()
        for line in lines:
            line = line.strip()
            if not line.startswith(">"):
                reg = r"[ATCG]"
                result_list = re.findall(reg,line.upper())
                if len(result_list) > 5:
                    #query_type is "nucleotide"
                    #set blast type
                    if db_type == "nucleotide":
                        blast_type = "blastn"
                    else:
                        blast_type="blastx"
                else:
                    #query_type = "protein"
                    if db_type == "nucleotide":
                        blast_type = "tblastn"
                    else:
                        blast_type = "blastp"
            else:
                #obtain the accession number of this query sequence from the header
                acc = line.split(" ")[0]
                acc = acc[1:]

    #blasting
    try:
        blast_query = f"{blast_type} -db {db_name} -query {query_file_dir} -outfmt 7 > {acc}_{blast_type}.out"
        subprocess.call(blast_query, shell=True)       
    except Exception as e:
        print("blasting is fail")
        print(e) 

        
#test
#blast_request(species_name, "nucleotide", "./query_nucleotide.fasta")

#user interaction
i = 0
while True:
    #obtain the database type
    db_type = input("what type of database you want to use? nucleotide or protein?")
    db_type = db_type.lower()
    if db_type.startswith("nucl"):
        db_type = "nucleotide"
        break
    elif db_type.startswith("prot"):
        db_type = "protein"
        break
    else:
        print("please enter the correct database type!")
        i += 1
    if i >=3:
        print("reach three attempts limit, exit from the program")
        exit(1)

i = 0
while True:
    #obtain the query file directory
    query_dir = input("please enter the directory of query file")
    if not os.path.exists(query_dir):
        print("please provide the corrent directory of query file")
        i += 1
    else:
        break
    if i >= 3:
        print("reach three attempts limit, exit from the program")
        exit(1)

blast_request(species_name, db_type, query_dir)