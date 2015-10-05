__author__ = 'peikos'

import csv
import random
import logging

# Debug-berichten worden niet geprint, maar in plaats daarvan via logging.debug() getoond.
# Je hoeft dit niet te begrijpen, een ook niet de %s syntax die gebruikt wordt hiervoor.
# Het enige dat van belang is om te weten, is dat je het hekje bij de onderstaande regel
# kunt verwijderen om meer (debug) prints te zien. Aanroepen naar logging.debug kan je
# als optionele prints beschouwen.

# logging.basicConfig(level=logging.DEBUG)  # Ontcommenteer deze regel om alle debug-prints te zien.


menu_string = """
Welkom bij PyBank!

Hier is uw keuzemenu:
1: Rekeningen-overzicht
2: Rekening openen
3: Geld opnemen
4: Geld storten
5: Geld overschrijven
6: Rekening opzeggen
0: Stoppen
"""  # String


def get_rekeningen():  # IO [Rekening]
    """
    Haal alle rekeningen uit het CSV bestand.
    :return: Een lijst met alle rekeningen, elk weergegeven als dictionary.
    """
    csvfile = open('rekeningen.csv', 'r')
    csvr = csv.DictReader(csvfile)
    db = []
    for row in csvr:
        logging.debug("[REKENING] %s" % row)
        db.append(row)
    csvfile.close()
    return db


def get_rekening(rekeningnr):  # RekeningNr -> IO Rekening
    """
    Lees een rekeningnummer uit het CSV bestand.
    :param rekeningnr: Het nummer van de rekening om te laden.
    :return: De rekening, weergegeven als dictionary.
    """
    logging.debug("[REKENING] %s" % rekeningnr)
    return list(k for k in get_rekeningen() if k["rekening"] == str(rekeningnr))[0]
    # Dit is een python-generator of lijst-comprehensie. Hoef je niet te kunnen volgen.
    # Geeft basically het eerste element terug waarvoor de if waar is, oftewel de eerste met het juiste nummer.


def nieuw_rekeningnummer():  # IO Int
    """
    Geeft het eerstvolgende rekeningnummer dat vrij is.
    :return: Het rekeningnummer.
    """
    bestaand = get_rekeningnummers()
    rekeningnr = 0
    for rek in bestaand:
        if rek > rekeningnr:
            rekeningnr = rek
    logging.debug("[NIEUW NUMMER] %s" % str(rekeningnr + 1))
    return rekeningnr + 1


def get_rekeningnummers():  # IO {Int}
    """
    Geeft een set met bestaande rekeningnummers.
    :return: Een set met alle rekeningnummers.
    """
    bezet = set()
    for k in get_rekeningen():
        bezet.add(int(k['rekening']))
    logging.debug("[REKENINGNUMMERS] %s" % bezet or "{ }")
    return bezet


def schrijf_csv(rekeningen_nieuw):  # [Rekening] -> IO ()
    """
    Schrijft de huidige programma-toestand naar het CSV bestand.
    :param rekeningen_nieuw: Een lijst met dictionaries. Elk dictionary moet één rekening zijn.
    :return: ()
    """
    logging.debug("[SCHRIJF CSV] %s" % rekeningen_nieuw)
    csvfile = open('rekeningen.csv', 'w')
    fieldnames = ['rekening', 'naam', 'pin_code', 'saldo', 'roodlimiet', 'type']
    csvw = csv.DictWriter(csvfile, fieldnames=fieldnames)
    csvw.writeheader()
    csvw.writerows(rekeningen_nieuw)
    csvfile.close()


def nieuwe_rekening(rekeningnr=0, naam="Anonymous", rektype="betaal", roodlimiet=0):
    # Maybe RekeningNr, Maybe Naam, Maybe Type, Maybe Bedrag -> IO ()
    """
    Neemt een nieuwe rekening in gebruik. Als rekeningnr is gegeven wordt dit rekeningnummer geprobeerd.
    Bij geen nummer, of een nummer dat reeds in gebruik is, wordt een willekeurig vrij rekeningnummer gekozen.
    Geeft een foutmelding in STDOUT als alle rekeningen bezet zijn.
    :param rekeningnr: Het nummer van de rekening om in gebruik te nemen.
    :param naam: De naam van de rekeninghouder.
    :param rektype: Het type (betaal- of spaarrekening).
    :param roodlimiet: Het minimale bedrag dat op de rekening moet staan.
    :return: ()
    """
    logging.debug("[NIEUWE REKENING]")
    if rekeningnr == 0:
        nieuwe_rekening(nieuw_rekeningnummer())  # kies een random getal en probeer het nog eens.
    elif rekeningnr not in get_rekeningnummers():
        huidig = get_rekeningen()
        pin = ''.join(random.sample("0123456789", 4))
        huidig.append({'rekening': rekeningnr, 'pin_code': pin, 'naam': naam, 'type': rektype,
                       'roodlimiet': roodlimiet, 'saldo': 0})
        schrijf_csv(huidig)
        print("Je hebt rekening", rekeningnr, "gekregen!")
        print("Je PIN-code is:", pin)
    else:
        print("Rekening bezet, ik kies een andere rekening!")
        nieuwe_rekening(naam=naam, rektype=rektype, roodlimiet=roodlimiet)


def geld_opnemen(rekeningnr, bedrag, pin=None):  # RekeningNr, Bedrag -> IO Bool
    """
    Probeert geld van een rekening op te nemen. Vraagt de gebruiker om een PIN-code om te rekening te mogen openen,
    tenzij deze al is ingevoerd voor de functie werd aangeroepen.
    :param rekeningnr: Het nummer van de rekening om geld van op te nemen.
    :param bedrag: Het bedrag dat moet worden afgetrokken van het rekeningsaldo.
    :param pin: Als de gebruiker eerder haar PIN-code heeft ingevoerd kan deze worden meegegeven.
                Er wordt dan niet opnieuw om gevraagd.
    :return: True als de opname is gelukt; False als er een probleem is opgetreden.
    """
    logging.debug("[GELD OPNEMEN]")
    if not pin:
        print("Rekening", rekeningnr, end=". ")
        pin = input("Geef je PIN-code: ")
    bron = get_rekening(rekeningnr)
    if pin == bron["pin_code"]:
        if int(bron["saldo"]) - bedrag >= int(bron["roodlimiet"]):
            bron["saldo"] = str(int(bron["saldo"]) - bedrag)
            print("Je hebt €", bedrag, "van rekening", formatteer_iban(rekeningnr), "afgeschreven.")
            nieuwe_status = list(k for k in get_rekeningen() if not k["rekening"] == str(rekeningnr))
            # Dit is een python-generator of lijst-comprehensie. Hoef je niet te kunnen volgen.
            # Geeft basically alle elementen terug waarvoor de if onwaar is, oftewel alles behalve de rekening met
            # het gegeven nummer.
            nieuwe_status.append(bron)
            schrijf_csv(nieuwe_status)
            return True
        else:
            print("Onvoldoende saldo!")
            return False
    else:
        print("Dat is niet goed!")
        return False


def geld_storten(rekeningnr, bedrag):  # RekeningNr, Bedrag -> IO Bool
    """
    Stort een bedrag op een rekening.
    :param rekeningnr: Het nummer van de doel-rekening.
    :param bedrag: Het bedrag dat bij het saldo moet worden opgeteld.
    :return: True als de storting is gelukt. Omdat de overschrijving niet kan falen is dit altijd het geval.
    """
    logging.debug("[GELD STORTEN]")
    doel = get_rekening(rekeningnr)
    doel["saldo"] = str(int(doel["saldo"]) + bedrag)
    print("Je hebt €", bedrag, "op rekening", formatteer_iban(rekeningnr), "gestort.")
    nieuwe_status = list(k for k in get_rekeningen() if not k["rekening"] == str(rekeningnr))
    # Dit is een python-generator of lijst-comprehensie. Hoef je niet te kunnen volgen.
    # Geeft basically alle elementen terug waarvoor de if onwaar is, oftewel alles behalve de rekening met
    # het gegeven nummer.
    nieuwe_status.append(doel)
    schrijf_csv(nieuwe_status)
    return True


def geld_overboeken(bron, doel, bedrag, pin=None):  # RekeningNr, RekeningNr, Bedrag, Maybe PIN -> IO Bool
    """
    Probeert een bedrag over te schrijven. Vraagt de gebruiker om een PIN-code om te rekening te mogen benaderen, tenzij
    deze al is ingevoerd voordat de functie werd aangeroepen. Schrijft eerst het bedrag van de bron-rekening af, en als
    dit lukt wordt het bedrag bij de doelrekening bijgeschreven.
    :param bron: Het nummer van de rekening waarvan moet worden afgeschreven.
    :param doel: Het nummer van de rekening waarop moet worden gestort..
    :param bedrag: Het bedrag dat moet worden overgesschreven.
    :param pin: Als de gebruiker eerder haar PIN-code heeft ingevoerd kan deze worden meegegeven.
                Er wordt dan niet opnieuw om gevraagd.
    :return: True als de overschrijving is gelukt; False als er een probleem is opgetreden.
    """
    logging.debug("[GELD OVERBOEKEN]")
    if geld_opnemen(bron, bedrag, pin):
        return geld_storten(doel, bedrag)
    else:
        return False


def rekening_verwijderen(rekeningnr):  # RekeningNr -> IO Bool
    """
    Probeert een rekening te verwijderen. Vraagt de gebruiker om een PIN-code om te rekening te mogen verwijderen. Als
    de rekening rood staat kan deze niet worden verwijderd; als de rekening tegoed bevat moet een tweede rekeningnummer
    worden opgegeven, waar het tegoed naartoe kan. Geeft de PIN-code mee aan de overschrijf-functie, zodat deze niet
    twee keer wordt gevraagd.
    :param rekeningnr: Het nummer van de rekening om te verwijderen.
    :return: True als het opzeggen is gelukt; False als er een probleem is opgetreden.
    """
    logging.debug("[REKENING VERWIJDEREN]")
    rek = get_rekening(rekeningnr)
    pin = input("Geef je PIN-code om de rekening op te kunnen zeggen? ")
    if pin == rek["pin_code"]:
        if int(rek["saldo"]) < 0:
            print("Je kunt je rekening niet sluiten zo lang je rood staat.")
            return False
        elif int(rek["saldo"]) > 0:
            doel = input_rekeningnr("Op de rekening staat nog tegoed. Naar welke rekening wil je dit overschrijven? ")
            if not geld_overboeken(rekeningnr, doel, int(rek["saldo"]), pin):
                print("Er ging iets fout met overschrijven, probeer het later nog eens. Excuses voor het ongemak.")
                return False

        print("Je hebt de rekening", rekeningnr, "opgezegd.")
        nieuwe_status = list(k for k in get_rekeningen() if not k["rekening"] == str(rekeningnr))
        # Dit is een python-generator of lijst-comprehensie. Hoef je niet te kunnen volgen.
        # Geeft basically alle elementen terug waarvoor de if onwaar is, oftewel alles behalve de rekening met
        # het gegeven nummer.
        schrijf_csv(nieuwe_status)
        return True
    else:
        print("De juiste pincode is benodigd om de rekening op te kunnen zeggen.")
        return False


def input_integer(prompt):  # String -> Int
    """
    Hulpfunctie om een integer in te laten voeren. De functie blijft zichzelf aanroepen tot een leesbaar getal wordt
    ingevoerd.
    :param prompt: Het prompt.
    :return: De invoer als integer.
    """
    invoer = input(prompt)
    if invoer and invoer.isdigit():
        return int(invoer)
    else:
        print("Laten we dat nog een keer proberen...")
        return input_integer(prompt)


def input_rekeningnr(prompt):  # String -> RekeningNr
    """
    Hulpfunctie om een rekeningnummer in te laten voeren. De functie blijft zichzelf herhalen tot een bestaand rekening-
    nummer wordt ingevoerd. Maakt gebruik van input_integer().
    :param prompt: Het prompt.
    :return: De invoer als integer.
    """
    invoer = input_integer(prompt)
    if invoer in get_rekeningnummers():
        return invoer
    else:
        print("Laten we dat nog een keer proberen...")
        return input_rekeningnr(prompt)


def input_keuze(prompt, keuzes):  # String, Dict -> String
    """
    Hulpfunctie om een keuze te laten maken. De functie blijft zichzelf herhalen tot een geldige keuze is ingevoerd.
    De keuzes worden geleverd in een dictionary: de geldige karakters zijn hier de keys, de bijbehorende value wordt
    als resultaat van de functie teruggegeven. Alleen de eerste letter van de gebruikersinvoer wordt gelezen.
    :param prompt: Het prompt.
    :param keuzes: De keuzes en hoe deze geïnterpreteerd worden.
    :return:
    """
    invoer = input(prompt)
    if invoer and invoer[0] in keuzes.keys():
        return keuzes[invoer[0]]
    else:
        print("Laten we dat nog een keer proberen...")
        return input_keuze(prompt, keuzes)


def spaties_invoegen(string, lengte):  # String -> String
    """
    Hulpfunctie om een string in stukken van een gegeven lengte te knippen, gescheiden door spaties.
    :param string: De string om te verknippen.
    :param lengte: De lengte die de stukken moeten krijgen.
    :return: De verknipte string.
    """
    return ' '.join(string[i:i+lengte] for i in range(0, len(string), lengte))
    # Probeer dit maar niet te begrijpen ;-)
    # Maakt een range met de start-indices van ieder blok, gebruikt subscripting om alle blokken te verkrijgen, en
    # plakt de handel weer met spaties aan elkaar.


def formatteer_iban(rekeningnr):  # String -> String
    """
    Hulpfunctie om het rekeningnummer er interessanter uit te laten zien. Levert geen geldige IBAN-codes op, of in
    ieder geval niet met opzet.
    :param rekeningnr: Het rekeningnummer om te pimpen.
    :return: Een shiny pseudo-IBAN nummer.
    """
    iban = "NL42PYTH" + "{0:010d}".format(int(rekeningnr))
    return spaties_invoegen(iban, 4)


def menu_toon_rekeningen():  # IO ()
    """
    Menu-item één. Print alle rekeningnummers uit met een format string.
    :return: ()
    """
    for rek in get_rekeningen():
        rek["iban"] = formatteer_iban(rek["rekening"])
        print("{naam:s} <{type:1s}rekening {iban:s}> \n € {saldo:s} (€ {roodlimiet:s})\n".format(**rek))
        # De twee sterretjes maken het mogelijk de keys van de dictionary in de format-string te gebruiken.


def menu_maak_nieuwe_rekening():  # IO ()
    """
    Menu-item twee. Vraagt de nodige invoer om nieuwe_rekening() aan te kunnen roepen.
    :return: ()
    """
    nummer = input_integer("Welk nummer moet de nieuwe rekening hebben? ")
    naam = input("Wat is de naam van de rekeninghouder? ")
    rekeningtype = input_keuze("Gaat hem om een [B]etaalrekening of een [S]paarrekening? ",
                               {'b': 'betaal', 'B': 'betaal', 'S': 'spaar', 's': 'spaar'})
    roodlimiet = 0 - input_integer("Wat is de roodlimiet? ")
    nieuwe_rekening(nummer, naam, rekeningtype, roodlimiet)


def menu_neem_geld_op():  # IO ()
    """
    Menu-item drie. Vraagt de nodige invoer om geld_opnemen() aan te kunnen roepen.
    :return: ()
    """
    nummer = input_rekeningnr("Wat is het rekeningnummer? ")
    bedrag = input_integer("Hoeveel wil je opnemen? ")
    geld_opnemen(nummer, bedrag)


def menu_stort_geld():  # IO ()
    """
    Menu-item vier. Vraagt de nodige invoer om geld_storten() aan te kunnen roepen.
    :return: ()
    """
    nummer = input_rekeningnr("Wat is het rekeningnummer? ")
    bedrag = input_integer("Hoeveel wil je storten? ")
    geld_storten(nummer, bedrag)


def menu_boek_geld_over():  # IO ()
    """
    Menu-item vijf. Vraagt de nodige invoer om geld_overboeken() aan te kunnen roepen.
    :return: ()
    """
    bron = input_rekeningnr("Van welk rekeningnummer wil je geld overschrijven? ")
    doel = input_rekeningnr("Naar welk rekeningnummer moet het geld worden overgeschreven? ")
    bedrag = input_integer("Hoeveel wil je overschrijven? ")
    geld_overboeken(bron, doel, bedrag)


def menu_rekening_opzeggen():  # IO ()
    """
    Menu-item zes. Vraagt de nodige invoer om rekening_verwijderen() aan te kunnen roepen.
    :return: ()
    """
    rekeningnr = input_rekeningnr("Welk rekeningnummer wil je opzeggen? ")
    rekening_verwijderen(rekeningnr)


def menu(repeat=True):  # Bool -> IO ()
    """
    Menu. Blijft afhankelijk van de waarde van repeat eindeloos herhalen, of tot eenmaal een juiste keuze is gemaakt.
    :param repeat: Herhalen of niet?
    :return: ()
    """
    print(menu_string)
    keuze = input("Uw keuze: ")
    if not keuze:
        menu()
    elif keuze[0] == '1':
        menu_toon_rekeningen()
    elif keuze[0] == '2':
        menu_maak_nieuwe_rekening()
    elif keuze[0] == '3':
        menu_neem_geld_op()
    elif keuze[0] == '4':
        menu_stort_geld()
    elif keuze[0] == '5':
        menu_boek_geld_over()
    elif keuze[0] == '6':
        menu_rekening_opzeggen()
    elif keuze[0] == '0':
        exit(0)
    else:
        print("Dit is geen geldige keuze. U wordt teruggestuurd naar het hoofdmenu.")
        menu()

    if repeat:
        menu()


def menu_korter(repeat=True):  # Bool -> IO ()
    """
    Hetzelfde menu, maar nu met een functielijst. Hier wordt try/except gebruikt om mogelijke fouten af te vangen.
    :param repeat: Herhalen of niet?
    :return: ()
    """
    print(menu_string)
    keuze = input("Uw keuze: ")
    opties = [exit, menu_toon_rekeningen, menu_maak_nieuwe_rekening, menu_neem_geld_op, menu_stort_geld,
              menu_maak_nieuwe_rekening, menu_rekening_opzeggen]
    try:
        opties[int(keuze)]()
    except (IndexError, ValueError):
        print("Dit is geen geldige keuze. U wordt teruggestuurd naar het hoofdmenu.")
        menu_korter()
    if repeat:
        menu_korter()


open('rekeningen.csv', 'a').close()  # Dit garandeert dat het bestand bestaat.
menu_korter(True)  # Roep een herhalend menu aan.
