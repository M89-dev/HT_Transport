import xml.etree.ElementTree as ET
import random

class Calcul_HT_Transport:

    def __init__(self):
        self.tree_client = ET.parse("INFO_transport/client.xml")
        self.root_client = self.tree_client.getroot()

        self.tree_localite = ET.parse("INFO_transport/localite.xml")
        self.root_localite = self.tree_localite.getroot()

        self.tree_tarif = ET.parse("INFO_transport/tarif.xml")
        self.root_tarif = self.tree_tarif.getroot()

        self.tree_taxation = ET.parse("INFO_transport/conditiontaxation.xml")
        self.root_taxation = self.tree_taxation.getroot()

        self.object_clients = self.root_client.findall(".//ObjectClient")
        self.object_localites = self.root_localite.findall(".//ObjectLocalite")
        self.object_tarifs = self.root_tarif.findall(".//ObjectTarif")
        self.object_condition_taxations = self.root_taxation.findall(".//ObjectConditionTaxation")

    # Fonction pour prendre au hasard un Client et un Expediteur différents
    def get_info_client(self):
        random_expediteur = random.choice(self.object_clients)
        random_destinataire = random.choice(self.object_clients)

        while random_destinataire == random_expediteur:
            random_destinataire = random.choice(self.object_clients)

        return random_expediteur, random_destinataire

    # Fonction qui sert à saisir le nombre de colis et le poids de l’expédition.
    def input_info(self):
        print("Quelle est le nombre total de colis ?")
        nombre_colis = int(input("> "))
        
        print("Quel est le poids total des colis ? ")
        poids_colis = float(input("> "))


        return nombre_colis, poids_colis

    # Fonction pour prendre au hasard de l’expéditeur ou du destinataire qui règle le transport
    def get_payement_info(self, *args):
        return random.choice(args)

    # Fonction qui sert à derterminer ou se trouve la zone du destinataire
    def get_zone_destinataire(self, client_destinataire):
        ville_dest = client_destinataire.find("ville").text

        for localite in self.object_localites:
            ville_loc = localite.find("ville").text
            zone_loc = localite.find("zone").text

            if ville_loc == ville_dest:
                return zone_loc

    # Fonction qui permet de recuperer tous les tarifs avec le meme ID et code_postale
    def get_all_zone_id(self, zone_num_id, code_postal_destinataire):
        liste_zone_tarifs = []

        for tarif in self.object_tarifs:
            code_client_id = tarif.find("idClient").text
            tarif_codeDepartement = tarif.find("codeDepartement").text

            if code_client_id == zone_num_id and code_postal_destinataire == tarif_codeDepartement:
                liste_zone_tarifs.append(tarif)

        return liste_zone_tarifs
    
    # Fonction qui permet de determiner les tarifs de la zone en fonction de la zone et de l'ID Client
    def get_tarif_zone(self, liste_zone_tarifs, zone_destinataire, code_postal_destinataire):
        for tarif in liste_zone_tarifs:
            tarif_zone = tarif.find("zone").text
            tarif_montant = tarif.find("montant").text
            tarif_id = tarif.find("idClient").text
            tarif_heritage = tarif.find("idClientHeritage").text

            if tarif_zone == zone_destinataire:
                if tarif_heritage: # Regarde si le paramètre heritage Client est true
                    print("Votre département ne possède aucun tarif, C'est donc les tarifs généraux qui sont pris en compte\n")
                    liste_zone_tarifs = self.get_all_zone_id(tarif_heritage, code_postal_destinataire)
                    return self.get_tarif_zone(liste_zone_tarifs, zone_destinataire, code_postal_destinataire)
                else:
                    return tarif_montant, tarif_id

        # Si un tarif n’existe pas dans la zone déterminée, alors on utilise le tarif de la zone z-1.
        tarif_montant_inverse, tarif_id_inverse = self.inverse_tarrif_zone(liste_zone_tarifs, zone_destinataire)
        return tarif_montant_inverse, tarif_id_inverse
    
    # Fonction qui récupère l'inverse de la zone que l'on cherche pour le département
    def inverse_tarrif_zone(self, liste_zone_tarifs, zone):
        for tarif in liste_zone_tarifs:
            tarif_zone = tarif.find("zone").text
            tarif_monatant = tarif.find("montant").text
            tarif_id = tarif.find("idClient").text

            if tarif_zone != zone:
                return tarif_monatant, tarif_id

    # Fonction qui permet de recuperer les taxations en fonction de l'ID Client  
    def get_taxation_zone(self, id_destinataire):
        for condition_taxation in self.object_condition_taxations:

            id_taxation_zone = condition_taxation.find("idClient").text
            taxePortDu = condition_taxation.find("taxePortDu").text
            taxePortPaye = condition_taxation.find("taxePortPaye").text
            useTaxePortDuGenerale = condition_taxation.find("useTaxePortDuGenerale").text
            useTaxePortPayeGenerale = condition_taxation.find("useTaxePortPayeGenerale").text

            taxePortDuGeneral = self.object_condition_taxations[0].find("taxePortDu").text
            taxePortPayeGeneral = self.object_condition_taxations[0].find("taxePortPaye").text

            if id_taxation_zone == id_destinataire:

                if useTaxePortDuGenerale and useTaxePortPayeGenerale:
                    return self.get_payement_info(taxePortDuGeneral, taxePortPayeGeneral)
                
                elif useTaxePortPayeGenerale:
                    return taxePortPayeGeneral
                
                elif useTaxePortDuGenerale:
                    return taxePortDuGeneral
                
                else:
                    return self.get_payement_info(taxePortDu, taxePortPaye)
        
        print("Votre département ne possède aucune taxation, C'est donc les taxations générales qui sont prises en compte\n")
        return self.get_payement_info(taxePortDuGeneral, taxePortPayeGeneral)

    # Fonction qui permet de centraliser tous les tarifs et taxations de l'expedition
    def get_tarif_info(self, zone_destinataire, code_postal_destinataire, code_id):
        liste_zone_tarifs = []

        liste_zone_tarifs = self.get_all_zone_id(code_id, code_postal_destinataire)

        if len(liste_zone_tarifs) >= 1: # Le client possèdent des tarifs pour ce département
            tarif_montant, tarif_id = self.get_tarif_zone(liste_zone_tarifs, zone_destinataire, code_postal_destinataire)
            taxation_montant = self.get_taxation_zone(tarif_id)
            
        else: # Le client ne possèdent pas de tarifs pour ce département
            liste_zone_tarifs = self.get_all_zone_id("0", code_postal_destinataire)
            tarif_montant, tarif_id = self.get_tarif_zone(liste_zone_tarifs, zone_destinataire, code_postal_destinataire)
            taxation_montant = self.get_taxation_zone(tarif_id)

        return tarif_montant, taxation_montant

    def main(self):
        client_expediteur, client_destinataire = self.get_info_client()

        # Informations sur le destinataire
        zone_destinataire = self.get_zone_destinataire(client_destinataire)
        id_destinataire = client_destinataire.find("idClient").text
        code_postal_destinataire = client_destinataire.find("codePostal").text
        raisonSociale_destinataire = client_destinataire.find("raisonSociale").text
        ville_destinataire = client_destinataire.find("ville").text

        # Informations sur l'expediteur
        id_expediteur = client_expediteur.find("idClient").text
        code_postal_expediteur = client_expediteur.find("codePostal").text
        raisonSociale_expediteur = client_expediteur.find("raisonSociale").text
        ville_expediteur = client_expediteur.find("ville").text

        # Récupère les infos sur les colis
        nb_colis, poid_colis = self.input_info()

        # Calcule la somme total de l'expedition
        tarif_montant, taxation_montant = self.get_tarif_info(zone_destinataire, code_postal_destinataire, id_destinataire)
        sum_total = tarif_montant + taxation_montant

        # Présentation des données
        print("--------------------------------------------")
        print("Expediteur ->\n")
        print("idClient :", id_expediteur)
        print("codePostale :", code_postal_expediteur)
        print("raisonSociale :", raisonSociale_expediteur)
        print("ville :", ville_expediteur)
        print("--------------------------------------------")
        print("Destinataire ->\n")
        print("idClient :", id_destinataire)
        print("codePostale :", code_postal_destinataire)
        print("raisonSociale :", raisonSociale_destinataire)
        print("ville :", ville_destinataire)
        print("--------------------------------------------")
        print("Nombre de colis ->", nb_colis)
        print("Poids colis ->", poid_colis ,"KG")
        print("--------------------------------------------")
        print("Le montant total est donc de :", sum_total, "euro")
        print("--------------------------------------------")
        print("Tarifs département ->", tarif_montant, "euro")
        print("Taxation département ->", taxation_montant, "euro")
        print("--------------------------------------------")

# Création d'une instance de la classe
calcul_transport = Calcul_HT_Transport()

# Appel de la méthode principale pour exécuter le programme
calcul_transport.main()
