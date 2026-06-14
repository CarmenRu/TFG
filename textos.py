#Importaciones
import pandas as pd
from itertools import product

def texto_principal(ppio_1, ppio_2, riesgo):
    '''

    '''
    texto = ""
    
    if (ppio_1 not in DDI["ppio_normalizado"].values):
        texto += f"{ppio_1} no se ha encontrado en la base de datos, porfavor introduce otro y vuelve a pulsar el boton analizar.\n\n"
        #Dar posibles opciones??
    elif (ppio_2 not in DDI["ppio_normalizado"].values):
        texto += f"{ppio_2} no se ha encontrado en la base de datos, porfavor introduce otro y vuelve a pulsar el boton analizar.\n\n"
        #Dar posibles opciones?
    else:
        texto += f"Nivel de riesgo: {riesgo}.\n\n"
        
    return texto
    
def principales(df):
    '''
    Busca la lista de las enzimas por las que se metaboliza un principio activo y sus principales en todo caso de haber.

    Parametros
    ------------------
        df- Solo incluye las filas con el ppio activo concreto que estemos consultando
    Devolución
    -----------------------------
        enz - Lista de enzimas por las que se metaboliza el principio activo
        ppal - Lista de enzimas principales por las que se metaboliza el fármaco (prioridad=1)
    '''
    #df con todas las enzimas por las que se metaboliza (no target)
    df_enzimas = df[df["Tipo"]=="enzyme"]
    # Lista de enzimas unicas por las que se metaboliza el ppio
    enz = df_enzimas["Gene_name"].unique().tolist()      
    #Lista de enzimas principales (si tiene) el ppio (categorizadas como 1)
    ppal = df_enzimas[df_enzimas["Prioridad"]==1]["Gene_name"].unique().tolist()

    return enz, ppal


def interaccion (ppio_1, ppio_2, DDI):
    '''
    Funcion que determina si existe interacción entre los dos principios activos o no.
    Ademas si texto, describe: cada principio y sus enzimas, 
    
    Parámetros
    -----------------
        ppio_1 - El primer principio activo que se quiere comparar con el segundo
        ppio_2 - El segundo principio activo que se quiere comparar con el primero
        DDI - Dataframe que contiene los nombres, ATC, enzimas, target, acciones y prioridad
    Devolucion
    ------------------
        String con el nivel de riesgo Leve, Medio y Alto
    '''
    #Comprobamos primero que esté en nuestra BBDD
    if (ppio_1 in DDI["ppio_normalizado"].values) and (ppio_2 in DDI["ppio_normalizado"].values):
        df_1 = DDI[DDI["ppio_normalizado"] == ppio_1]
        enz_1, ppal_1 = principales(df_1)
        
        df_2 = DDI[DDI["ppio_normalizado"] == ppio_2]
        enz_2, ppal_2 = principales(df_2)
            
        #Sabiendo que está, no queremos texto
        intro_1 = texto_intro(ppio_1, enz_1, ppal_1) 
        intro_2 = texto_intro(ppio_2, enz_2, ppal_2)
    
        #Comparamos con las ppales o con la lista de enzimas
        if intro_1:
            comparo1 = ppal_1
        else:
            comparo1 = enz_1
        if intro_2:
            comparo2 = ppal_2
        else:
            comparo2 = enz_2
        #Aqui compruebo si hay interaccion o no
        coincidentes = list(set(comparo1) & set(comparo2))
        #Calculamos el riesgo y si se desea texto imprime el nivel de riesgo que tendrán
        riesgo = calcular_riesgo(ppio_1, ppio_2,coincidentes, intro_1, intro_2)

        if riesgo=="Alta" or riesgo=="Media":
            ATC_1 = df_1["Drug_ATC"].unique().tolist()
            ATC_2 = df_2["Drug_ATC"].unique().tolist()
            ref_1 = []
            ref_2 = []
            #Poner opcion de introducir codigo ATC?
            if ATC_1:
                for ATC in ATC_1:
                    comprobante = False
                    #Cogemos los 5 primeras letras del ATC
                    i=5
                    while comprobante==False :
                        #Si hemos llegado a i=0 es que no hay mas codigos atc que comprobar
                        if i!=0:
                            #En principio uso las 5 primeras letras del codigo ATC, luego voy bajando si no se encuentran opciones
                            codigo_referencia = ATC[:i]
                            #Para asegurarnos de que la lista al principio está vacía (anteriores búsquedas)
                            principios_1 = []
                            #Obtengo los nombres de los principios que sirven como alternativa si no estan en el diccionario
                            if codigo_referencia not in ref_1:
                                principios_1 = DDI[DDI['Drug_ATC'].str.startswith(codigo_referencia, na=False)]["Drug_name"].unique().tolist()
                            #Si hay principios que coincidan con el codigo de referencia lo guardo
                            if principios_1:
                                ref_1.append(codigo_referencia)
                                #Establezco el comprobante a True
                                comprobante = True
                            
                        else:
                            #Finalizamos el bucle
                            comprobante = True
                            
                        #Si no hay principios uso una letra menos de la q estaba usando 
                        i-=1
                    
            #Segundo ppio
            if ATC_2:
                for ATC in ATC_2:
                    comprobante = False
                    #Cogemos los 5 primeras letras del ATC
                    i=5
                    while comprobante==False :
                        #Si hemos llegado a i=0 es que no hay mas codigos atc que comprobar
                        if i!=0:
                            #En principio uso las 5 primeras letras del codigo ATC, luego voy bajando si no se encuentran opciones
                            codigo_referencia = ATC[:i]
                            #Para asegurarnos de que la lista al principio está vacía (anteriores búsquedas)
                            principios_2 = []
                            #Obtengo los nombres de los principios que sirven como alternativa si no estan en el diccionario
                            if codigo_referencia not in ref_2:
                                principios_2 = DDI[DDI['Drug_ATC'].str.startswith(codigo_referencia, na=False)]["Drug_name"].unique().tolist()
                            #Si hay principios que coincidan con el codigo de referencia lo guardo
                            if principios_2:
                                ref_2.append(codigo_referencia)
                                #Establezco el comprobante a True
                                comprobante = True
                            
                        else:
                            #Finalizamos el bucle
                            comprobante = True
                            
                        #Si no hay principios uso una letra menos de la q estaba usando 
                        i-=1

        else:
            ATC_1 = []
            ATC_2 = []
            ref_1 = []
            ref_2 = []
        #Mas explicito 
        dic_resumen = {"p1" : ppio_1,
                       "p2" : ppio_2,
                       
                       "df1" : df_1.to_dict("records"),
                       "df2" : df_2.to_dict("records"),
                       
                       "enz1" : enz_1,
                       "enz2" : enz_2,
                       
                       "ppal1" : ppal_1,
                       "ppal2" : ppal_2,
                       
                       "ATC1" : ATC_1,
                       "ATC2" : ATC_2,
                       
                       "ref1" : ref_1,
                       "ref2" : ref_2,
                       
                       "interaccion" : coincidentes,
                       "riesgo" : riesgo
                      }
    
    return dic_resumen

#TENGO QUE DEVOLVER LOS ATC DE REFERENCIA
#Si no fuera asi meteria aqui los efectos adversos pero no <3
def opciones_ATC(DDI, ATC_1, ATC_2, ppio_1, ppio_2):
    """
    Busqueda en la base de datos de opciones con el código ATC de los principios activos problema

    Parámetos
    -------------------------
        DDI - Dataframe que contiene los nombres, ATC, enzimas, target, acciones y prioridades
        ATC_1 - Lista con los códigos ATC únicos del ppio_1
        ATC_2 - Lista con los códigos ATC únicos del ppio_2
        ppio_1 - El primer principio activo que se quiere comparar con el segundo
        ppio_2 - El segundo principio activo que se quiere comparar con el primero
        
    Devolución
    ---------------------------
        #Deberia ser un diccionario HAY QUE CAMBIARLO
        Lista de tuplas con los dos principios activos de alternativa a cada uno que estan categorizados como interaccion leve
    """
    opciones = []
    #Alternativas 1 y 2
    alternativas_1 = []
    alternativas_2 = []
    
    #Primer ppio
    if not ATC_1:
#       #Poner opcion de introducir codigo ATC?
        print(f"No ha sido posible buscar alternativas del principio activo: {ppio_1} debido a que no hay datos de cual es su código ATC")
    else:
        for ATC in ATC_1:
            comprobante = False
            #Cogemos los 5 primeras letras del ATC
            i=5
            while comprobante==False :
                #Si hemos llegado a i=0 es que no hay mas codigos atc que comprobar
                if i!=0:
                    #En principio uso las 5 primeras letras del codigo ATC
                    codigo_referencia = ATC[:i]
                    #Obtengo los nombres de los principios que sirven como alternativa
                    principios_1 = DDI[DDI['Drug_ATC'].str.startswith(codigo_referencia, na=False)]["Drug_name"].unique().tolist()
                    
                    if principios_1:
                        #Junto las listas para obtener unas con todas las alternativas del primer principio
                        alternativas_1 = alternativas_1 + principios_1
                        #Imprimo las diferentes alternativas
                        print(f"Para el principio: {ppio_1} con código ATC: {ATC} existen las siguientes alternativas:{principios_1} con código de referencia:{codigo_referencia}")
                        #Establezco el comprobante a True
                        comprobante=True
                    
                else:
                    print(f"No ha sido posible encontrar una opción factible para el principio: {ppio_1} con los códigos ATC")
                    break
                    
                #Si no hay principios uso una letra menos de la q estaba usando 
                i-=1
            
    #Segundo ppio
    if not ATC_2:
        #Poner opcion de introducir codigo ATC?
        print(f"No ha sido posible buscar alternativas del principio activo: {ppio_2} debido a que no hay datos de cual es su código ATC")
    else:
        for ATC in ATC_2:
            comprobante = False
            #Cogemos los 5 primeras letras del ATC
            i=5
            while comprobante==False :
                #Si hemos llegado a i=0 es que no hay mas codigos atc que comprobar
                if i!=0:
                    #En principio uso las 5 primeras letras del codigo ATC
                    codigo_referencia = ATC[:i]
                    #Obtengo los nombres de los principios que sirven como alternativa
                    principios_2 = DDI[DDI['Drug_ATC'].str.startswith(codigo_referencia, na=False)]["Drug_name"].unique().tolist()
                    
                    if principios_2:
                        #Junto las listas para obtener unas con todas las alternativas del primer principio
                        alternativas_2 = alternativas_2 + principios_2
                        #Imprimo las diferentes alternativas
                        print(f"Para el principio: {ppio_2} con código ATC: {ATC} existen las siguientes alternativas:{principios_2} con código de referencia:{codigo_referencia}")
                        #Establezco el comprobante a True
                        comprobante=True
                    
                else:
                    print(f"No ha sido posible encontrar una opción factible para el principio: {ppio_2} con los códigos ATC")
                    break
                    
                #Si no hay principios uso una letra menos de la q estaba usando 
                i-=1
                
    #Si hay elementos en al menos uno de los dos, comprobamos la interaccion de las combinaciones
    if alternativas_1 or alternativas_2:
        #Añado los principios activos
        alternativas_1 = list(set(alternativas_1 + [ppio_1]))
        alternativas_2 = list(set(alternativas_2 + [ppio_2]))
        print()
        print(alternativas_1)
        print(alternativas_2)
        #Combinatoria
        #Deberia sacar combinatorias de ATC por separado dependiendo de su ATC concreto?? igual poner en un diccionario SI
        for comb in product(alternativas_1, alternativas_2):
            interac = interaccion(comb[0], comb[1], DDI)
            if interac=="Leve":
                opciones = opciones + [comb]
        print()
        print()
        print(f"Las posibles combinaciones resultantes son:{opciones}")

    else:
        print("No ha habido ninguna combinacion factible")
        #Es posible que aqui pueda volver a llamar a la funcion pero con un número menos de i???

    return opciones

def texto_intro (ppio, enzimas, principales, texto, primero=False):
    '''
    Texto de introducción de el principio activo concreto

    Parámetros
    ------------------------
        ppio - Principio activo que se va a describir
        enzimas - Lista con las enzimas por las que se metaboliza el ppio activo según la BBDD consultada
        principales - Lista con las enzimas principales (si las hay) por las que se metaboliza el ppio activo según las FT de CIMA con chat y notebook
        primero - Un booleano, por defecto en False que indica si es la primera vez que se ejecuta el texto o no para imprimir la introducción

    Devolución
    ---------------
        True cuando hay enzima principal, False cuando no y None cuando no es ninguna tenida en cuenta o no se metaboliza por una enzima (según DrugBank)
    '''
    #Si es la primera vez que ejecuta se muestran explicaciones clave principales
    if primero:
        if texto:
            print("En esta web vamos a indicar si existe una interacción LEVE, MEDIA o ALTA basandonos en las enzimas por las que se metabolizan cada uno de los principios activos consultados en la base de datos de DrugBank")
            print("Se muestran solo las interacciones en la primera ingesta del principio activo, debido se desconocen los efectos a largo plazo de los principios.")
            print()
            print("Solo se han tenido en cuenta las siguientes enzimas: [CYP2D6, CYP3A4, CYP3A5, CYP2C19, CYP2C9, CYP1A2] que según DrugBank son las 5 por las que se metabolizan mas principios activos. Teniendo en cuenta tambien la CYP3A5 que es como la CYP3A4 (CAMBIO), sin embargo cuando ambas mencionadas previamente se consideraban principales, la CYP3A5 era eliminada debido a  que la mayoria de la pobalcion no expresa esta enzima.")
            print()
            print()
    #Si no hay lista de enzimas
    if not enzimas:
        if texto:
            print(f"El principio activo: {ppio} no se metaboliza por ninguna enzima de las tenidas en cuenta según la base de datos de DrugBank, por tanto la interacción con cuaquier otro principio activo consultado aparecerá categorizada como LEVE")
            print()
    else:
        #Si solo hay una enzima es la principal
        if len(enzimas) == 1:
            if texto:
                print(f"El principio activo: {ppio} solo se metaboliza por una enzima de las que se tienen en cuenta, la cual hemos considerado como enzima de metabolización principal del principio activo")
                print()
            return True
        else:
            #Si no tiene principales (al menos de las tenidas en cuenta)
            if not principales:
                if texto:
                    print(f"El principio activo: {ppio} se metaboliza por las siguientes enzimas: {enzimas}, no se ha podido determinar la enzima principal por la que se metaboliza, por tanto las interacciones mostradas a continuacion serán con cada una de ellas")
                    print()
                return False

            else:
                #Cuando solo hay una principal
                if len(principales) == 1:
                    if texto:
                        print(f"El principio activo: {ppio} se metaboliza por las enzimas: {enzimas} de las cuales, se ha considerado principal: {principales}, en las siguientes descripciones se mostrarán las interacciones solo con dicha enzima considerada principal")
                        print()
                    return True
                else:
                    #Cuando hay varias principales
                    if texto:
                        print(f"El principio activo: {ppio} se metaboliza por las enzimas: {enzimas}, de las cuales se han considerado principales las siguientes: {principales}, en las siguientes descripciones se mostrarán las interacciones solo con dichas enzimas consideradas principales")
                        print()
                    return True
                    
    return None



def calcular_riesgo (ppio_1, ppio_2,coincidentes, intro_1, intro_2, texto=False):
    """
    Evalua el nivel de riesgo de la posible interacción

    Parámetros
    ---------------------
        ppio_1 - El primer principio activo que se quiere comparar con el segundo
        ppio_2 - El segundo principio activo que se quiere comparar con el primero
        coincidentes - lista que contiene las enzimas que coinciden en las listas de enzimas del ppio 1 y 2
        intro_1 - True si el ppio_1 tiene principales, False si no
        intro_2 - True si el ppio_2 tiene principales, False si no
        texto - Si es necesaria la impresión de texto o no (para comparar el ATC no lo es), por defecto a False

    Devolución
    ---------------------------
        string que contiene "Alta","Media","Leve" dependiendo de cual sea su nivel de riesgo
    """
    #Si hay coincidentes hay interaccion
    if coincidentes:
        #Si las dos tienen principal
        if intro_1 and intro_2:
            if texto:
                print(f"La interacción {ppio_1}-{ppio_2} es considerada Alta")
                print(f"Como ambos principios son metabolizados por enzimas tenidas en cuenta que tienen alguna enzima considerada principal y estas coinciden entre si en las siguientes: {coincidentes} es considerada como interacción alta")
                print()
            return "Alta"
        else:
            #Si al menos una no es principal la interaccion es consderada media
            if texto:
                print(f"La interacción {ppio_1}-{ppio_2} es considerada Media")
                print(f"Como no sabemos las enzimas principales de por lo menos uno de los dos principios activos pero coinciden en la metabolización de las siguientes enzimas: {coincidentes} su interacción es considerada Media")
                print()
            return "Media"

    else:
        #Si no hay coincidentes lo consideramos como sin interaccion, categorizado como Leve
        if texto:
            print(f"La interacción {ppio_1}-{ppio_2} es considerada Leve")
            print("Los principios activos no coinciden en ser metabolizados por ninguna enzima de las tenidas en cuenta y por tanto su interacción es categorizada como Leve")
            print()
        return "Leve"


def texto_acciones (ppio_1, acc_1, ppio_2, acc_2, enzima):
    """
    Se describe la interaccion solo con la enzima concreta que se pasa por parámetro

    Parámetros
    --------------------
        ppio_1 - El primer principio activo que se quiere comparar con el segundo
        acc_1 - Lista de acciones de la enzima coincidente en el ppio 1
        ppio_2 - El segundo principio activo que se quiere comparar con el primero
        acc_2 - Lista de acciones de la enzima coincidente en el ppio 2
        enzima - La enzima coincidente en ambos principios activos

    Devolución
    --------------------
        None
    """
    #Diccionario con la traducción de cada una de las acciones tenidas en cuenta
    traduccion = {"substrate":"sustrato",
              "inhibitor":"inhibidor",
              "inducer":"inductor"}
    #Declaramos cuales son las posibilidades
    posibilidades = [x for x in traduccion]
    #Diccionario que dicta la prevalencia ante dos acciones de las tenidas en cuenta
    competicion = {("sustrato","inductor"):"sustrato", ("inductor", "sustrato"):"sustrato",
           ("sustrato","inhibidor"):"inhibidor",("inhibidor","sustrato"):"inhibidor",
           ("inductor","inhibidor"):"inhibidor",("inhibidor","inductor"):"inhibidor"}
    
    #Print explicativo
    print(f"En este caso solo se describen las interacciones de los principios activos con la enzima: {enzima} teniendo en cuenta solo que lleven a cabo algunas de las siguientes acciones: {posibilidades}")
    print()
    
    #De las listas proporcionadas con las acciones UNICAS eliminamos las que no tenemos en cuenta:
    mias_1 = [x for x in acc_1 if x in posibilidades]
    mias_2 = [x for x in acc_2 if x in posibilidades]

    #Guardamos una variable con las coincidencias de las acciones (sustrato-sustrato, inhib-inhib, induct-induct)
    #Se supone que ya deben de ser las distintas pero porsiacaso set
    doble = list(set(mias_1) & set(mias_2))
    #Lo traducimos al español para el print
    esp = [traduccion[x] for x in doble]

    #Una vez declaramos las variables comprobamos cada uno de los casos para obtener el texto adecuado
    #Aunque se ha comprobado (en jupyter) que no hay elementos nulos en las acciones cuando la BBDD queda reducida a solo los que tienen enzimas se comprueba
    if (acc_1==None) or (acc_2==None):
        print(f"Las acciones de la enzima {enzima} para los principios activos {ppio_1} y {ppio_2} no están registradas en DrugBank, por tanto no se puede describir la interacción que tienen.")
        print()
        
    else:
        #De la lista ninguna es inductor-inhibidor-sustrato
        if (not mias_1) or (not mias_2):
            print(f"De las acciones que se llevan a cabo con la enzima: {enzima} en los dos principios activos consulltados: {ppio_1} y {ppio_2} ninguna es de las tenidas en cuenta, por tanto no se puede describir la interacción.")
            print()

        else:
            if esp:
                #Es posible que doble tenga mas de una acción ¿QUE HACES EN ESE CASO?, con que se tenga una que coincida pues vale supongo
                print(f"Para la enzima: {enzima} los dos principios activos consultados actuan como: {doble} por tanto competirán al mismo nivel, lo que quiere decir que ninguno tendrá prevalencia sobre el otro a la hora de metabolizarse ")
                print()

            else:
                #Texto genérico que describe interaccion
                if len(mias_1)==1 and len(mias_2)==1:
                    a1 = traduccion[mias_1[0]]
                    a2 = traduccion[mias_2[0]]
                    preval = competicion[(a1,a2)]
                    print(f"Para la enzima: {enzima} el principio activo: {ppio_1} esta actuando como: {a1}, mientras que el principio activo: {ppio_2} está actuando como: {a2}, en este caso tiene prevalencia de metabolización el {preval}")
                else:
                    print(f"Como alguno de los dos principios activos consultados poseen mas de una acción en la base de datos consultada para la enzima: {enzima} no es posible determinar si alguno de los dos tiene prioridad de metabolizacion")
                    print(f"Para el principio: {ppio_1} las acciones registradas son:{mias_1}")
                    print(f"Para el principio: {ppio_2} las acciones registradas son:{mias_2}")



#Los efectos salen en ingles porque la bbdd consultada es en ingles
def texto_efectos (lista_ATC, ATC_ref, efectos_adversos, ppio):
    '''
    Imprime una tabla con los top 10 efectos adversos que esten asociados con los codigos ATC de cada uno de los principios (por separado)

    Parámetros
    -----------------
        lista_ATC - Lista con los códigos ATC del principio activo para el que se estén consultando los efectos adversos
        ATC_ref - Los codigos ATC (en caso de haber mas de uno) cogidos como referencia anteriormente para las alternativas
        efectos_adversos - csv que contiene los efectos adversos prdenados por código ATC
        ppio - Nombre del principio activo del que se van a sacar los efectos adversos asociados

    Devolución
    ------------------
        None
    '''
    #Si no hay ATC de referecncia significa que no se ha encontrado ninguna alternativa
    if len(ATC_ref)==0:
        print(f'No se ha podido encontar ninguna alternativa para el principio: {ppio}')
    
    else:
        #Sino, por cada ATC de referencia de el principio concreto
        for ref in ATC_ref:
            #Vemos cuales son los codigos ATC que tienen cada codigo de referencia (5 letras al principio)
            ATCs = [x.str.startswith(ref, na=False) for x in lista_ATC]
            #Inicializamos el contador
            cont = 0

            #Por cada uno de los codigos ATC asociados al de referencia sacamos sus efectos adversos
            for uno in ATCs:
                #Si es el primero determina df
                if cont == 0:
                    df = efectos_adversos[efectos_adversos["Drug_ATC"]==uno]
                else:
                    #Cuando no es el primero determina nuevo
                    nuevo = efectos_adversos[efectos_adversos["Drug_ATC"]==uno]
                    #Los uno
                    union = pd.concat([df, nuevo], ignore_index=True)
                    #Y cambio la variable df
                    df = union
                #Cambiamos el contador
                cont+=1

            #Para solo un codigo de referencia saco los 10 efectos adversos mas comunes sacados de SIDDER ordenados por mayor frecuencia
            #Si hay un efecto que esta dos veces se calcula la media de las dos frecuencias y se tiene en cuenta esa
            final = (
                union.groupby('Side_effect', as_index=False)['Freq_media']
                .mean()
            ).sort_values(by="Freq_media", ascending=False)

            print(f"Para el principio activo: {ppio} con codigo ATC de referencia: {ref} los 10 posibles efectos adversos mas comunes son:")
            final.head(10)
            print()
            print()






'''
#Pruebas con casos limite
ppio_1 = "Omeprazole"
ppio_2 = "Clopidogrel"
existe = interaccion (ppio_1, ppio_2, DDI, efectos, texto=True)
if existe=="Alta" or existe=="Media":
    df_1 = DDI[DDI["Drug_name"] == ppio_1]   
    ATC_1 = df_1["Drug_ATC"].unique()
    df_2 = DDI[DDI["Drug_name"] == ppio_2]
    ATC_2 = df_2["Drug_ATC"].unique()
    opciones_ATC(DDI, efectos, ATC_1, ATC_2, ppio_1, ppio_2)
'''