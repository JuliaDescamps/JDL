#!/usr/bin/env python
# coding: utf-8

# import panda (and other useful packages)
import os
import pandas as pd
import numpy as np
import random 
import matplotlib.pyplot as plt
import math
import unicodedata
import re
from jdl.settings import BASE_DIR
from collections import Counter

DIR_CSV = os.path.join(BASE_DIR, 'jdl_web', 'jdl_core', 'csv')
DIR_PREF = os.path.join(DIR_CSV, "pref")
DIR_PRETIRET = os.path.join(DIR_CSV, "pretiret")
DIR_SUF = os.path.join(DIR_CSV, "suf")
DIR_SUFTIRET = os.path.join(DIR_CSV, "suftiret")
DIR_MILTIRET = os.path.join(DIR_CSV, "miltiret")
DIR_LISTORDON = os.path.join(DIR_CSV, "listordon")


# # Import des données


data_final= pd.read_csv(os.path.join(DIR_CSV, 'data_final.csv'), sep = ";")
# data_final


dic = {}
for (_,row) in data_final.iterrows():
    if row["Région"] in dic:
        dic[row["Région"]].add(row["CODE_DEPT"])
    else:
        dic[row["Région"]] = set()
    dic["Ile-de-France"] = {"77", "78", "91", "92", "93", "94", "95"}
# dic


# # Création de variables

data_final["pop_niv"] = pd.cut(data_final['POPULATION'], bins=[0, 200, 1000, 20000, 100000, np.inf])
# je crée des catégories de tailles de villes

# print(data_final["pop_niv"])

# data_final["pop_niv"].value_counts()
# Tri à plat de la variable discrète

data_final["taille_pop"] = pd.Series(data_final['POPULATION'].astype(str))


# # Définition des fonctions de base

def slugify(value, allow_unicode=False):
    """
    Taken from https://github.com/django/django/blob/master/django/utils/text.py
    Convert to ASCII if 'allow_unicode' is False. Convert spaces or repeated
    dashes to single dashes. Remove characters that aren't alphanumerics,
    underscores, or hyphens. Convert to lowercase. Also strip leading and
    trailing whitespace, dashes, and underscores.
    """
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize('NFKC', value)
    else:
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value.lower())
    return re.sub(r'[-\s]+', '-', value).strip('-_')


##### Fonction qui fait l'extraction de la base de région à partir de la base initiale
def extract(x):
    data0 = data_final[data_final["Région"] == x]
    data1 = data0[data0["NOM_DEPT"] != "PARIS"]
    data2 = data1[data1["NOM_COM"].apply(lambda x: not x.startswith("MARSEILLE-"))]
    data3 = data2[data2["NOM_COM"].apply(lambda x: not x.startswith("LYON-"))]
    return(data3)

##### Fonction qui fait l'extraction de la base de taille à partir de la base initiale
def extractpop(x, data):
    data0 = data[data["pop_niv"] == x]
    return(data0)

##### Fonction qui fait l'extraction de la base de départements à partir de la base initiale
def extractdep(x):
    data0 = data_final[data_final["CODE_DEPT"] == x]
    data1 = data0[data0["NOM_DEPT"] != "PARIS"]
    data2 = data1[data1["NOM_COM"].apply(lambda x: not x.startswith("MARSEILLE-"))]
    data3 = data2[data2["NOM_COM"].apply(lambda x: not x.startswith("LYON-"))]
    return(data3)


##### Fonction qui extrait une colonne du dataframe sous forme de liste
def convliste(dataframe, colonne):   
    # Je convertis la colonne des noms de communes en matrice
    matrice = np.array(dataframe[colonne])
    # puis je convertis la matrice en liste
    liste_r = list(matrice)
    ## Je supprime les villes qui sont plusieurs fois
    #liste_r = [] 
    #for i in liste : 
    #    if i not in liste_r: 
    #        liste_r.append(i) 
    return(liste_r)

##### Fonction qui trie dans 2 listes les villes avec tirets et sans tirets
def tri_tiret(liste):
    data_tiret = []
    data_entier = []
    boule = 0
    for ville in liste:
        taille = len(ville)
        for i in range(taille):
            if ville[i] == "-":
                boule = boule +1    
        if boule > 0:
            data_tiret.append(ville)
        else:
            data_entier.append(ville)
        boule = 0
    return(data_tiret, data_entier)


##### Fonction préfixes 
def prefixe(liste):
    prelist=[]  # On crée une liste vide dans laquelle on met les préfixes générés
    NREPL = 8 # On définit un nombre de caractère max pour le préfixe
    for l in liste:
        for i in range(3,NREPL):
            p = l[0:i]
            prelist.append(p)
    return(prelist)


##### Fonction suffixes
def suffixe(liste):
    suflist=[]  # On crée une liste vide dans laquelle on met les suffixes générés
    NREPL = 8 # On définit un nombre de caractère max pour le préfixe
    for l in liste:
        for i in range(3,NREPL):
            p = l[-i:]
            suflist.append(p)
    return(suflist)


##### Fonctions de purification
### 1 ###
## Je retire de la liste de suffixes les suffixes qui
    # - sont un sous-suffixes d'un suffixe
    # - ne sont pas eux-mêmes
    # - ont une fréquence d'occurrence négligeable par rapport à leur sur-suffixe
def purif(liste):
    list_r = []
    remove = 0
    for x in liste:
        for x2 in liste:
            if x2.startswith(x) and len(x) != len(x2) and liste.count(x) <  1.5*liste.count(x2):
                remove = 1
        if remove == 0:
            list_r.append(x)
        remove = 0
    return(list_r)

### 2 ###
## Je cherche à privilégier les préfixes qui sont gros mais qui apparaissent un peu moins souvent par rapport à des préfixes qui sont petits mais très fréquents
## (taille*effectif) => privilégie les préfixes longs qui apparaissent peu 
## On compare ça à l'effectif moyen pour s'avoir si on le garde ou pas. Si <, on le vire

def sdc(x):
    res = []
    # remove = 0
    for c in x:
        if len(c[0])*c[1] > 15*eff_moy(x):
            res.append(c)
    return(res)


##### Fonctions de calcul
## Je compte les occurrences de chaque élément d'une liste
def compt(liste):
    couples = Counter(liste).most_common()
    return(couples)

## Je calcule l'effectif moyen de l'occurrence des éléments d'une liste
def eff_moy(x):
    res = 0
    somme = 0
    for c in x:
        somme = somme + c[1]
    res = somme / len(x)
    return(res)


##### Fonction de composition
def compo(liste1, liste2):
    res = []
    while len(res) < 1000:
        res.append(random.choice(liste1)+random.choice(liste2))
    return(res)


##### Fonctions de purification bis
## Fonction qui prend toutes les sous-chaînes de taille 3 dans une chaîne
def sous_chaine(s): 
    res = []
    for i in range(len(s) -2):
        res.append(s[i: i+3])
    return res

## Fonction qui décide si une chaîne de 3 caractères est dans la liste de villes de départ
# Assert : on s'assure que la chaîne de caractère qu'on met dans la fonction est bien de 3 caractères
def realiste(s, liste_r):
    assert len(s) == 3
    res2 = 0
    for i in liste_r:
        if s in i:
            res2 = 1
    return res2 

## Fonction qui décide si je garde la ville ou pas
# Si je trouve une sous-chaîne de 3 caractères qui n'apparaît pas dans la ville de départ, je ne garde pas la ville
# Il faut passer à la négative car c'est plus compliqué de vérifier que toutes les sous-chaînes apparaissent, plutôt que de vérifier s'il y en a une qui n'apparaît pas
def keep(v, liste_r):
    res3 = 1
    for i in sous_chaine(v):
        if realiste(i, liste_r) == 0:
            res3 = 0
    return res3

## Fonction qui crée la liste finale de fragments inventés
def puriffinal(liste, liste_r):
    res = []
    for v in liste:
        if keep(v, liste_r) == 1:
            res.append(v)
    return(res)

##### Fonction qui vérifie si un élément n'est pas déjà dans une liste
def control(x, liste):
    res = 0
    if x in liste:
        res = 1
    return(res)

## Fonction qui supprime de la liste des noms existants
def pertinent(liste, liste_r):
    res = []
    for v in liste:
        if control(v, liste_r) == 0:
            res.append(v)
    return(res)


##### Fonctions pour les noms composés
## Extraction de toutes les sous-chaînes qui commencent au début et qui finissent par "-" et toutes les sous-chaînes qui commencent par un "-" et qui terminent par "-"
## Débuts
def tiret_debut(v):
    res = []
    for i in range(len(v)) :
        for j in range(i + 1, len(v)):
            if i == 0 and v[j] == "-":
                res.append(v[i:j+1])
    return(res)

## Milieux
def tiret_milieu(v):
    res = []
    for i in range(len(v)) :
        for j in range(i + 1, len(v)):
            if v[i] == "-" and v[j] == "-":
                res.append(v[i:j+1])
                res.append(v[i:j+1])
    return(res)

## Fins
def tiret_fin(v):
    res = []
    for i in range(len(v)) :
        for j in range(i + 1, len(v)):
            if v[i] == "-" and j == len(v) - 1:
                res.append(v[i:j+1])
    return(res)

## Fonction qui récupère tous les éléments avec tirets d'une liste
def separtiret(liste):
    bouts_tirets_debut = []
    bouts_tirets_milieu = []
    bouts_tirets_fin = []
    for v in liste:
        bouts_tirets_debut = bouts_tirets_debut + tiret_debut(v)
        bouts_tirets_milieu = bouts_tirets_milieu + tiret_milieu(v)
        bouts_tirets_fin = bouts_tirets_fin + tiret_fin(v)
    return(bouts_tirets_debut, bouts_tirets_milieu, bouts_tirets_fin)


## Fonction qui purifie la liste comme on l'avait fait pour les villes : en supprimant les éléments qui sont inclus les uns dans les autres
def puriftirets(x):
    res = []
    remove = 0
    for mot in x:
        for mot2 in x:
            if mot in mot2 and len(mot) != len(mot2) and x.count(mot) <  4*x.count(mot2):
                    remove = 1
        if remove == 0:
            res.append(mot)
        remove = 0
    return(res)

## Je cherche à privilégier les préfixes qui sont gros mais qui apparaissent un peu moins souvent par rapport à des préfixes qui sont petits mais très fréquents
## (taille*effectif) => privilégie les préfixes longs qui apparaissent peu 
## On compare ça à l'effectif moyen pour s'avoir si on le garde ou pas. Si <, on le vire
def sdc_tiret(x):
    res = []
    for c in x:
        if c[1] > 3*eff_moy(x):
            res.append(c)
    return(res)


##### Fonctions de statistiques sur les villes avec tirets
## Proportion de villes avec au moins 1 tiret
def tiret_compt(liste):
    res = 0
    for element in liste :
        for i in range(len(element)):
            if element[i] == "-":
                res = res + 1
                break
    return(res)

def freq_tiret(liste):
    res = tiret_compt(liste)/len(liste)
    return(res)

def eff_tiret(liste):
    res = tiret_compt(liste)
    return(res)


## Proportion de villes avec un préfixe composé
def untiret_compt(liste):
    res = 0
    for element in liste :
        for i in range(len(element)):
            if element[i] == "-":
                res = res + 1
                return(res)
            
def freq_untiret(liste):
    res = untiret_compt(liste)/len(liste)
    return(res)

## Proportion de villes avec deux tirets ou plus
def deuxtirets_compt(liste):
    res = 0
    for element in liste :
        for i in range(len(element)):
            if element[i] == "-":
                res = res + 1
                break
    res = res - untiret_compt(liste)
    return(res)

def freq_deuxtirets(liste):
    res = deuxtirets_compt(liste)/len(liste)
    return(res)

## Fonction d'ajout de tirets
def ajout_tiret(liste, x):
    prop1 = freq_untiret(list(data_final[data_final["Région"] == x]["NOM_COM"]))
    prop2 = freq_deuxtirets(list(data_final[data_final["Région"] == x]["NOM_COM"]))
    liste_final = set()
    for i in range(10):
        alea = random.random()
        # Débuts
        if alea < prop1/2 :
            v = random.choice(sdc_tiret(tirets_couples_debut))[0]+random.choice(liste)
            liste_final.add(v)
        # Fins
        if prop1/2 < alea < prop2/2 + prop1/2:
            v = random.choice(liste)+random.choice(sdc_tiret(tirets_couples_fin))[0]
            liste_final.add(v)
        # Milieux
        if prop2/2 + prop1/2 < alea < prop2 + prop1/2  :
            v = random.choice(liste)+random.choice(sdc_tiret(tirets_couples_milieu))[0]+random.choice(liste)
            liste_final.add(v)
        # Compositions
        if prop2 + prop1/2 < alea < prop1 + prop2:
            v = random.choice(liste)+"-"+random.choice(liste)
            liste_final.add(v)
        if alea > prop1 + prop2:
            v = random.choice(liste)
            liste_final.add(v) 
    return(liste_final)


##### Fonction qui donne la région d'appartenance de la ville
def region(x):
    region = []
    if homonyme(x) == 0:
        region = data_final[data_final["NOM_COM"] == x]["Région"].iloc[0]
    if homonyme(x) == 1:
        region = "Précisez le numéro du département"
    return(region)


##### Fonction qui donne la région agrégée d'appartenance de la ville (réforme des régions)
def refregion(x):
    region = []
    region = data_final[data_final["NOM_COM"] == x]["NOM_REG"].iloc[0]
    return(region)

##### Fonction qui donne la région d'appartenance du département
def region2(x):
    region = data_final[data_final["CODE_DEPT"] == x]["Région"].iloc[0]
    return(region)


##### Fonction qui donne le département d'appartenance de la ville
def dept(x):
    dept = []
    dept = data_final[data_final["NOM_COM"] == x]["NOM_DEPT"].iloc[0]
    return(dept)

##### Fonction qui donne le code du département d'appartenance de la ville
def codedept(x):
    dept = []
    dept = data_final[data_final["NOM_COM"] == x]["CODE_DEPT"].iloc[0]
    return(dept)


##### Fonction qui donne la taille de la ville
def taille(x):
    res = data_final[data_final["NOM_COM"] == x]["taille_pop"].iloc[0]
    t = str(res)
    return(res)

##### Fonction qui donne la taille de la ville si homonyme
def taille_h(x, y) -> int : 
    if y == "13" and x == "MARSEILLE":
        res = 861635
    elif y == "69" and x == "LYON":
        res = 513275
    else:
        data = extractdep(y)
        res = data[data["NOM_COM"] == x]["taille_pop"].iloc[0]

    return(res)

##### Fonction qui dit si un élément apparaît une autre fois dans une liste
def homonyme(x):
    return convliste(data_final, "NOM_COM").count(x) > 1

#### Fonction qui dit si une ville n'est pas dans le département
def absurde(x, y):
    data = extractdep(y)
    listeville = convliste(data, "NOM_COM")
    return not x in listeville 

##### Fonctions d'extraction en fichiers csv
def export_pref(liste, name):
    name = slugify(name)
    df = pd.DataFrame(liste, columns=["prefixe"])
    df.to_csv( os.path.join(DIR_PREF, f'{name}.csv'), index=False)
    return

def import_pref(name):
    name = slugify(name)
    df = pd.read_csv(os.path.join(DIR_PREF, f'{name}.csv'), sep = ";")
    lp = convliste(df, "prefixe")
    return(lp)

def export_suf(liste, name):
    name = slugify(name)
    df = pd.DataFrame(liste, columns=["suffixe"])
    df.to_csv(os.path.join(DIR_SUF, f'{name}.csv'), index=False)
    return

def import_suf(name):
    name = slugify(name)
    df = pd.read_csv(os.path.join(DIR_SUF, f'{name}.csv'), sep = ";")
    lp = convliste(df, "suffixe")
    return(lp)

def export_pretiret(liste, name):
    name = slugify(name)
    df = pd.DataFrame(liste, columns=["pretiret"])
    df.to_csv(os.path.join(DIR_PRETIRET, f'{name}.csv'), index=False)
    return

def import_pretiret(name):
    name = slugify(name)
    df = pd.read_csv(os.path.join(DIR_PRETIRET, f'{name}.csv'), sep = ";")
    lp = convliste(df, "pretiret")
    return(lp)

def export_suftiret(liste, name):
    name = slugify(name)
    df = pd.DataFrame(liste, columns=["suftiret"])
    df.to_csv(os.path.join(DIR_SUFTIRET, f'{name}.csv'), index=False)
    return

def import_suftiret(name):
    name = slugify(name)
    df = pd.read_csv(os.path.join(DIR_SUFTIRET, f'{name}.csv'), sep = ";")
    lp = convliste(df, "suftiret")
    return(lp)

def export_miltiret(liste, name):
    name = slugify(name)
    df = pd.DataFrame(liste, columns=["miltiret"])
    df.to_csv(os.path.join(DIR_MILTIRET, f'{name}.csv'), index=False)
    return

def import_miltiret(name):
    name = slugify(name)
    df = pd.read_csv(os.path.join(DIR_MILTIRET, f'{name}.csv'), sep = ";")
    lp = convliste(df, "miltiret")
    return(lp)

def export_listordon(liste, name):
    name = slugify(name)
    df = pd.DataFrame(liste, columns=["liste"])
    df.to_csv(os.path.join(DIR_LISTORDON, f'{name}.csv'), index=False)
    return

def import_listordon(name):
    name = slugify(name)
    df = pd.read_csv(os.path.join(DIR_LISTORDON, f'{name}.csv'), sep = ";")
    lp = convliste(df, "liste")
    return(lp)

# # Extraction

# ### Fonction d'extraction en csv des listes de préfixes et suffixes propres à chaque région

def jdlpref(x):
    def supra_fonction(x):
        ## Je crée la base de région
        data_region = extract(x)
        # Je convertis la colonne des noms de communes en matrice
        liste_r = convliste(data_region, "NOM_COM")
        return(liste_r)   
    
    liste_r = supra_fonction(x)
    ## Je mets à part les villes avec les tirets
    data_tiret = tri_tiret(liste_r)[0]
    data_entier = tri_tiret(liste_r)[1]


    ############ Villes sans tirets : création des préfixes ############
    prelist = prefixe(data_entier)
    prelist_r = purif(prelist)
    pre_couples = compt(prelist_r)
    prelist_r2 = map(lambda x : x[0], sdc(pre_couples))
    prelist_r2 = list(prelist_r2)
    return(prelist_r2)

def jdlsuf(x):
    def supra_fonction(x):
        ## Je crée la base de région
        data_region = extract(x)
        # Je convertis la colonne des noms de communes en matrice
        liste_r = convliste(data_region, "NOM_COM")
        return(liste_r)   
    
    liste_r = supra_fonction(x)
    ## Je mets à part les villes avec les tirets
    data_tiret = tri_tiret(liste_r)[0]
    data_entier = tri_tiret(liste_r)[1]


    ############ Villes sans tirets : création des préfixes ############
    suflist = suffixe(data_entier)
    suflist_r = purif(suflist)
    suf_couples = compt(suflist_r)
    suflist_r2 = map(lambda x : x[0], sdc(suf_couples))
    suflist_r2 = list(suflist_r2)
    return(suflist_r2)


def jdlpretiret(x):
    def supra_fonction(x):
        ## Je crée la base de région
        data_region = extract(x)
        # Je convertis la colonne des noms de communes en matrice
        liste_r = convliste(data_region, "NOM_COM")
        return(liste_r)   
    
    liste_r = supra_fonction(x)
    ## Je mets à part les villes avec les tirets
    data_tiret = tri_tiret(liste_r)[0]
    data_entier = tri_tiret(liste_r)[1]


    ############ Villes avec tirets : création des préfixes ############
    bouts_tirets_debut = separtiret(data_tiret)[0] 
    bouts_tirets_debut_r = puriftirets(bouts_tirets_debut)
    tirets_couples_debut = compt(bouts_tirets_debut_r)
    tirets_couples_debut_r = map(lambda x : x[0], sdc_tiret(tirets_couples_debut))
    tirets_couples_debut_r = list(tirets_couples_debut_r)
    return(tirets_couples_debut_r)

def jdlsuftiret(x):
    def supra_fonction(x):
        ## Je crée la base de région
        data_region = extract(x)
        # Je convertis la colonne des noms de communes en matrice
        liste_r = convliste(data_region, "NOM_COM")
        return(liste_r)   
    
    liste_r = supra_fonction(x)
    ## Je mets à part les villes avec les tirets
    data_tiret = tri_tiret(liste_r)[0]
    data_entier = tri_tiret(liste_r)[1]


    ############ Villes avec tirets : création des préfixes ############
    bouts_tirets_fin = separtiret(data_tiret)[2] 
    bouts_tirets_fin_r = puriftirets(bouts_tirets_fin)
    tirets_couples_fin = compt(bouts_tirets_fin_r)
    tirets_couples_fin_r = map(lambda x : x[0], sdc_tiret(tirets_couples_fin))
    tirets_couples_fin_r = list(tirets_couples_fin_r)
    return(tirets_couples_fin_r)

def jdlmiltiret(x):
    def supra_fonction(x):
        ## Je crée la base de région
        data_region = extract(x)
        # Je convertis la colonne des noms de communes en matrice
        liste_r = convliste(data_region, "NOM_COM")
        return(liste_r)   
    
    liste_r = supra_fonction(x)
    ## Je mets à part les villes avec les tirets
    data_tiret = tri_tiret(liste_r)[0]
    data_entier = tri_tiret(liste_r)[1]


    ############ Villes avec tirets : création des préfixes ############
    bouts_tirets_mil = separtiret(data_tiret)[1] 
    bouts_tirets_mil_r = puriftirets(bouts_tirets_mil)
    tirets_couples_mil = compt(bouts_tirets_mil_r)
    tirets_couples_mil_r = map(lambda x : x[0], sdc_tiret(tirets_couples_mil))
    tirets_couples_mil_r = list(tirets_couples_mil_r)
    return(tirets_couples_mil_r)

# jdlpref("Ile-de-France")
# jdlsuf("Ile-de-France")
# jdlsuftiret("Ile-de-France")
# jdlmiltiret("Ile-de-France")


# ### Fonction d'extraction des listes de préfixes et suffixes propres à chaque département




def jdlsufdep(x):
    def supra_fonction(x):
        ## Je crée la base de région
        data = extractdep(x)
        # Je convertis la colonne des noms de communes en matrice
        liste_r = convliste(data, "NOM_COM")
        return(liste_r)   
    
    liste_r = supra_fonction(x)
    ## Je mets à part les villes avec les tirets
    data_tiret = tri_tiret(liste_r)[0]
    data_entier = tri_tiret(liste_r)[1]


    ############ Villes sans tirets : création des suffixes ############
    suflist = suffixe(data_entier)
    suflist_r = purif(suflist)
    suf_couples = compt(suflist_r)
    suflist_r2 = map(lambda x : x[0], sdc(suf_couples))
    suflist_r2 = list(suflist_r2)
    return(suflist_r2)


def jdlpretiretdep(x):
    def supra_fonction(x):
        ## Je crée la base de région
        data = extractdep(x)
        # Je convertis la colonne des noms de communes en matrice
        liste_r = convliste(data, "NOM_COM")
        return(liste_r)   
    
    liste_r = supra_fonction(x)
    ## Je mets à part les villes avec les tirets
    data_tiret = tri_tiret(liste_r)[0]
    data_entier = tri_tiret(liste_r)[1]


    ############ Villes avec tirets : création des préfixes ############
    bouts_tirets_debut = separtiret(data_tiret)[0] 
    bouts_tirets_debut_r = puriftirets(bouts_tirets_debut)
    tirets_couples_debut = compt(bouts_tirets_debut_r)
    tirets_couples_debut_r = map(lambda x : x[0], sdc_tiret(tirets_couples_debut))
    tirets_couples_debut_r = list(tirets_couples_debut_r)
    return(tirets_couples_debut_r)

def jdlsuftiretdep(x):
    def supra_fonction(x):
        ## Je crée la base de région
        data = extractdep(x)
        # Je convertis la colonne des noms de communes en matrice
        liste_r = convliste(data, "NOM_COM")
        return(liste_r)   
    
    liste_r = supra_fonction(x)
    ## Je mets à part les villes avec les tirets
    data_tiret = tri_tiret(liste_r)[0]
    data_entier = tri_tiret(liste_r)[1]


    ############ Villes avec tirets : création des suffixes ############
    bouts_tirets_fin = separtiret(data_tiret)[2] 
    bouts_tirets_fin_r = puriftirets(bouts_tirets_fin)
    tirets_couples_fin = compt(bouts_tirets_fin_r)
    tirets_couples_fin_r = map(lambda x : x[0], sdc_tiret(tirets_couples_fin))
    tirets_couples_fin_r = list(tirets_couples_fin_r)
    return(tirets_couples_fin_r)

def jdlmiltiretdep(x):
    def supra_fonction(x):
        ## Je crée la base de région
        data = extractdep(x)
        # Je convertis la colonne des noms de communes en matrice
        liste_r = convliste(data, "NOM_COM")
        return(liste_r)   
    
    liste_r = supra_fonction(x)
    ## Je mets à part les villes avec les tirets
    data_tiret = tri_tiret(liste_r)[0]
    data_entier = tri_tiret(liste_r)[1]


    ############ Villes avec tirets : création des préfixes ############
    bouts_tirets_mil = separtiret(data_tiret)[1] 
    bouts_tirets_mil_r = puriftirets(bouts_tirets_mil)
    tirets_couples_mil = compt(bouts_tirets_mil_r)
    tirets_couples_mil_r = map(lambda x : x[0], sdc_tiret(tirets_couples_mil))
    tirets_couples_mil_r = list(tirets_couples_mil_r)
    return(tirets_couples_mil_r)


def realiste_tiret(x, y):
    # x est la région
    # y est le département
    liste = []
    res = set(jdlsuftiret(x))
    for i in dic[x]:
        res = res - set(jdlsuftiretdep(i)) 
        liste = list(res) + jdlsuftiretdep(y)
    return(liste)


               #
             #   #
               #

## Les listes de préfixes, suffixes, et de composés sont ensuite exportés et stockés dans des fichiers .csv à part
## Les préfixes et suffixes ne sont pas re-générés à chaque fois : l'algorithme va piocher dans ces fichiers de manière aléatoire
## Cela dans l'unique but d'optimiser la rapidité de la sortie finale
            
               #
             #   #
               #




# # Définition de la super-fonction


def super_fonction(x, dep, n=10):
    # x est la région
    # dep est le département
    ville_final = []
    def supra_fonction(x):
        ## Je crée la base
        data = extract(x)
        # Je convertis la colonne des noms de communes en matrice
        liste_r = convliste(data, "NOM_COM")
        return(liste_r)
    
    liste_r = supra_fonction(x)
    ## Je mets à part les villes avec les tirets
    data_tiret = tri_tiret(liste_r)[0]
    data_entier = tri_tiret(liste_r)[1]

    ############ Composition ############
    ville_entier = compo(import_pref(f"pref_{x}"), import_suf(f"suf_{x}"))
    ville_entier_r = puriffinal(ville_entier, liste_r)
    ville_entier_r = pertinent(ville_entier_r, liste_r)
    
    return(ville_entier_r)

# # Fonction finale JDL

# In[20]:


def jdl2(x, y):
    if y not in ["2A", "2B"] and int(y) >= 97:
        res = "Désolée, JDL ne traite pas les villes d'Outre-mer :("
        return {'err': res}
    if (x,y) in [('PARIS', "75"), ('MARSEILLE', "13"), ('LYON', "69")] or (not absurde(x, y)):
        if y == "75":
            res = "As-tu vraiment besoin d'anonymiser la capitale ?"
            return {'err': res}
        #if x == "MARSEILLE":
        #    return {
        #        'city_name': x,
        #        'dept': y,
        #        'region': region2(y),
        #        'taille': taille_h(x, y),
        #        'graph_taille': f'jdl_web/graph_taille/{y}-{x}.png',
        #        'graph_tiret': f'jdl_web/graph_tiret/plot_{y}.png',
        #        'cities': ["CARMONT (cf. Paul Pasquali)"]
        #    }
        dep = y
        ville_entier_r = super_fonction(region2(y), dep)

        ############ Rajout de noms composés ##############
        ville_final = set()
        ville_final = list(ville_final)
        prop1 = freq_untiret(list(data_final[data_final["CODE_DEPT"] == dep]["NOM_COM"]))
        prop2 = freq_deuxtirets(list(data_final[data_final["CODE_DEPT"] == dep]["NOM_COM"]))

        if dep in ["91", "92", "93", "94", "95", "77", "78"] or int(taille_h(x, dep)) < 50000:
             for i in range(10):
                alea = random.random()
                # Débuts
                if alea < prop1/2 :
                    v = random.choice(import_pretiret(f"pretiret_{region2(y)}"))+random.choice(ville_entier_r)
                    ville_final.append(v)
                # Fins
                if prop1/2 < alea < 2*prop2/3 + prop1/2 and import_suftiret(f"suftiret2_{dep}") != []:
                    v = random.choice(ville_entier_r)+random.choice(import_suftiret(f"suftiret2_{dep}"))
                    ville_final.append(v)
                # Fins
                if prop1/2 < alea < 2*prop2/3 + prop1/2 and import_suftiret(f"suftiret2_{dep}") == []:
                    v = random.choice(ville_entier_r)+random.choice(import_miltiret(f"miltiret_{region2(y)}"))+random.choice(ville_entier_r)
                    ville_final.append(v)
                # Milieux
                if 2*prop2/3 + prop1/2 < alea < prop2 + prop1/2  :
                    v = random.choice(ville_entier_r)+random.choice(import_miltiret(f"miltiret_{region2(y)}"))+random.choice(ville_entier_r)
                    ville_final.append(v)
                # Compositions
                if prop2 + prop1/2 < alea < prop1 + prop2:
                    v = random.choice(ville_entier_r)+"-"+random.choice(ville_entier_r)
                    ville_final.append(v)
                if alea > prop1 + prop2:
                    v = random.choice(ville_entier_r)
                    ville_final.append(v) 
        else:
            for i in range(10):
                v = random.choice(ville_entier_r)
                ville_final.append(v)

    else:
        res = "Révisez votre géographie !"
        return {'err': res}
    return {
        'city_name': x,
        'dept': y,
        'region': region2(y),
        'taille': taille_h(x, y),
        'graph_taille': f'jdl_web/graph_taille/{y}-{x}.png',
        'graph_tiret': f'jdl_web/graph_tiret/plot_{y}.png',
        'cities': set(ville_final)
    }


               #
             #   #
               #


# # Statistiques descriptives et graphiques


####### Fonctions de statistiques descriptives sur la taille de la ville

### Fait un tri à plat des villes selon une taille donnée (encadrée par une borne min et une borne max), par département
def tri_taille(dep, mini, maxi):
    res = []
    data = extractdep(dep)
    liste = convliste(data, "NOM_COM")
    for x in liste:
        if int(taille_h(x, dep)) <= maxi and int(taille_h(x, dep)) > mini:
            res.append(x)
    res = set(res)
    res = list(res)
    return(res)

### Calcule la fréquence du nombre de villes avec tirets sur un intervalle de taille donné
def stat_tiret(dep, mini, maxi):
    liste = tri_taille(dep, mini, maxi)
    if liste == []:
        res = 0
    if liste != []:
        res = freq_tiret(liste)
    return(res)

### Calcule l'effectif du nombre de villes avec tirets sur un intervalle de taille donné
def stat_tiret2(dep, mini, maxi):
    liste = tri_taille(dep, mini, maxi)
    if liste == []:
        res = 0
    if liste != []:
        res = eff_tiret(liste)
    return(res)

########## Graphique 1 : donne la position de la ville dans le département selon sa taille 
# Abscisse = fréquence cumulée des villes
# Ordonnée = taille de la ville

def affich2(dep):
    res = []
    a = stat_tiret2(dep, 0, 200)
    b = stat_tiret2(dep, 200, 1000)
    c = stat_tiret2(dep, 1000, 20000)
    d = stat_tiret2(dep, 20000, 50000)
    e = stat_tiret2(dep, 50000, 100000)
    f = stat_tiret2(dep, 100000.0, math.inf)
    
    g = len(tri_taille(dep, 0, 200))
    h = len(tri_taille(dep, 200, 1000))
    i = len(tri_taille(dep, 1000, 20000))
    j = len(tri_taille(dep, 20000, 50000))
    k = len(tri_taille(dep, 50000, 100000))
    l = len(tri_taille(dep, 100000, math.inf))
            
    y1 = [a, b, c, d, e, f]
    y2 = [g - a , h - b , i - c, j - d, k - e, l - f]
    x = range(len(y1)) # position en abscisse des barres
    # Tracé
    largeur_barre = 0.8
    a = plt.bar(x, y1, width = largeur_barre, color = "#3ED8C9")
    b = plt.bar(x, y2, width = largeur_barre, bottom = y1, color = "#EDFF91")
    plt.xticks(range(len(y1)), ['0-200', '200-1000', '1000-20 000', '20 000-50 000', '50 000 - 100 000', "100 000 et plus"], rotation=60)
    plt.xlabel("Nombre d'habitants")
    plt.ylabel("Nombre de villes")
    plt.title(f"Noms simples ou composés dans le {dep} ?")
    plt.legend([a, b], ['Noms composés', 'Noms simples'])
    # plt.show()
    plt.savefig(f'plot_{dep}.png', bbox_inches='tight')
    plt.clf()
    return()

#### Ordonne les villes, par département, selon leur taille
def tripartaille(dep):
    liste = list(set(convliste(extractdep(dep), "NOM_COM")))
    liste.sort(key = lambda x : int(taille_h(x, dep)))
    if dep == "69":
        liste.append("LYON")
    if dep == "13":
        liste.append("MARSEILLE")
    return(liste)

### Calcule la proportion de villes avec nom composé dans le département
def pourcent(ville, dep):
    liste_ent = tripartaille(dep)
    bornesup = liste_ent.index(ville)
    liste_ville = liste_ent[0:bornesup+1]
    res = len(liste_ville)/len(liste_ent)*100
    return(res)


           

########## Graphique 2 : compare l'effectif de noms composés et noms simples dans un département donnés 
# Abscisse = taille de la ville (discret)
# Ordonnée = effectif

def courbe2(ville, dep, location):  
    t = import_listordon(f"listordon_{dep}")
    x = []
    y = []
    freqville = t.index(ville)/len(t)*100
    for i in range(len(t)):
        freq = i/len(t)*100
        x.append(freq) 
        y.append(int(taille_h(t[i], dep)))
    plt.yscale('log')
    plt.ylim(1,max([int(taille_h(x, dep)) for x in t]))
    plt.ylabel("Taille de la ville (échelle logarithmique)")
    plt.xlabel("Fréquence cumulée des villes dans le département")
    plt.title("Comment se situe cette ville dans le département selon sa taille ?")
    plt.scatter(x, y)
    plt.scatter(freqville, int(taille_h(ville, dep)), c = "red")
    plt.savefig(location, bbox_inches='tight')
    plt.clf()
    return() # affiche la figure a l'ecran
