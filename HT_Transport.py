import xml.etree.ElementTree as ET

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

        self.montant_tarif = None
        self.montant_taxation = None

    # Fonction qui permet de récuperer les infos pour l'expediteur, le destinataire et autre ....
    def get_user_info(self):
        self.client_id_expediteur = str(input("Entrez l'id du client expéditeur : "))
        self.client_id_destinataire = str(input("Entrez l'id du client destinataire : "))
        self.nombre_colis = int(input("Entrez le nombre de colis : "))
        self.poids_expedition = float(input("Entrez le poids de l'expédition : "))
        self.port_paye = input("Le transport est payé par le destinataire (O/N)? ").upper()
        self.boolean_port_paye()

    # Fonction qui transforme la réponse pour savoir qui paye en boolean
    def boolean_port_paye(self):
        self.port_paye = self.port_paye == "O"

    # Fonction qui permet de récuperer toutes les informations nécessaire sur le destinataire 
    def get_info_destinataire(self):
        ville_destinataire = None

        for client in self.object_clients:
            if client.find("idClient").text == self.client_id_destinataire:
                ville_destinataire = client.find("ville").text

        for localite in self.object_localites:
            if localite.find("ville").text == ville_destinataire:
                return localite.find("zone").text, localite.find("codePostal").text

    # Fonction qui permet de récuperer les tarifs de la zone que l'on souhaite         
    def get_tarif_zone(self, zone, client_id, code_postal):
        for tarif in self.object_tarifs:
    
            if tarif.find('idClient').text == client_id and tarif.find('zone').text == zone and code_postal == tarif.find('codeDepartement').text:
                if tarif.find('idClientHeritage').text is None:
                    self.montant_tarif = float(tarif.find('montant').text)
                    return 
                else:
                    self.get_tarif_zone(zone, tarif.find('idClientHeritage').text, code_postal)

        return None
    
    # Fonction qui permet de récuperer les taxations de la zone que l'on souhaite    
    def get_taxation_zone(self, client_id):
        for condition_taxation in self.object_condition_taxations:
            if condition_taxation.find("idClient").text == client_id or client_id == "0":
    
                if self.port_paye:
                    if condition_taxation.find("useTaxePortPayeGenerale").text == "true":
                        self.get_taxation_zone("0")
                    else:
                        self.montant_taxation = float(condition_taxation.find("taxePortPaye").text)
                        return
                
                else:
                    if condition_taxation.find("useTaxePortDuGenerale").text == "true":
                        self.get_taxation_zone("0")
                    else:
                        self.montant_taxation = float(condition_taxation.find("taxePortDu").text)
                        return

        self.get_taxation_zone("0")

    # Fonction qui regroupe toutes les infos sur les tarifs et taxations
    def get_tarif_info(self, zone, client_id, code_postal):

        self.get_taxation_zone(client_id)
        self.get_tarif_zone(zone, client_id, code_postal)

        if self.montant_tarif is None:
            self.get_tarif_zone(str((int(zone)) - 1), client_id, code_postal)

            if self.montant_tarif is None:
                self.get_tarif_zone(zone, "0", code_postal)

    # Principale fonction du programme
    def main(self):
        self.get_user_info()
        zone_destinataire, code_postale_destinataire = self.get_info_destinataire()
        self.get_tarif_info(zone_destinataire, self.client_id_destinataire, code_postale_destinataire)

        sum_total = self.montant_tarif + self.montant_taxation

        # Présentation des données
        print("--------------------------------------------")
        print("Nombre de colis ->", self.nombre_colis)
        print("Poids colis ->", self.poids_expedition ,"KG")
        print("--------------------------------------------")
        print("Tarifs département ->", self.montant_tarif, "euro")
        print("Taxation département ->", self.montant_taxation, "euro")
        print("--------------------------------------------")
        print("Le montant total est donc de :", sum_total, "euro")
        print("--------------------------------------------")


if __name__ == '__main__':
    HT_Transport = Calcul_HT_Transport()
    HT_Transport.main()    
