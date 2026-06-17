#Importaciones
import pandas as pd
from itertools import product

def texto_principal(ppio_1, ppio_2, riesgo, DDI):
    '''
    Devuelve el texto que se fijará en la parte de arriba

    Parámetros
    ------------------------
        ppio_1 - El primer principio activo que se quiere comparar con el segundo
        ppio_2 - El segundo principio activo que se quiere comparar con el primero
        riesgo - Cadena de texto que indica el nivel de riesgo en la interaccion (Alta, Media, Leve)
        DDI - Dataframe que contiene los nombres, ATC, enzimas, target, acciones y prioridad
    Devolución
    ---------------
        texto - cadena de texto explicativa
    '''
    #Inicializo la cadena de texto
    texto = ""

    #Cuando no se encuentra alguno de los principios se muestra en pantalla ese error
    if (ppio_1 not in DDI["ppio_normalizado"].values):
        texto += f"{ppio_1} no se ha encontrado en la base de datos, porfavor introduce otro y vuelve a pulsar el boton analizar.\n\n"
        
    elif (ppio_2 not in DDI["ppio_normalizado"].values):
        texto += f"{ppio_2} no se ha encontrado en la base de datos, porfavor introduce otro y vuelve a pulsar el boton analizar.\n\n"

    #Sino, se muestra el nivel de riesgo de la interacción
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
    dic_resumen = {}
    #Comprobamos primero que esté en nuestra BBDD
    if (ppio_1 in DDI["ppio_normalizado"].values) and (ppio_2 in DDI["ppio_normalizado"].values):
        
        #Conseguimos la lista de enzimas por las que se metaboliza cada principio y las principales en todo caso de haber
        df_1 = DDI[DDI["ppio_normalizado"] == ppio_1]
        enz_1, ppal_1 = principales(df_1)
        df_2 = DDI[DDI["ppio_normalizado"] == ppio_2]
        enz_2, ppal_2 = principales(df_2)
            
        #Sabiendo que está saber si tiene principales o no
        intro_1 = texto_intro(ppio_1, enz_1, ppal_1) 
        intro_2 = texto_intro(ppio_2, enz_2, ppal_2)
    
        #Comparamos con las ppales o con la lista de enzimas dependiendo si hay principal o nop
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
                            #Si ya existe el codigo de referencia
                            if codigo_referencia in ref_1:
                                comprobante = True
                            else:
                                #Obtengo los nombres de los principios que sirven como alternativa si no estan en el diccionario
                                principios_1 = DDI[DDI['Drug_ATC'].str.startswith(codigo_referencia, na=False)]["Drug_name"].unique().tolist()
                                #Elimino el principio de la lista para que esté vacía si solo existe el principio en ella.
                                principios_1 = [x for x in principios_1 if x.strip().casefold() != ppio_1]
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
                            #Si ya existe el codigo de referencia
                            if codigo_referencia in ref_2:
                                comprobante = True
                            else:
                                #Obtengo los nombres de los principios que sirven como alternativa si no estan en el diccionario
                                principios_2 = DDI[DDI['Drug_ATC'].str.startswith(codigo_referencia, na=False)]["Drug_name"].unique().tolist()
                                #Elimino el principio de la lista para que esté vacía si solo existe el principio en ella.
                                principios_2 = [x for x in principios_2 if x.strip().casefold() != ppio_2]
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


#TENGO QUE SEPARAR LOS ATC POR CODIGOS DE REF
#Como casos limite coger uno que no tenga opcion con las 5 primeras letras
#Otro caso limite: sin codigo ATC
#Y si tienen los dos el mismo codigo de referencia de ATC? EL SEGUNDO QUE SALGA NO SE UNE TAL Y COMO LO TENGO PUESTO AHORA

#Devolver dos en el boton de opciones atc, las opciones y el texto
def opciones_ATC(alternativas_1, alternativas_2, ppio_1, ppio_2, DDI):
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
    #Inicializo opciones
    opciones = []
    #Añado los principios activos, porsiacaso aunque deberian estar, incluso aunque no haya ninguna otra opcion el ppio activo smp estará, tengo q cambiar eso antes creo yo
    alt_1 = list(set(alternativas_1 + [ppio_1]))
    alt_2 = list(set(alternativas_2 + [ppio_2]))
    #Combinatoria
    #Deberia sacar combinatorias de ATC por separado dependiendo de su ATC concreto?? igual poner en un diccionario SI
    for p1,p2 in product(alt_1, alt_2):
        p1 = p1.strip().casefold()
        p2 = p2.strip().casefold()
        diccionario = interaccion (p1, p2, DDI)
        if not diccionario:
            continue
        if diccionario["riesgo"]=="Leve":
            #Tupla
            opciones = opciones + [(p1,p2)]

    #Cambiar opciones
    return opciones  


def texto_intro (ppio, enzimas, principales, texto=False, primero=False):
    '''
    Texto de introducción de el principio activo concreto (explica las enzimas)

    Parámetros
    ------------------------
        ppio - Principio activo que se va a describir
        enzimas - Lista con las enzimas por las que se metaboliza el ppio activo según la BBDD consultada
        principales - Lista con las enzimas principales (si las hay) por las que se metaboliza el ppio activo según las FT de CIMA con chat y notebook
        texto - Booleano, por defecto false
        primero - Un booleano, por defecto en False que indica si es la primera vez que se ejecuta el texto o no para imprimir la introducción

    Devolución
    ---------------
        True cuando hay enzima principal, False cuando no y None cuando no es ninguna tenida en cuenta o no se metaboliza por una enzima (según DrugBank)
    '''
    #Cuando quiera devolver texto
    cadena = ""
    #Si no hay lista de enzimas se devuelve None
    booleano = None
    #Si es la primera vez que ejecuta se muestran explicaciones clave principales
    if primero:
        cadena += "En esta web vamos a indicar si existe una interacción LEVE, MEDIA o ALTA basandonos en las enzimas por las que se metabolizan cada uno de los principios activos consultados en la base de datos de DrugBank\n"
        cadena += "Se muestran solo las interacciones en la primera ingesta del principio activo, debido se desconocen los efectos a largo plazo de los principios.\n\n"
        cadena += "Solo se han tenido en cuenta las siguientes enzimas: [CYP2D6, CYP3A4, CYP3A5, CYP2C19, CYP2C9, CYP1A2] que según DrugBank son las 5 por las que se metabolizan mas principios activos. Teniendo en cuenta tambien la CYP3A5 que es como la CYP3A4 (CAMBIO), sin embargo cuando ambas mencionadas previamente se consideraban principales, la CYP3A5 era eliminada debido a  que la mayoria de la pobalcion no expresa esta enzima.\n\n\n"

    #Si no hay lista de enzimas
    if not enzimas:
        cadena += f"El principio activo: {ppio} no se metaboliza por ninguna enzima de las tenidas en cuenta según la base de datos de DrugBank, por tanto la interacción con cuaquier otro principio activo consultado aparecerá categorizada como LEVE.\n\n"
    else:
        #Si solo hay una enzima es la principal
        if len(enzimas) == 1:
            cadena += f"El principio activo: {ppio} solo se metaboliza por una enzima de las que se tienen en cuenta, la cual hemos considerado como enzima de metabolización principal del principio activo.\n\n"
            booleano = True
        else:
            #Si no tiene principales (al menos de las tenidas en cuenta)
            if not principales:
                cadena += f"El principio activo: {ppio} se metaboliza por las siguientes enzimas: {enzimas}, no se ha podido determinar la enzima principal por la que se metaboliza, por tanto las interacciones mostradas a continuacion serán con cada una de ellas.\n\n"
                booleano = False

            else:
                #Cuando solo hay una principal
                if len(principales) == 1:
                    cadena += f"El principio activo: {ppio} se metaboliza por las enzimas: {enzimas} de las cuales, se ha considerado principal: {principales}, en las siguientes descripciones se mostrarán las interacciones solo con dicha enzima considerada principal.\n\n"
                    booleano = True
                else:
                    #Cuando hay varias principales
                    cadena += f"El principio activo: {ppio} se metaboliza por las enzimas: {enzimas}, de las cuales se han considerado principales las siguientes: {principales}, en las siguientes descripciones se mostrarán las interacciones solo con dichas enzimas consideradas principales.\n\n"
                    booleano = True

    if texto:
        return cadena
    else:
        return booleano



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
    cadena = ""
    riesgo = None 
    #Si hay coincidentes hay interaccion
    if coincidentes:
        #Si las dos tienen principal
        if intro_1 and intro_2:
            cadena += f"La interacción {ppio_1}-{ppio_2} es considerada Alta.\n"
            cadena += f"Como ambos principios son metabolizados por enzimas tenidas en cuenta que tienen alguna enzima considerada principal y estas coinciden entre si en las siguientes: {coincidentes} es considerada como interacción alta.\n\n"
            riesgo = "Alta"
        else:
            #Si al menos una no es principal la interaccion es consderada media
            cadena += f"La interacción {ppio_1}-{ppio_2} es considerada Media.\n"
            cadena += f"Como no sabemos las enzimas principales de por lo menos uno de los dos principios activos pero coinciden en la metabolización de las siguientes enzimas: {coincidentes} su interacción es considerada Media.\n\n"
            riesgo = "Media"

    else:
        #Si no hay coincidentes lo consideramos como sin interaccion, categorizado como Leve
        cadena += f"La interacción {ppio_1}-{ppio_2} es considerada Leve.\n"
        cadena += "Los principios activos no coinciden en ser metabolizados por ninguna enzima de las tenidas en cuenta y por tanto su interacción es categorizada como Leve.\n\n"

        riesgo = "Leve"

    if texto:
        return cadena
    else:
        return riesgo


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
    cadena = ""
    #Print explicativo
    cadena += f"En este caso solo se describen las interacciones de los principios activos con la enzima: {enzima} teniendo en cuenta solo que lleven a cabo algunas de las siguientes acciones: {posibilidades}.\n\n"
    
    #De las listas proporcionadas con las acciones UNICAS eliminamos las que no tenemos en cuenta:
    mias_1 = [x for x in acc_1 if x in posibilidades]
    mias_2 = [x for x in acc_2 if x in posibilidades]

    #Guardamos una variable con las coincidencias de las acciones (sustrato-sustrato, inhib-inhib, induct-induct)
    #Se supone que ya deben de ser las distintas pero porsiacaso set
    doble = list(set(mias_1) & set(mias_2))
    #Lo traducimos al español para el print
    esp = [traduccion[x] for x in doble]

    #Una vez declaramos las variables comprobamos cada uno de los casos para obtener el texto adecuado
    if not acc_1 or not acc_2:
        cadena += f"Las acciones de la enzima {enzima} para los principios activos {ppio_1} y {ppio_2} no están registradas en DrugBank, por tanto no se puede describir la interacción que tienen.\n\n"
        
    else:
        #De la lista ninguna es inductor-inhibidor-sustrato
        if (not mias_1) or (not mias_2):
            cadena += f"De las acciones que se llevan a cabo con la enzima: {enzima} en los dos principios activos consulltados: {ppio_1} y {ppio_2} ninguna es de las tenidas en cuenta, por tanto no se puede describir la interacción.\n\n"

        else:
            if doble:
                #Es posible que doble tenga mas de una acción ¿QUE HACES EN ESE CASO?, con que se tenga una que coincida pues vale supongo
                cadena += f"Para la enzima: {enzima} los dos principios activos consultados actuan como: {esp} por tanto competirán al mismo nivel, lo que quiere decir que ninguno tendrá prevalencia sobre el otro a la hora de metabolizarse.\n\n"

            else:
                #Texto genérico que describe interaccion
                if len(mias_1)==1 and len(mias_2)==1:
                    a1 = traduccion[mias_1[0]]
                    a2 = traduccion[mias_2[0]]
                    preval = competicion.get((a1,a2))
                    cadena += f"Para la enzima: {enzima} el principio activo: {ppio_1} esta actuando como: {a1}, mientras que el principio activo: {ppio_2} está actuando como: {a2}, en este caso tiene prevalencia de metabolización el {preval}.\n"
                else:
                    cadena += f"Como alguno de los dos principios activos consultados poseen mas de una acción en la base de datos consultada para la enzima: {enzima} no es posible determinar si alguno de los dos tiene prioridad de metabolizacion.\n"
                    cadena += f"Para el principio: {ppio_1} las acciones registradas son:{mias_1}.\n"
                    cadena += f"Para el principio: {ppio_2} las acciones registradas son:{mias_2}.\n"
                    
    return cadena



#Los efectos salen en ingles porque la bbdd consultada es en ingles
#Cambiar descripcion
def texto_efectos (lista_ATC, ref, efectos_adversos, ppio):
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
    
    #Vemos cuales son los codigos ATC que tienen cada codigo de referencia (5 letras al principio)
    ATCs = [x for x in lista_ATC if str(x).startswith(ref)]
    
    if not ATCs:
        return pd.DataFrame()

    df = efectos_adversos[efectos_adversos["Drug_ATC"].isin(ATCs)]
    #Para solo un codigo de referencia saco los 10 efectos adversos mas comunes sacados de SIDDER ordenados por mayor frecuencia
    #Si hay un efecto que esta dos veces se calcula la media de las dos frecuencias y se tiene en cuenta esa
    final = (
        df.groupby("Side_effect", as_index=False)["Freq_media"]
        .mean()
        .sort_values(by="Freq_media", ascending=False)
    )

    return final.head(10)

