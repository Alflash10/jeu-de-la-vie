####Jeu de la vie Leul et Alexandre###
 
from tkinter import *
from tkinter import messagebox #Pour les regles
#from pygame import* #musique


# Fenêtre tkinter 
root = Tk() #fenetre  qui permet de commencer
space = " "
root.title(100*space+"Jeu de la vie")# Nom de la fenetre
root.minsize(900,600)# Dimension que l'utilisateur peut reduire jusqu'a ces dimensions
root.iconbitmap("ukraine.ico")#Icon en haut a gauche qui est une image, sorte de logo
canvas = Canvas(root, width=800, height=600, background="white") #dimension de la fenetre
canvas.pack(side=LEFT, padx=5, pady=5)#pack permet de afficher
 
n=30#nombre de rangee
p = 30#nombre de colonne
echelle = 30#taille d'une case
tableau = [[0 for j in range(p)] for i in range(n)] #grille vide(depart)


def nombre_voisins(i,j,tab): 
 """Calcule le nombre de voisin a coté de la case comme le démineur """
 nb = 0#Compteur qui compte le nombre de voisins
 # Voisin en haut à gauche
 if (i>0) and (j>0) and (tab[i-1][j-1] != 0):
  nb += 1
 # Voisin juste au-dessus
 if (i>0) and (tab[i-1][j] != 0):
  nb += 1
 # Voisin en haut à droite
 if (i>0) and (j<p-1) and (tab[i-1][j+1] != 0):
  nb += 1
 # Voisin juste à gauche
 if (j>0) and (tab[i][j-1] != 0):
  nb += 1
 # Voisin juste à droite
 if (j<p-1) and (tab[i][j+1] != 0):
  nb += 1
 # Voisin en bas à gauche
 if (i<n-1) and (j>0) and (tab[i+1][j-1] != 0):
  nb += 1
 # Voisin juste en-dessous
 if (i<n-1) and (tab[i+1][j] != 0):
  nb += 1
 # Voisin en bas à droite
 if (i<n-1) and (j<p-1) and (tab[i+1][j+1] != 0):
  nb += 1
 
 return nb #Il renvoie le nombre de voisin que la case a (entre 1 et8)
 
def evolution(tab):
 """ Modifie la grille en fonction du nombre de voisins par 1 tour """ 
 
 nouv_tab = [[0 for j in range(p)] for i in range(n)]#Nouvelle grille(tableau) pour avoir un tableau avec les regles appliquées
 
 for j in range(p):
  for i in range(n):
   if tab[i][j] != 0: #Si la case etait déja vivante soit different de 0
    cellule_vivante = True#Vivante
   else:
    cellule_vivante = False#Morte
 
 # Nombres de voisins de la case
   nb_voisins = nombre_voisins(i,j,tab)
 
 # Règle du jeu de la vie, si la case a plus de 3 voisins, elle meurt ou si moins de 2...
   if cellule_vivante == True and (nb_voisins == 2 or nb_voisins == 3):
    nouv_tab[i][j] = 1#Vivante
   if cellule_vivante == False and nb_voisins == 3:
    nouv_tab[i][j] = 1 #Vivante
 
 return nouv_tab #Renvoie le nouvlle grille(tableau)
 
 
def afficher_lignes():
 """ Affiche la grille à l'écran """ 
 for i in range(n+1):
  canvas.create_line(0,i*echelle,p*echelle,i*echelle) # ligne horizantale, echelle est la dimension de la case
 for j in range(p+1):
  canvas.create_line(j*echelle,0,j*echelle,n*echelle)# ligne verticale
 for i in range(n):
  canvas.create_text(echelle//3,i*echelle+echelle//2,text=str(i)) # le texte pour horizantale str permet d'avoir le numéro sur les cases
 for j in range(p): 
  canvas.create_text(j*echelle+echelle//2,echelle//3,text=str(j)) #le texte pour verticale
 return
 
def afficher_tableau(tab):
 """ Affiche un tableau à l'écran, tab= tableau de depart, renvoie tableau avec changement """ 
 for i in range(n):
  for j in range(p):
   if tab[i][j] != 0:
    canvas.create_rectangle(j*echelle,i*echelle,(j+1)*echelle,(i+1)*echelle,fill="black")#Case vivante fill est pour que la case deviene noir
 return
 
def clignotant():
 """ Shéma du clignotant """
 global tableau ,x     #global permet de modifier le tableau dans une fonction mais qui va etre modifier dans le programme
 tableau = [[0 for j in range(p)] for i in range(n)] 
 tableau[4][7] = 1
 tableau[4][8] = 1
 tableau[4][9] = 1
 x=0# Permet de mettre tour a zero
 text.config(text=x)
 text.pack
 canvas.delete("all") # Permet d'effacer la grille pour ajouter une nouvelle
 afficher_lignes() #Fonction pour afficher la nouvelle grille
 afficher_tableau(tableau)
 return
 
def vaisseau():
 """ Shéma du vasseau spatial """
 global tableau,x
 tableau = [[0 for j in range(p)] for i in range(n)] 
 tableau[3][4] = 1
 tableau[3][5] = 1
 tableau[3][6] = 1
 tableau[2][6] = 1
 tableau[1][5] = 1
 x=0
 text.config(text=x)
 text.pack
 canvas.delete("all") 
 afficher_lignes() 
 afficher_tableau(tableau)
 return

def pentadecathlon():
 """ Shéma du pentadecathlon """
 global tableau,x
 tableau = [[0 for j in range(p)] for i in range(n)] 
 tableau[6][4] = 1
 tableau[6][5] = 1
 tableau[6][7] = 1
 tableau[6][8] = 1 
 tableau[6][9] = 1
 tableau[6][10] = 1
 tableau[6][12] = 1
 tableau[6][13] = 1 
 tableau[5][6] = 1
 tableau[7][6] = 1
 tableau[5][11] = 1
 tableau[7][11] = 1 
 x=0
 text.config(text=x)
 text.pack
 canvas.delete("all") 
 afficher_lignes() 
 afficher_tableau(tableau)
 return

def grenouille():
 """ Shéma de la grenouille"""
 global tableau,x
 tableau = [[0 for j in range(p)] for i in range(n)] 
 tableau[7][4] = 1
 tableau[7][5] = 1
 tableau[7][6] = 1
 tableau[6][5] = 1 
 tableau[6][6] = 1
 tableau[6][7] = 1
 x=0
 text.config(text=x)
 text.pack
 canvas.delete("all") 
 afficher_lignes() 
 afficher_tableau(tableau)
 return

def planer():
 """ Shéma du planer """
 global tableau,x
 tableau = [[0 for j in range(p)] for i in range(n)] 
 tableau[7][7] = 1
 tableau[8][8] = 1
 tableau[9][6] = 1
 tableau[9][7] = 1 
 tableau[9][8] = 1
 x=0
 text.config(text=x)
 text.pack
 canvas.delete("all") 
 afficher_lignes() 
 afficher_tableau(tableau)
 return
 
def pyramide():
    """Shéma d'une pyramide"""
    global tableau,x
    tableau = [[0 for j in range(p)] for i in range(n)] 
    tableau[5][5] = 1
    tableau[6][4] = 1
    tableau[6][6] = 1
    tableau[7][7] = 1 
    tableau[7][3] = 1
    tableau[8][2] = 1
    tableau[8][3] = 1
    tableau[8][4] = 1
    tableau[8][5] = 1 
    tableau[8][6] = 1
    tableau[8][7] = 1 
    tableau[8][8] = 1
    x=0
    text.config(text=x)
    text.pack
    canvas.delete("all") 
    afficher_lignes() 
    afficher_tableau(tableau)
    return

def vaisseau_2():
    """Shéma du vaisseau_bis"""
    global tableau,x
    tableau = [[0 for j in range(p)] for i in range(n)] 
    tableau[2][2] = 1
    tableau[4][2] = 1
    tableau[5][3] = 1
    tableau[5][4] = 1 
    tableau[5][5] = 1
    tableau[5][6] = 1
    tableau[4][6] = 1
    tableau[3][6] = 1
    tableau[2][5] = 1 
    x=0
    text.config(text=x)
    text.pack
    canvas.delete("all") 
    afficher_lignes() 
    afficher_tableau(tableau)
    return

def croix():
    """Shéma de la croix"""
    global tableau,x
    tableau = [[0 for j in range(p)] for i in range(n)] 
    tableau[2][3] = 1
    tableau[2][4] = 1
    tableau[2][5] = 1
    tableau[2][6] = 1 
    tableau[3][3] = 1
    tableau[3][6] = 1
    tableau[4][1] = 1
    tableau[4][2] = 1
    tableau[4][3] = 1 
    tableau[4][6] = 1
    tableau[4][7] = 1
    tableau[4][8] = 1 
    tableau[5][1] = 1
    tableau[5][8] = 1
    tableau[6][1] = 1
    tableau[6][8] = 1
    tableau[7][1] = 1
    tableau[7][2] = 1
    tableau[7][3] = 1 
    tableau[7][8] = 1
    tableau[7][7] = 1
    tableau[7][6] = 1
    tableau[8][3] = 1
    tableau[8][6] = 1 
    tableau[9][3] = 1
    tableau[9][4] = 1
    tableau[9][5] = 1
    tableau[9][6] = 1 
    x=0
    text.config(text=x)
    text.pack
    canvas.delete("all") 
    afficher_lignes() 
    afficher_tableau(tableau)
    return

def diagonale():
    global tableau,x
    tableau = [[0 for j in range(p)] for i in range(n)] 
    tableau[4][16] = 1
    tableau[4][15] = 1
    tableau[5][15] = 1
    tableau[6][15] = 1 
    tableau[7][14] = 1
    tableau[6][13] = 1
    tableau[6][12] = 1
    tableau[7][11] = 1
    tableau[8][11] = 1 
    tableau[8][12] = 1
    tableau[9][12] = 1
    tableau[9][13] = 1 
    tableau[10][13] = 1
    tableau[11][12] = 1
    tableau[11][11] = 1
    tableau[10][10] = 1
    tableau[11][9] = 1
    tableau[12][9] = 1
    tableau[13][9] = 1 
    tableau[13][8] = 1
    tableau[13][7] = 1
    x=0
    text.config(text=x)
    text.pack
    canvas.delete("all") 
    afficher_lignes() 
    afficher_tableau(tableau)
    return
   
    canvas.delete("all") 
    afficher_lignes() 
    afficher_tableau(tableau)
    return
    
def bouton_evolution(): #changement du aux regle donc nouveau affichage
 global tableau
 tableau = evolution(tableau)
 canvas.delete("all")
 afficher_lignes()
 afficher_tableau(tableau)
 tour()
 return

    
def restart():  #fonction pour revenir a une grille vierge
    global x
    canvas.delete("all")
    x=0
    text.config(text=x)
    text.pack
    afficher_lignes()
    return x

#Messagebox: permet d'ouvrir une fenetre juste pour une information
def regle():
    messagebox.showinfo("Régles","Régles tres simple: -Si une case(cellule) veut rester en vie, elle doit avoir 2 ou 3 voisins-Si une case(cellule) veut mourir, elle doit avoir moins de 2 ou plus de 3")
#Fonction qui compte le nombre de tour
x=0
def tour():
      global x
      x+=1
      text.config(text=x)
      text.pack
      return x

def grille_100(): # modifier le tableau(grille) sur 100*100
    global n,p,echelle,tableau
    n=100#Dimension
    p=100
    echelle=10#Dimension de la case
    tableau = [[0 for j in range(p)] for i in range(n)]
    canvas.delete("all")
    afficher_lignes()
    afficher_tableau(tableau)
    return n,p,echelle

def grille_50(): # modifier le tableau(grille) sur 50*50
    global n,p,echelle,tableau
    n=50 #Dimension
    p=50
    echelle=10#Dimension de la case
    tableau = [[0 for j in range(p)] for i in range(n)]
    canvas.delete("all")
    afficher_lignes()
    afficher_tableau(tableau)
    return n,p,echelle

#Menu pour le fichier et figures qui  est deroulante     
menu_bar=Menu(root)
fichier_menu=Menu(menu_bar,tearoff=0)
fichier_menu.add_command(label="Quitter", command=root.quit)#Quitter la fenetre
fichier_menu.add_command(label="Nouveau", command=restart)#Recommencer a nouveau
menu_bar.add_cascade(label="Fichier", menu=fichier_menu)# Menu deroulant
figure_menu=Menu(menu_bar,tearoff=0)#tearoff permet d'enlever le tiret qui n'est pas tres beau
figure_menu.add_command(label="Clignotant", command=clignotant)#Different figure
figure_menu.add_command(label="Vaisseau", command=vaisseau)
figure_menu.add_command(label="Pentadecathlon", command=pentadecathlon)
figure_menu.add_command(label="Grenouille", command=grenouille)
figure_menu.add_command(label="Planer", command=planer)
figure_menu.add_command(label="Pyramide", command=pyramide)
figure_menu.add_command(label="Vaisseau_bis", command=vaisseau_2)
figure_menu.add_command(label="Croix", command=croix)
figure_menu.add_command(label="Diagonale", command=diagonale)
menu_bar.add_cascade(label="Figure",menu=figure_menu)#Menu deroulant
grille_menu=Menu(menu_bar,tearoff=0)
grille_menu.add_command(label="Grille:100", command=grille_100)#Differente grille
grille_menu.add_command(label="Grille:50", command=grille_50)#Differente grille 
menu_bar.add_cascade(label="Grille",menu=grille_menu)

root.config(menu=menu_bar)
#Bouton de droite pour evoluer, evoluer rapide et le nombre de tour
bouton_afficher = Button(root,text="Évoluer", width=10, command=bouton_evolution)#Permet d'evoluer
bouton_afficher.pack(side=TOP, padx=5, pady=5)#Position
bouton_regle = Button(root,text="Régle", width=10, command=regle)#Regle du jeu
bouton_regle.pack(side=TOP, padx=5, pady=5)#Position
text=Label(root,text=x)#Permet de montrer le nombre de tour que l'utilisateur a fait
text.pack(side=TOP,padx=5, pady=5)
text_tour=Label(root,text="tour(s)")#Plus beau
text_tour.pack(side=TOP,padx=5, pady=5)
#Musique
"""
pygame.mixer.int()
def play():
    pygame.mixer.music.load("musique") #Telecharger la musique
    pygame.mixer.music.play()#Jouer la musique
    
def stop():#Arreter la music
    pygame.mixer.music.stop()#Fonction pour arreter
    
musique=Button(root,text="Musique",command=play)#Bouton pour allumer 
musique.pack(side=TOP,padx=5,pady=5)
stop=Button(root,text="Stop",command=stop)#Bouton pour eteindre
stop.pack(side=TOP,padx=5,pady=5)
"""
 
def allumer_eteindre(i,j): #pour que la case cliquer est égale a 1 soit noir
 global tableau
 if tableau[i][j] == 0:
  tableau[i][j] = 1
 else: 
  tableau[i][j] = 0
 return
 
 
def xy_vers_ij(x,y): #pour avoir la taille de la case(cellule)
 i = y // echelle
 j = x // echelle
 return i, j
 
 
def action_clic_souris(event): #Grille qui change quand l'utilisateur clique 
 canvas.focus_set()
 # print("Clic à", event.x, event.y)
 x = event.x #Positon en x de la souris
 y = event.y#Positon en y de la souris
 allumer_eteindre(*xy_vers_ij(x,y))#Pour mettre en vie une case
 canvas.delete("all") 
 afficher_lignes() 
 afficher_tableau(tableau)
 return
 
# Liaison clic, Button-1 : a clic gauche
canvas.bind("<Button-1>",action_clic_souris)
 
afficher_lignes()#Pour afficher au depart la grille
afficher_tableau(tableau)#Pour afficher au depart la grille
root.mainloop()#Fin de la fenetre, hors ca rien n'apparaitra