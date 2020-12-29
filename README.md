# CARLAS
# # 27.12.2020  
# Status:  
&nbsp;Functional  
# De adaugat:  
1.Procesarea imaginii in paralel  
2.Populare cu pietoni  
3.Rezolvat sacadarea din opencv, https://youtu.be/LnJuMhz1QtU -> Abordat in V1.03 si V1.04  
4.De studiat diferitele tipuri de senzori pentru camera, Semantic segmentation / RGB  
5.Salvarea fisierului video (V1.03) -> Rezolvat in (1.04)  
6.Logging  
7.Pornire automata server (V1.04)

#  Version Log:  
##1.00  
-> Initial commit, functional  
##1.01  
-> Rezolvata problema legata de stergerea actorilor la finalul simularii, problema generata de garbage-collectorul din python care nu apela mereu functia __del__  
-> Adaugata posibilitatea de a selecta lumea in care se desfasoara simularea (Dezactivata, destul de inceata tranzitia)
##1.02  
->Migrat pe noua versiune de CARLA, 0.9.10
->Adaugat control pentru vreme, de vazut influenta asupra camerei  
##1.03  
https://youtu.be/6KcKXASQX8A  
->Rezolvata problema in care outputul camerei sarea peste frame-uri.
->Imbunatatit sistemul de aplicare a auto pilotului
->Separare intre senzori si vehicule
->Mecanismul de vizualizare nu mai este acum in real time, probleme cu frame-drops si fps, generate de Unreal Engine. Simularea este rulata, imaginile sunt salvate intr-un buffer care este afisat la finalul simularii.  
##1.04
->Adaugata posibilitatea de a salva videoclipul  
->Izolate listele cu senzori si vehicule  
->Mici modificari de sintaxa
