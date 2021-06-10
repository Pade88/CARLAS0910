# CARLAS
# # 10.06.2021  
# Status:  
&nbsp;Functional  
# De adaugat:  
1.Procesarea imaginii in paralel  -> Rezolvat in (1.07)  
2.Populare cu pietoni -> Rezolvat in (1.05)  
3.Rezolvat sacadarea din opencv, https://youtu.be/LnJuMhz1QtU -> Abordat in V1.03 si V1.04  
4.De studiat diferitele tipuri de senzori pentru camera, Semantic segmentation / RGB  -> Adaugat SS in (1.07)  
5.Salvarea fisierului video (V1.03) -> Rezolvat in (1.04)  
6.Logging  -> Necesar? Posibil drop  
7.Pornire automata server (V1.04)  
8.Comentarii ale codului + formatarea codului  
9.Model TensorFlow mai bine generat  
10. Model HAAR mai bine antrenat  
11. Metoda de obtinere a imaginilor dupa detectie pentru viitoarele antrenari  
12. Performanta crescuta in randare? 3 minute de simulare = 48 de minute de procesare. De analizat diferentele dintre .tiff si .png    

#  Version Log:  
**1.00**    
-> Initial commit, functional  
**1.01**   
-> Rezolvata problema legata de stergerea actorilor la finalul simularii, problema generata de garbage-collectorul din python care nu apela mereu functia __del__  
-> Adaugata posibilitatea de a selecta lumea in care se desfasoara simularea (Dezactivata, destul de inceata tranzitia)
**1.02**    
->Migrat pe noua versiune de CARLA, 0.9.10
->Adaugat control pentru vreme, de vazut influenta asupra camerei  
**1.03**    
https://youtu.be/6KcKXASQX8A  
->Rezolvata problema in care outputul camerei sarea peste frame-uri.  
->Imbunatatit sistemul de aplicare a auto pilotului  
->Separare intre senzori si vehicule  
->Mecanismul de vizualizare nu mai este acum in real time, probleme cu frame-drops si fps, generate de Unreal Engine. Simularea este rulata, imaginile sunt salvate intr-un buffer care este afisat la finalul simularii.  
**1.04**    
https://youtu.be/8eTqcVskhN4  
->Adaugata posibilitatea de a salva videoclipul  
->Izolate listele cu senzori si vehicule  
->Mici modificari de sintaxa  
**1.05**  
->Pietoni adaugati  
->Adaugat town10HD, maps update  
->Mici imbunatatiri  
**1.06**  
->Modificata functia de playback  
->Mici modificari de sintaxa si formatare  
**1.07**  
->Adaugata camera de segmentare semantica
->Adaugata procesarea in paralel
->Adaugata detectia semnelor de circulatie cu HAAR Cascade
->Adaugata detectia obiectelor cu opencv
