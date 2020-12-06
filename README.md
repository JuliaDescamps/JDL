## Données 

L’algorithme a été conçu à partir d’un fichier disponible sur [cette page](https://public.opendatasoft.com), croisant la base Geofla 2015 des communes de France et la base des codes postaux INSEE. J’y ai rajouté une variable « région » prenant en compte la classification préalable à la réforme territoriale de 2015, par esprit davantage pratique que réfractaire : afin d’avoir des sous-ensembles géographiques qui soient suffisamment grands et spécifiques de la toponymie. 

## Méthode


### Base des noms inventés 

JDL extrait, pour chaque région, une liste de préfixes et de suffixes caractéristiques de celle-ci. Plusieurs opérations de nettoyage sont nécessaires : écarter les préfixes et suffixes inclus les uns dans les autres, et écarter ceux qui sont trop courts pour être caractéristiques, notamment. Puis, JDL fusionne de manière aléatoire un préfixe et un suffixe. Il faut ensuite contrôler que cette fusion ne donne pas des noms syntaxiquement incorrects (succession improbable de voyelles ou de consonnes). 

Malheureusement, cette méthode ne fonctionne pas lorsque le nombre de villes est trop faible au sein d’une même région ou d’un même département. C’est pourquoi les communes d’Outre-mer sont écartées de JDL, à mon grand regret. 

### Ajouts de composés 

Enfin, parce que 15 511 communes (soit 39 % d’entre elles en 2015) ont un nom composé, JDL ajoute aux noms ainsi inventés des préfixes et suffixes composés, récoltés selon la même méthode, mais caractéristiques cette fois-ci à la fois de la région et du département. Le département joue ici un rôle de contrôle dans l’ajout de composés (par exemple pour éviter les Trifouillis-sur-Oise dans les Hauts-de-Seine). La probabilité d’apparition de ces composés dans la liste finale est calculée sur la fréquence réelle de villes au nom composé par département. J’ai fixé cette probabilité d’apparition à 0 pour les villes de taille supérieure à 50 000, hors région parisienne. En effet, seules 4 villes dans cette configuration ont des noms composés (Saint-Étienne, Cherbourg-en-Cotentin, Saint-Nazaire et La-Seyne-sur-Mer selon [Wikipedia](https://fr.wikipedia.org/wiki/Liste_des_communes_de_France_les_plus_peuplées)). 

Les renseignements sur la taille des communes et le calcul de la fréquence d’apparition des noms composés ont permis de faire quelques statistiques descriptives qui s’affichent lorsqu’une requête est demandée à JDL. D’autres idées de graphiques sont en germe... 
