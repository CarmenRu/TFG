#O poner un texto en cada funcion de texto y ejecutar con el boton?


#Cuando no hay enzimas por las que se metaboliza se tendrá en cuenta en si hay interacción o no? --------> SE HA TENIDO EN CUENTA COMO LEVE TAMBIEN
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
    #SE MUESTRAN SOLO LAS INTERACCIONES EN LA PRIMERA INGESTA, PONER ESO
    if primero:
        if texto:
            print("En esta web vamos a indicar si existe una interacción LEVE, MEDIA o ALTA basandonos en las enzimas por las que se metabolizan cada uno de los principios activos consultados en la base de datos de DrugBank")
            print()
            print("Solo se han tenido en cuenta las siguientes enzimas: [CYP2D6, CYP3A4, CYP3A5, CYP2C19, CYP2C9, CYP1A2] que según DrugBank son las 5 por las que se metabolizan mas principios activos. Teniendo en cuenta tambien la CYP3A5 que es como la CYP3A4 (CAMBIO), sin embargo cuando ambas mencionadas previamente se consideraban principales, la CYP3A5 era eliminada debido a  que la mayoria de la pobalcion no expresa esta enzima.")
            print()
            print()
        
    if not enzimas:
        if texto:
            print(f"El principio activo: {ppio} no se metaboliza por ninguna enzima de las tenidas en cuenta según la base de datos de DrugBank, por tanto la interacción con cuaquier otro principio activo consultado aparecerá categorizada como LEVE")
            print()
    else:
        
        if len(enzimas) == 1:
            if texto:
                print(f"El principio activo: {ppio} solo se metaboliza por una enzima de las que se tienen en cuenta, la cual hemos considerado como enzima de metabolización principal del principio activo")
                #Aunque no tiene porque ser asi porque puede tener otra via principal de metabolizacion de enzimas no tenidas en cuenta, que pasaba con las fichas tecnicas de CIMA (salian otras enzimas de no mencionadas)
                print()
            return True
        else:
            
            if not principales:
                if texto:
                    print(f"El principio activo: {ppio} se metaboliza por las siguientes enzimas: {enzimas}, no se ha podido determinar la enzima principal por la que se metaboliza, por tanto las interacciones mostradas a continuacion serán con cada una de ellas")
                    print()
                return False

            else:
                if len(principales) == 1:
                    if texto:
                        print(f"El principio activo: {ppio} se metaboliza por las enzimas: {enzimas} de las cuales, se ha considerado principal: {principales}, en las siguientes descripciones se mostrarán las interacciones solo con dicha enzima considerada principal")
                        print()
                    return True
                else:
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
    if coincidentes:
        if intro_1 and intro_2:
            if texto:
                print(f"La interacción {ppio_1}-{ppio_2} es considerada Alta")
                print(f"Como ambos principios son metabolizados por enzimas tenidas en cuenta que tienen alguna enzima considerada principal y estas coinciden entre si en las siguientes: {coincidentes} es considerada como interacción alta")
                print()
            return "Alta"
        else:
            if texto:
                print(f"La interacción {ppio_1}-{ppio_2} es considerada Media")
                print(f"Como no sabemos las enzimas principales de por lo menos uno de los dos principios activos pero coinciden en la metabolización de las siguientes enzimas: {coincidentes} su interacción es considerada Media")
                print()
            return "Media"

    else:
        if texto:
            print(f"La interacción {ppio_1}-{ppio_2} es considerada Leve")
            print("Los principios activos no coinciden en ser metabolizados por ninguna enzima de las tenidas en cuenta y por tanto su interacción es categorizada como Leve")
            print()
        return "Leve"




#Falta completar
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

    #Declaramos cuales son las posibilidades
    posibilidades = ["inducer", "substrate", "inhibitor"]
    #Print explicativo
    print(f"En este caso solo se describen las interacciones de los principios activos con la enzima: {enzima} teniendo en cuenta solo que lleven a cabo algunas de las siguientes acciones: {posibilidades}")
    print()
    
    #De las listas proporcionadas con las acciones UNICAS eliminamos las que no tenemos en cuenta:
    mias_1 = [x for x in acc_1 if x in posibilidades]
    mias_2 = [x for x in acc_2 if x in posibilidades]

    #Guardamos una variable con las coincidencias de las acciones (sustrato-sustrato, inhib-inhib, induct-induct)
    #Se supone que ya deben de ser las distintas pero porsiacaso set
    doble = list(set(mias_1) & set(mias_2))

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
            #Mostrar las posibilidades
            if doble:
                #Es posible que doble tenga mas de una acción ¿QUE HACES EN ESE CASO?, con que se tenga una que coincida pues vale supongo
                print(f"doble")
                print()
            #Sustrato
            else:
            
            #Aqui estoy dando prioridad al sustrato y asi??
            #PONER TEXTO GENERAL Y DICCIONARIO
                if "substrate" in acc_1:
                    
                    #sustrato-inductor
                    if "inducer" in acc_2:
                        print(f"Con la enzima: {enzima} el {ppio_1} está actuando como sustrato y {ppio_2} está actuando como inductor, en este caso tendría prevalencia el sustrato")
                        print()
                    #Se supone que con un else deberia valer
                    #sustrato-inhibidor
                    elif "inhibitor" in acc_2:
                        print(f"p1")
                        print()
    
                #Inhibidor
                elif "inhibitor" in acc_1:
                    
                    #inhibidor-indcutor
                    if "inducer" in acc_2:
                        print(f"p2")
                        print()
                    #Se supone que con un else deberia valer
                    #Inhibidor-sustrato
                    elif "substrate" in acc_2:
                        print(f"p3")
                        print()
    
                #Inductor (tambien podría ser solo un else en teoría)
                elif "inducer" in acc_1:
                    
                    #inductor-inhibidor
                    if "inhibitor" in acc_2:
                        print(f"p4")
                        print()
                    #Se supone que con un else deberia valer
                    #inductor-sustrato
                    elif "substrate" in acc_2:
                        print(f"p5")
                        print()





#Y NO SERÍA POSIBLE UN TEXTO GENERICO?? PARA LA ENZIMA E EL PPIO ACTIVO  1  ESTA ACTUANDO COMO: TRADUCCION DE SU ACTUACION Y EL DOS COMO: TRADD, EN ESTE CASO PREVALECERIA: (consulto diccionario con interacción?)

#Y SI UNO TIENE DOS ACCIONES????? CON QUE XUXA ME QUEDO