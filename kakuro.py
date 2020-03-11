import copy
import math
import queue
from collections import OrderedDict
import itertools

counter = itertools.count()
Infinity = math.inf
plansza_startowa = OrderedDict
litery = 'ABCDEFGH'
cyfry = '123456789'



# FUNKCJE POMOCNICZE

# parsujemy zadaną planszę, jako wynik otrzymujemy listę haseł i szukanych sum
def utworz_liste_hasel(rozmiar, plansza):
    lista_hasel = []
    for key in plansza.keys():
        if plansza[key]: #jesli istnieje pole z szukaną_sumą
            wiersz, kolumna = list(key)
            for kierunek in plansza[key].keys():
                haslo = []
                if kierunek == 'pionowo':
                	haslo = [box_wiersz + kolumna for box_wiersz in list(litery)[list(litery).index(wiersz) + 1:rozmiar]]            
                elif kierunek == 'poziomo':
                    haslo = [wiersz + str(box_kolumna) for box_kolumna in range(int(kolumna) + 1, rozmiar + 1)]

                haslo.append(plansza[key][kierunek])
                lista_hasel.append(haslo)
    print ("lista_hasel = ", lista_hasel, "\n")
    return lista_hasel

# Jeżeli w komórkę wpiszemy cyfrę, to możemy ją usunąć w pozostałych komórkach w danym haśle
def usun_pojedyncza_mozliwosc_u_sasiadow(stan):
    for haslo in lista_hasel:
        for pole in range(0, len(haslo)-1):
            if len(stan[haslo[pole]]) == 1:
                for sasiad in range(0, len(haslo)-1):
                    if sasiad != pole:
	                    stan[haslo[sasiad]] = stan[haslo[sasiad]].replace(stan[haslo[pole]], '')
    return stan

#stan terminalny jest wtedy, kiedy w każdym polu jest tylko jedna cyfra
#oraz suma cyfr w każdym haśle zgadza się z szukaną sumą
def stan_terminalny(stan):
	for haslo in lista_hasel:
		for pole in range(0, len(haslo)-1):
			if len(stan[haslo[pole]])>1:
				return False
	return True

#sprawdza czy dany stan gry jest niemożliwy, jak np. w przypadku, gdy
#cyfry w uzupełnionym haśle nie sumują się do poszukiwanej sumy
def stan_zakazany(stan):
	for haslo in lista_hasel:
		pole_z_najw_liczba_cyfr = 1
		for pole in range(0, len(haslo)-1):
			if len(stan[haslo[pole]])>1:
				pole_z_najw_liczba_cyfr = len(stan[haslo[pole]])
		if pole_z_najw_liczba_cyfr == 1: 
			#sprawdzamy czy pola w jednostce sumuja sie do prawidlowej wartosci
			suma = 0
			for pole in range(0, len(haslo)-1):
				suma += int(stan[haslo[pole]])
			if suma != haslo[-1]:
				return True
	return False

#po znalezieniu stanu terminalnego odtworzymy drogę dotarcia do niego od stanu początkowego
def odtworz_droge(poprzednicy, poczatek, koniec):
	biezacy = koniec
	droga = []
	while biezacy != poczatek:
		droga.append(biezacy)
		for i in range(0, len(poprzednicy)):
			if poprzednicy[i][0] == biezacy:
				biezacy = poprzednicy[i][1]
				break
	droga.append(poczatek)
	droga.reverse()
	return droga




# WCZYTANIE PLANSZY, UTWORZENIE LISTY HASEŁ

# Przykładowa Plansza nr 1
#lista_hasel = utworz_liste_hasel(3, {'A1':{'poziomo': 4, 'pionowo': 4}, 'B2': None, 'B3': None, 'C2': None, 'C3': None})
#plansza_startowa = {'A2': cyfry, 'A3': cyfry, 'B1': cyfry, 'C1': cyfry}

# Przykładowa Plansza nr 2
lista_hasel = utworz_liste_hasel(4, {'A1':{'poziomo': 6, 'pionowo': 9}, 'B2': None, 'B3': None, 'B4': None, 'C2': None, 'C3': None, 'C4': None, 'D2': None, 'D3': None, 'D4': None})
plansza_startowa = {'A2': cyfry, 'A3': cyfry, 'A4': cyfry, 'B1': cyfry, 'C1': cyfry, 'D1': cyfry}

# Przykładowa Plansza nr 3
#lista_hasel = utworz_liste_hasel(4, {'A1':{'poziomo': 9, 'pionowo': 6}, 'B2': None, 'B3': {'poziomo': 3, 'pionowo': 10}, 'C2': None, 'C4': None, 'D2': None, 'D4': None})
#plansza_startowa = {'A2': cyfry, 'A3': cyfry, 'A4': cyfry, 'B1': cyfry, 'C1': cyfry, 'D1': cyfry, 'B4': cyfry, 'C3': cyfry, 'D3': cyfry}





# POSZUKIWANIE ROZWIĄZANIA ZA POMOCĄ ALGORTYMU A*

stan_biezacy = plansza_startowa
zbior_Q = queue.PriorityQueue()	#do zbioru Q będziemy dodawać rozwijane stany

koszt = 0 #koszt stanu to suma kosztu dotarcia do bieżącego stanu 
		  #i heurystyki szacującej koszt dotarcia od niego do stanu terminalnego
koszt_dotychczas = 0 #faktyczny koszt dotarcia do bieżącego stanu

odwiedzone = [plansza_startowa] #bedziemy utrzymywać listę stanów, które już sprawdziliśmy,
								#żeby nie sprawdzać ich ponownie
poprzednicy = [] # lista, ktora bedzie zawierała pary - (stan, jego poprzednik)
				 # użyjemy jej do odtworzenia ścieżki rozwiązania


# Rozwijamy stan bieżacy
while not stan_terminalny(stan_biezacy):
	for pole in stan_biezacy.keys() :
		if len(stan_biezacy[pole])>1: #mamy wiecej niz jedna cyfre do wyboru
			for cyfra in stan_biezacy[pole]: #przechodzimy po cyfrach dostepnych w danym polu
				
				kopia_stanu = copy.copy(stan_biezacy) #będziemy pracować na kopii stanu
				kopia_stanu[pole] = cyfra #w pierwsze pole wpisujemy pierwszą cyfrę
				kopia_stanu = usun_pojedyncza_mozliwosc_u_sasiadow(kopia_stanu) #i usuwamy ją w sąsiednich polach danego hasła
				
				if kopia_stanu not in odwiedzone and not stan_zakazany(kopia_stanu):
					#obliczamy heurystykę, jako liczbę możliwych cyfr do wpisania w polach, gdzie jest więcej możliwości niż 1
					liczba_mozliwych_cyfr = 0
					for pozostale_cyfry in kopia_stanu.values():
						if len(pozostale_cyfry) > 1:
							liczba_mozliwych_cyfr += len(pozostale_cyfry)
						else:
							koszt_dotychczas += 0

					koszt = koszt_dotychczas + liczba_mozliwych_cyfr
					zbior_Q.put((koszt, next(counter), kopia_stanu)) # dopisujemy nowy stan do zbioru Q
																	 # używamy countera, żeby PriorityQueue mogła działąć ze słownikami
					odwiedzone.append(kopia_stanu)
					poprzednicy.append((kopia_stanu, stan_biezacy)) #stan_biezacy jest poprzednikiem kopii_stanu				
					print('dodano do Q: ', kopia_stanu, '\n')

					koszt_dotychczas = 0
		
	stan_z_kosztem = zbior_Q.get()
	stan_biezacy = stan_z_kosztem[2]
	print('rozwijany stan ', stan_biezacy, '\n')

		
# Wypisujemy znalezione rozwiązanie
print('Rozwiązanie: \n' )
droga = odtworz_droge(poprzednicy, plansza_startowa, stan_biezacy)
for stan in droga:
	print(stan)