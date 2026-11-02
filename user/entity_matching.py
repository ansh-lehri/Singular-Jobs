import csv
import concurrent.futures
import requests
import threading
import time
from collections import defaultdict


def read_csv_as_dict(fileread):

    skills_dict = {}
    
    with requests.get(fileread, stream=True) as r:
        lines = (line.decode('utf-8') for line in r.iter_lines())
        for line in csv.reader(lines):
            skills_dict[line[0]] = line[1]

    return skills_dict



class FileDrivers:
    '''
    afread = open("C://Users//Dell//Desktop//jobbackend//jobapi//users//kill_bases//a-f.csv","r")
    glread = open("C://Users//Dell//Desktop//jobbackend//jobapi//users//skill_bases//g-l.csv","r")
    mrread = open("C://Users//Dell//Desktop//jobbackend//jobapi//users//skill_bases//m-r.csv","r")
    szread = open("C://Users//Dell//Desktop//jobbackend//jobapi//users//skill_bases//s-z.csv","r")
    otherread = open("C://Users//Dell//Desktop//jobbackend//jobapi//users//skill_bases//others.csv","r")
    abbreviations = open("C://Users//Dell//Desktop//jobbackend//jobapi//users//skill_bases//abbreviations.csv",'r')
    grp_parent = open("C://Users//Dell//Desktop//jobbackend//jobapi//users//skill_bases//grp_parent.csv","r")
    '''
    
    def atof(self):
        return "https://raw.githubusercontent.com/ansh-lehri/singularjobs_skills_file_csv/main/a-f.csv"
        
    def gtol(self):
        return "https://raw.githubusercontent.com/ansh-lehri/singularjobs_skills_file_csv/main/g-l.csv"
        
    def mtor(self):
        return "https://raw.githubusercontent.com/ansh-lehri/singularjobs_skills_file_csv/main/m-r.csv"
        
    def stoz(self):
        return "https://raw.githubusercontent.com/ansh-lehri/singularjobs_skills_file_csv/main/s-z.csv"
        
    def otherread(self):
        return "https://raw.githubusercontent.com/ansh-lehri/singularjobs_skills_file_csv/main/others.csv"
        
    def abbreviations(self):
        return "https://raw.githubusercontent.com/ansh-lehri/singularjobs_skills_file_csv/main/abbreviations.csv"
    
    def grp_parent(self):
        return "https://raw.githubusercontent.com/ansh-lehri/singularjobs_skills_file_csv/main/grp_parent.csv"
        
 
filedrivers = FileDrivers()
class EntityMatch:

    def __init__(self):


        # optimization might be possible in way of using abbreviations and grp_parent. Havea thought
        
        
        self.skill_abbre = read_csv_as_dict(filedrivers.abbreviations())
        self.skill_abbre_list = list(self.skill_abbre.keys())
        self.grp_parent = read_csv_as_dict(filedrivers.grp_parent())
        #print(self.skill_abbre)
        #print("::::::::::::::::::::::::::::::::::::::::")
        #print(self.skill_abbre_list)


    def new_string_formation(self,token_list,token_freq):

      new_current=""
      for token in token_list:
        if token_freq[token]!=0:
          new_current+=token
          new_current+=" "
          token_freq[token]

      new_current = new_current.rstrip(" ")
      return new_current


    def expand(self,current):
        
        #print("Ansh")
        current_tokens = current.split(" ")
        expanded_current = ""
        for token in current_tokens:
            if token in self.skill_abbre_list:
                expanded_current += self.skill_abbre[token]
            else:
                expanded_current += token
                expanded_current += " "
        #print(expanded_current)
        return expanded_current


    def edit_distance(self,current,target):

        n = len(current)
        m = len(target)

        # current -> row
        # target -> column

        dp = [[0 for j in range(m+1)] for i in range(n+1)]

        for i in range(n+1):
            for j in range(m+1):
                if i==0:
                    dp[i][j]=j
                elif j==0:
                    dp[i][j]=i
                elif current[i-1]==target[j-1]:
                    dp[i][j] = dp[i-1][j-1]
                else:
                    dp[i][j] = 1+min(dp[i-1][j],min(dp[i][j-1],dp[i-1][j-1]))

        return dp[n][m]/min(n,m)


    def exclude_similar_tokens(self,current,target):
        
        #print("FALSE")
        
        current_tokens = current.split(" ")
        target_tokens = target.split(" ")

        current_tokens_freq = defaultdict(int)
        target_tokens_freq = defaultdict(int)

        for token in current_tokens:
            current_tokens_freq[token]+=1

        for token in target_tokens:
            target_tokens_freq[token]+=1

        current_tokens_dict = dict(current_tokens_freq)
        target_tokens_dict = dict(target_tokens_freq)

        current_unique_tokens_list = list(current_tokens_dict.keys())
        target_unique_tokens_list = list(target_tokens_dict.keys())

        for token in current_tokens:
            if token in current_unique_tokens_list and token in target_unique_tokens_list:
                current_tokens_dict[token]-=1
                target_tokens_dict[token]-=1

        new_current = self.new_string_formation(current_tokens,current_tokens_dict)
        new_target = self.new_string_formation(target_tokens,target_tokens_dict)

        if new_current=="" and new_target=="":
            return 0
        if new_current=="" or new_target=="":
            return 0.4
        return self.edit_distance(new_current,new_target)


    def entity_examine(self,entity):


        #the method can be optimized by using cache memory to store groups of latest y stringsand jsut checking grp part at the end of method.
        # latest x can be used or after some analysis most frequently visited y strings can be used.
        
        entity = entity.lstrip(" ")
        entity = entity.rstrip(" ")
        print("TRUE")
        print(entity)
        if entity[0]>='a' and entity[0]<='f':
            filedriver = filedrivers.atof()
        elif entity[0]>='g' and entity[0]<='l':
            filedriver = filedrivers.gtol()
        elif entity[0]>='m' and entity[0]<='r':
            filedriver = filedrivers.mtor()
        elif entity[0]>='s' and entity[0]<='z':
            filedriver = filedrivers.stoz()
        else:
            filedriver = filedrivers.otherread()
        
        #print(filedriver)
        #filereader = csv.reader(filedriver)
        
        # can be optimized by using cache to store expanded form latest x strings. 
        entity = self.expand(entity)
        print("ENTITY  AFTER  EXPANSION:         ,",entity)
        final_grp = -1
        current_edit_ratio = 10
      
        #print(":::::::::::::::::::     ",entity)
        # optimization possible.
        entity_ratio = []
        with requests.get(filedriver, stream=True) as r:
            lines = (line.decode('utf-8') for line in r.iter_lines())
            for line in csv.reader(lines):

                #print(line)
                if line[1]!="":
                    target_entity = line[1]
                else:
                    target_entity = line[0]
                    #print(target_entity)

                if target_entity[0]>entity[0]:
                    break
                if target_entity[0]!=entity[0]:
                    continue

                edit_ratio = self.exclude_similar_tokens(entity,target_entity)
                #print(edit_ratio)
                if edit_ratio<current_edit_ratio:
                    current_edit_ratio = edit_ratio
                    final_grp = line[2]

                entity_ratio.append((entity,target_entity,edit_ratio))
        # no grp available 
        #print("Final Group:    ",final_grp)
        if final_grp==-1:
            status = "GA"
            parent = entity
        #grp available
        else:
            if self.grp_parent[final_grp]=="":
                status = "GP"+str(final_grp)+"PA"
                parent = entity
            else:
                status = "GP"+str(final_grp)+"PP"
                parent = self.grp_parent[final_grp]


        # for now return only parent. status is property of entity node.
        #print(parent)
        #entity_dict = {"parent":parent.rstrip(" ")}
        #print(entity_dict)
        #print(entity_ratio)
        #print()
        return parent


    def entities_multithread(self,entities):

        start_time =  time.time()
        result_entities = []
        print("??????????????????????????????//////////////////////////////////////////////////////")
        print(entities)
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            future_skills = {executor.submit(self.entity_examine, entity):entity for entity in entities}
            #print(future_skills.result())
            #print(future_skills)
            
            for future in concurrent.futures.as_completed(future_skills):
                #print(future)
                a=future_skills[future]
                #print(future.result())
                result_entities.append(future.result())
            print(result_entities)
        print(time.time()-start_time)
       
        '''
        for entity in entities:
            result_entities.append(self.entity_examine(entity))
        '''
        final_entities = ",".join(entity for entity in result_entities)
        final_entities = final_entities.rstrip(",")
        
        return final_entities
        
      
'''
if __name__=="__main__":

    #center = Center()
    #center.multithread()
    
    #FileDrivers()
    match = EntityMatch()
    
    #match.entities_multithread(['work from home', 'php', 'mysql', 'html', 'css', 'javascript', 'front end coding', 'back-end services', 'front-end', 'maintaining technical documentation', 'web development','front-end'])
    #match.entities_multithread(['ml','nlp','front-end','front-end'])
    match.entities_multithread(['work from home', 'react', 'javascript', 'react.js', 'front-end architecture', 'front-end', 'html', 'css', 'reactjs', 'redux', '×', 'react.js development'])
'''
