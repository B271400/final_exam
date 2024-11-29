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
    db_name = {short_name}_{type}
    request = f"makeblastdb -in {short_name}_{type}.fasta -dbtype {dbtype} -out {db_name}"
    try:
        subprocess.call(request, shell=True)
        return db_name
    except Exception as e:
        print("fail to create the database")
        print(e)

nucl_db_name = create_database(species_name, "nucleotide")
prot_db_name = create_database(species_name, "protein")

# blast
def blast_request(db_name, db_type, query_file_dir):
    if os.path.exists(query_file_dir):
        #need to identify the query type first
        with open(query_file_dir, mode="r") as f:
            lines = f.readlines().rstrip()
            for line in lines:
                if line.startwith(">") == -1:
                    reg = r"[ATCG]"
                    result_list = re.findall(reg,line.upper())
                    if len(result_list) > 5:
                        query_type = "nucleotide"
                    else:
                        query_type = "protein"
        #different query and database type use different blast
        if db_type == "nucleotide":
            if query_type == "nucleotide":
                blast_type = "blastn"
            else:
                blast_type = "tblastn"
        elif db_type == "protein":
            if query_type == "nucleotide":
                blast_type = "blastx"
            else:
                blast_type= "blastp"

        #blasting
        try:
            blast_query = f"{blast_type} -db {db_name} -query {query_file_dir} -outfmt 7 > {blast_type}.out"
            subprocess.call(blast_query)       
        except Exception as e:
            print("blasting is fail")
            print(e) 
    else:
        print("please provide the corrent directory of query file")

